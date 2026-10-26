/* RL Arena player dashboard.
   - All visible text comes from the translations sent by the server (window.RL_I18N).
   - Full-screen run layer with a 3-2-1-GO countdown and a level scan before each question.
   - Read aloud uses a voice for the chosen language. If the device has no voice for it, it says so.
   - Level map shows only the current batch of ten plus a preview of the next batch.
   - Reminder messages appear at their time while the page is open.
   - Full-screen congratulations only when a badge is unlocked. Other moments use toasts. */
(() => {
  const cfg = window.RL_CONFIG || {};
  const I18N = window.RL_I18N || {strings: {}, speech: "en-IN"};
  const XP_RING = 326.7, TIMER_RING = 100.53, TIMER_CAP = 30;
  const T = (key, vars = {}) => {
    let s = (I18N.strings && I18N.strings[key]) || key;
    Object.entries(vars).forEach(([name, value]) => { s = s.split("{" + name + "}").join(String(value)); });
    return s;
  };
  const $ = (id) => document.getElementById(id);
  const show = (el) => el && el.classList.remove("hidden");
  const hide = (el) => el && el.classList.add("hidden");
  const esc = (t) => String(t ?? "").replace(/[&<>"']/g, (c) => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]));
  const RA = () => window.RLArena || {fx: {}, sfx: {}, toast() {}};
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const reduceMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const csrf = () => {
    const formToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
    if (formToken) return formToken;
    const m = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : "";
  };
  const request = async (url, options = {}) => {
    const method = (options.method || "GET").toUpperCase();
    const csrfToken = csrf();
    if (!["GET", "HEAD", "OPTIONS", "TRACE"].includes(method) && !csrfToken) {
      throw new Error("CSRF token is missing. Reload the page and try again.");
    }
    const response = await fetch(url, {credentials: "same-origin", ...options,
      headers: {"Content-Type": "application/json", "X-CSRFToken": csrfToken, ...(options.headers || {})}});
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || data.detail || "Request failed");
    return data;
  };
  const get = (url) => request(url);

  const state = {sessionId: null, question: null, round: null, usedHint: false, selected: null,
    started: 0, streak: 0, sessionXp: 0, busy: false, starting: false, total: 10};
  let chart = null, timerFrame = null;

  /* ---------- speech (read aloud) ---------- */
  const SPEECH = I18N.speech || "en-IN";
  const SPEECH_PREFIX = SPEECH.split("-")[0].toLowerCase();

  function pickVoice(voices) {
    const exact = voices.find((v) => v.lang.replace("_", "-").toLowerCase() === SPEECH.toLowerCase());
    return exact || voices.find((v) => v.lang.replace("_", "-").toLowerCase().startsWith(SPEECH_PREFIX + "-")) || null;
  }

  function speak(text) {
    if (!("speechSynthesis" in window) || !("SpeechSynthesisUtterance" in window)) {
      RA().toast(T("tts_unsupported"), "warn", "🔈");
      return;
    }
    const synth = window.speechSynthesis;
    if (synth.speaking) { synth.cancel(); return; }
    synth.cancel();
    const start = (voices) => {
      const voice = pickVoice(voices);
      if (!voice) {
        RA().toast(T("tts_no_voice"), "warn", "🔈");
        return;
      }
      const utter = new SpeechSynthesisUtterance(text);
      utter.voice = voice;
      utter.lang = voice.lang;
      utter.rate = 0.9; utter.pitch = 1; utter.volume = 1;
      let started = false;
      utter.onstart = () => { started = true; };
      utter.onerror = (event) => {
        if (event.error !== "interrupted" && event.error !== "canceled") RA().toast(T("tts_failed"), "warn", "🔈");
      };
      // A short gap after cancel() stops some browsers from silently dropping the next utterance.
      setTimeout(() => {
        synth.speak(utter);
        setTimeout(() => { if (!started && !synth.speaking) RA().toast(T("tts_failed"), "warn", "🔈"); }, 2500);
      }, 80);
    };
    const voices = synth.getVoices();
    if (voices.length) { start(voices); return; }
    // Voices load asynchronously in many browsers: wait briefly for them.
    let done = false;
    const once = () => { if (!done) { done = true; start(synth.getVoices()); } };
    synth.addEventListener("voiceschanged", once, {once: true});
    setTimeout(once, 700);
  }

  /* ---------- full-screen run layer ---------- */
  function openLayer() {
    show($("gameLayer"));
    document.body.classList.add("run-open");
    $("gameLayer").scrollTop = 0;
  }
  function closeLayer() {
    hide($("gameLayer"));
    document.body.classList.remove("run-open");
  }

  /* ---------- overlays: full-screen badge unlock only ---------- */
  function badgeOverlay(badge) {
    return new Promise((resolve) => {
      const box = $("overlay"), card = $("overlayCard");
      if (!box || !card) return resolve();
      card.innerHTML = `
        <span class="unlock-kicker">${esc(T("unlocked"))}</span>
        <div class="unlock-medal" style="--glow:${esc(badge.glow)}"><span>${esc(badge.icon)}</span></div>
        <h2 class="unlock-title">${esc(T("congratulations"))}</h2>
        <p class="unlock-name">${esc(badge.name)}</p>
        <p class="muted">${esc(badge.description)}</p>
        <button class="btn btn-neon btn-lg" type="button" id="unlockContinue">${esc(T("continue_btn"))}</button>`;
      box.classList.add("unlock");
      box.classList.remove("hidden");
      requestAnimationFrame(() => box.classList.add("open"));
      let closed = false;
      const close = () => {
        if (closed) return;
        closed = true;
        box.classList.remove("open");
        setTimeout(() => { box.classList.add("hidden"); box.classList.remove("unlock"); resolve(); }, 260);
      };
      box.addEventListener("click", close, {once: true});
    });
  }

  /* ---------- timer ring ---------- */
  function startTimer() {
    cancelAnimationFrame(timerFrame);
    const tick = () => {
      const t = (Date.now() - state.started) / 1000;
      $("timerText").textContent = `${t.toFixed(1)}s`;
      $("timerRing").style.strokeDashoffset = String(TIMER_RING * (1 - Math.min(1, t / TIMER_CAP)));
      timerFrame = requestAnimationFrame(tick);
    };
    tick();
  }
  function stopTimer() { cancelAnimationFrame(timerFrame); }

  /* ---------- the engine's pick: a short scan that locks onto the chosen level ---------- */
  function scanReveal(levelNumber) {
    return new Promise((resolve) => {
      const el = $("levelLabel");
      if (!el || reduceMotion()) {
        if (el) el.textContent = T("level_label", {n: levelNumber});
        return resolve();
      }
      el.classList.add("scanning");
      let ticks = 0;
      const iv = setInterval(() => {
        el.textContent = T("level_label", {n: 1 + Math.floor(Math.random() * (I18N.total || 500))});
        ticks += 1;
        if (ticks >= 14) {
          clearInterval(iv);
          el.textContent = T("level_label", {n: levelNumber});
          el.classList.remove("scanning");
          el.classList.add("lock-in");
          setTimeout(() => el.classList.remove("lock-in"), 600);
          resolve();
        }
      }, 42);
    });
  }

  /* ---------- run flow ---------- */
  function updateChips() {
    if ($("streakChip")) $("streakChip").textContent = T("streak_label", {n: state.streak});
    if ($("xpChip")) $("xpChip").textContent = T("xp_label", {n: state.sessionXp});
    if ($("roundInfo") && state.round) {
      const phase = state.round.phase === "calibration" ? T("phase_warmup") : T("phase_adaptive");
      $("roundInfo").textContent = T("round_label", {number: state.round.number, total: state.round.total, phase});
    }
    if ($("questionProgress") && state.round) {
      $("questionProgress").style.width = `${Math.min(100, ((state.round.number - 1) / state.round.total) * 100)}%`;
    }
    const combo = $("combo");
    if (combo) {
      combo.textContent = `🔥 x${state.streak}`;
      combo.classList.toggle("hidden", state.streak < 3);
      combo.classList.remove("pulse"); void combo.offsetWidth;
      if (state.streak >= 3) combo.classList.add("pulse");
    }
  }

  function renderQuestion(q) {
    if (!q) return;
    state.question = q;
    state.selected = null;
    state.usedHint = false;
    state.started = Date.now();
    $("levelLabel").textContent = T("level_label", {n: q.level_number});
    const title = $("questionText");
    title.textContent = q.question_text;
    title.classList.remove("q-enter"); void title.offsetWidth; title.classList.add("q-enter");
    $("hintText").textContent = q.hint || T("hint_default");
    hide($("hintText"));
    $("gameFeedback").textContent = "";
    updateChips();

    const wrap = $("answerOptions");
    wrap.innerHTML = "";
    (q.options || []).forEach((option, i) => {
      const button = document.createElement("button");
      button.className = "answer-option";
      button.type = "button";
      button.style.animationDelay = `${i * 90}ms`;
      button.textContent = option;
      button.addEventListener("click", () => {
        if (state.busy) return;
        RA().sfx.click && RA().sfx.click();
        wrap.querySelectorAll("button").forEach((item) => item.classList.remove("selected"));
        button.classList.add("selected");
        state.selected = i;
        submitAnswer(button);
      });
      wrap.appendChild(button);
    });
    startTimer();
  }

  async function countdown() {
    const node = $("countdown");
    if (!node) return;
    show(node);
    for (const label of ["3", "2", "1", "GO"]) {
      node.textContent = label;
      node.classList.remove("tick"); void node.offsetWidth; node.classList.add("tick");
      if (label === "GO") RA().sfx.go && RA().sfx.go(); else RA().sfx.tick && RA().sfx.tick();
      await sleep(label === "GO" ? 450 : 620);
    }
    hide(node);
  }

  async function startRun() {
    if (state.sessionId || state.starting) return;
    state.starting = true;
    openLayer();
    $("questionText").textContent = T("getting_question");
    $("answerOptions").innerHTML = "";
    const startRequest = request(cfg.startUrl, {method: "POST", body: JSON.stringify({})});
    startRequest.catch(() => {});
    try {
      await countdown();
      const data = await startRequest;
      state.sessionId = data.session_id;
      state.round = data.round;
      state.total = data.round.total;
      state.streak = 0;
      state.sessionXp = 0;
      state.busy = false;
      $("adaptationText").textContent = data.reason;
      $("confidenceText").textContent = "";
      if (data.question) await scanReveal(data.question.level_number);
      renderQuestion(data.question);
    } catch (error) {
      closeLayer();
      RA().toast(T("could_not_start", {error: error.message}), "warn", "⚠️");
    } finally {
      state.starting = false;
    }
  }

  function floatAt(el, text, colour) {
    const rect = el.getBoundingClientRect();
    RA().fx.floatText && RA().fx.floatText(text, rect.left + rect.width / 2 - 30, rect.top, colour);
  }

  async function submitAnswer(button) {
    if (state.busy || state.selected === null || !state.question || !state.sessionId) return;
    state.busy = true;
    stopTimer();
    const buttons = [...$("answerOptions").querySelectorAll("button")];
    buttons.forEach((b) => { b.disabled = true; });
    try {
      const data = await request(cfg.answerUrl, {
        method: "POST",
        body: JSON.stringify({
          session_id: state.sessionId, question_id: state.question.id, answer_index: state.selected,
          used_hint: state.usedHint, response_seconds: (Date.now() - state.started) / 1000,
        }),
      });
      state.streak = data.streak;
      state.sessionXp += data.xp_gained;
      buttons.forEach((b, i) => {
        if (i === data.correct_index) b.classList.add("correct");
        else if (b.classList.contains("selected") && !data.correct) b.classList.add("wrong");
      });

      if (data.correct) {
        button.classList.add("pop");
        const rect = button.getBoundingClientRect();
        RA().fx.burst && RA().fx.burst(rect.left + rect.width / 2, rect.top + rect.height / 2, 46);
        RA().sfx.correct && RA().sfx.correct();
        RA().fx.flash && RA().fx.flash("good");
        floatAt(button, `+${data.xp_gained} XP`, "#5ef2b0");
      } else {
        RA().sfx.wrong && RA().sfx.wrong();
        RA().fx.shake && RA().fx.shake($("gameLayer"));
        RA().fx.flash && RA().fx.flash("bad");
        floatAt(button, T("not_quite"), "#ff5ec8");
      }

      const feedback = data.correct ? T("feedback_correct") : T("feedback_wrong");
      $("gameFeedback").textContent = `${feedback} ${T("score_line", {pct: data.score_percent, xp: data.xp_gained})}`;
      updateChips();
      if (data.cleared_now) {
        RA().sfx.levelup && RA().sfx.levelup();
        RA().fx.confetti && RA().fx.confetti();
        RA().toast(T("level_cleared_toast", {n: state.question.level_number}), "good", "🏁");
      }
      if (data.round_complete) {
        $("questionText").textContent = T("run_complete");
        $("answerOptions").innerHTML = "";
        $("gameFeedback").textContent += " " + T("press_finish");
        $("questionProgress").style.width = "100%";
        return;
      }
      $("adaptationText").textContent = data.adaptation_reason;
      $("confidenceText").textContent = data.predicted_success != null
        ? T("predicted", {pct: Math.round(data.predicted_success * 100)}) : "";
      state.round = data.round;
      await sleep(850);
      if (data.next_question) {
        await scanReveal(data.next_question.level_number);
        renderQuestion(data.next_question);
      } else {
        $("answerOptions").innerHTML = "";
        $("questionText").textContent = T("no_more_levels");
      }
    } catch (error) {
      $("gameFeedback").textContent = error.message;
      buttons.forEach((b) => { b.disabled = false; });
      startTimer();
    } finally {
      state.busy = false;
    }
  }

  async function finishRun() {
    if (!state.sessionId) { closeLayer(); return; }
    try {
      const data = await request(cfg.finishUrl, {method: "POST", body: JSON.stringify({session_id: state.sessionId})});
      const pending = {
        toast: T("run_saved", {xp: data.xp_gained}),
        perfect: !!data.perfect,
        levelUp: data.level_up ? data.level : null,
        badges: data.new_badges || [],
      };
      try { sessionStorage.setItem("rlArenaPending", JSON.stringify(pending)); } catch (_) { /* private mode */ }
      state.sessionId = null;
      window.location.reload();
    } catch (error) {
      $("gameFeedback").textContent = error.message;
    }
  }

  async function showPending() {
    let pending = null;
    try {
      pending = JSON.parse(sessionStorage.getItem("rlArenaPending") || "null");
      sessionStorage.removeItem("rlArenaPending");
    } catch (_) { return; }
    if (!pending) return;
    await sleep(400);
    RA().toast(pending.toast, "good", "✦");
    if (pending.perfect) RA().toast(T("flawless"), "good", "💎");
    if (pending.levelUp) {
      RA().sfx.levelup && RA().sfx.levelup();
      RA().fx.confetti && RA().fx.confetti();
      RA().toast(T("reached_level", {n: pending.levelUp}), "good", "🚀");
    }
    // Badges are the only thing that takes over the whole screen.
    for (const badge of pending.badges) {
      RA().sfx.badge && RA().sfx.badge();
      RA().fx.confetti && RA().fx.confetti();
      await badgeOverlay(badge);
    }
  }

  /* ---------- reminder messages ---------- */
  const reminders = (() => {
    try { return JSON.parse(document.getElementById("reminderData")?.textContent || "[]"); }
    catch (_) { return []; }
  })();

  function sentKey(id, day) { return `rlReminder:${id}:${day}`; }
  function alreadyShown(id, day) {
    try { return localStorage.getItem(sentKey(id, day)) === "1"; } catch (_) { return false; }
  }
  function markShown(id, day) {
    try { localStorage.setItem(sentKey(id, day), "1"); } catch (_) { /* storage unavailable */ }
  }

  function reminderBubble(reminder, timeLabel) {
    const stack = $("smsStack");
    if (!stack) return;
    const bubble = document.createElement("div");
    bubble.className = "sms-bubble";
    bubble.innerHTML = `
      <div class="sms-head"><span class="sms-avatar">✦</span><b>RL Arena</b><small>${esc(timeLabel)}</small></div>
      <p>${esc(T("reminder_prefix"))} <b>${esc(reminder.title)}</b>${reminder.notes ? ` <span>${esc(reminder.notes)}</span>` : ""}</p>
      <span class="sms-time">${esc(timeLabel)}</span>`;
    bubble.addEventListener("click", () => bubble.remove());
    stack.appendChild(bubble);
    if (navigator.vibrate) { try { navigator.vibrate([120, 80, 120]); } catch (_) { /* not supported */ } }
    RA().sfx.tick && RA().sfx.tick();
    setTimeout(() => {
      bubble.classList.add("sms-out");
      setTimeout(() => bubble.remove(), 400);
    }, 12000);
  }

  function checkReminders() {
    const now = new Date();
    const hhmm = `${String(now.getHours()).padStart(2, "0")}:${String(now.getMinutes()).padStart(2, "0")}`;
    const day = now.toISOString().slice(0, 10);
    reminders.forEach((r) => {
      if (!r.time || r.time !== hhmm || alreadyShown(r.id, day)) return;
      markShown(r.id, day);
      reminderBubble(r, hhmm);
    });
  }

  /* ---------- panels ---------- */
  async function loadLevels() {
    try {
      const data = await get(cfg.levelsUrl);
      const batch = data.batch;
      $("nextUnlock").textContent = data.next_unlock
        ? T("next_unlock", {level: data.next_unlock.level_number, required: data.next_unlock.required_skill, current: data.next_unlock.current_skill})
        : T("all_unlocked");
      $("batchPill").textContent = T("batch_pill", {number: batch.number, start: batch.start, end: batch.end});
      $("batchGrid").innerHTML = batch.levels.map((lv, i) => `
        <span class="lvl ${lv.state}" style="animation-delay:${i * 40}ms"
          title="${esc(T("level_label", {n: lv.level_number}))}: ${esc(T("state_" + lv.state))}">${lv.level_number}</span>`).join("");
      $("batchNext").innerHTML = batch.next
        ? T("next_batch", {number: batch.next.number, start: batch.next.start, end: batch.next.end})
        : T("last_batch", {total: I18N.total || 500});
    } catch (error) { console.warn("Levels unavailable", error); }
  }

  async function loadProgress() {
    try {
      const data = await get(cfg.progressUrl);
      const level = data.level;
      requestAnimationFrame(() => { $("xpRing").style.strokeDashoffset = String(XP_RING * (1 - level.percent / 100)); });
      $("levelBadge").textContent = T("level_badge", {n: level.level});
      $("xpText").textContent = T("xp_to_next", {xp: level.into_level, needed: level.needed, next: level.level + 1});
      $("badgeCount").textContent = `${data.earned_count} / ${data.total_badges}`;
      $("badgePill").textContent = T("unlocked_count", {count: data.earned_count});
      $("bestStreak").textContent = data.stats.streak;
      $("skillScore").textContent = Math.round(data.skill.score);
      requestAnimationFrame(() => requestAnimationFrame(() => {
        $("skillFill").style.width = `${Math.min(100, Math.round(data.skill.score))}%`;
      }));
      $("badgeGrid").innerHTML = data.badges.map((b, i) => `
        <div class="badge-card ${b.earned ? "earned" : "locked"}" style="--glow:${esc(b.glow)};animation-delay:${i * 40}ms" title="${esc(b.description)}">
          <span class="badge-icon">${esc(b.icon)}</span>
          <b>${esc(b.name)}</b>
          <small>${b.earned ? esc(T("earned_on", {date: b.earned_at})) : `${b.progress} / ${b.threshold}`}</small>
        </div>`).join("");
    } catch (error) { console.warn("Progress unavailable", error); }
  }

  async function loadLeaderboard() {
    try {
      const data = await get(cfg.leaderboardUrl);
      $("myRankPill").textContent = data.my_rank ? T("your_rank", {rank: data.my_rank}) : T("unranked");
      if (!data.entries.length) { $("leaderboard").innerHTML = `<li class="muted">${esc(T("standings_empty"))}</li>`; return; }
      $("leaderboard").innerHTML = data.entries.map((e, i) => {
        let arrow = '<span class="arrow same">–</span>';
        if (e.change === null) arrow = '<span class="arrow new">NEW</span>';
        else if (e.change > 0) arrow = `<span class="arrow up">▲ ${e.change}</span>`;
        else if (e.change < 0) arrow = `<span class="arrow down">▼ ${Math.abs(e.change)}</span>`;
        return `<li class="lb-row ${e.is_me ? "is-me" : ""}" style="animation-delay:${i * 70}ms">
          <span class="rank">${e.rank}</span>
          <span class="lb-name">${esc(e.name)}${e.is_me ? ` <em>${esc(T("you"))}</em>` : ""}<small>${esc(T("level_badge", {n: e.level}))} · ${e.sessions} ${esc(T("runs_short"))}</small></span>
          ${arrow}<span class="lb-xp">${e.total_xp} XP</span></li>`;
      }).join("");
    } catch (error) { console.warn("Leaderboard unavailable", error); }
  }

  async function loadAnalytics() {
    try {
      const data = await get(cfg.analyticsUrl);
      $("averageScore").dataset.count = data.average_score; $("averageScore").dataset.suffix = "%";
      $("totalSessions").dataset.count = data.total_sessions;
      document.querySelectorAll(".count").forEach((el) => RA().fx.countUp && RA().fx.countUp(el));
      const canvas = $("progressChart");
      if (!canvas || !window.Chart) return;
      if (chart) chart.destroy();
      chart = new Chart(canvas, {
        type: "line",
        data: {labels: data.sessions.map((s) => s.date), datasets: [{label: "Score (%)", data: data.sessions.map((s) => s.score),
          borderColor: "#5ec8ff", backgroundColor: "rgba(94,200,255,.12)", fill: true, tension: .38, pointRadius: 4, pointBackgroundColor: "#ff5ec8"}]},
        options: {responsive: true, maintainAspectRatio: false, animation: {duration: 1000},
          scales: {y: {min: 0, max: 100, ticks: {stepSize: 25, color: "#9aa6d6"}, grid: {color: "rgba(255,255,255,.06)"}},
            x: {ticks: {color: "#9aa6d6"}, grid: {display: false}}}, plugins: {legend: {display: false}}},
      });
    } catch (error) { console.warn("Analytics unavailable", error); }
  }

  /* ---------- wiring ---------- */
  $("startRun")?.addEventListener("click", startRun);
  $("hearInstructions")?.addEventListener("click", () => speak(T("instructions")));
  $("hintButton")?.addEventListener("click", () => { if (state.question) { state.usedHint = true; show($("hintText")); } });
  $("readQuestion")?.addEventListener("click", () => {
    if (!state.question) { RA().toast(T("start_run_first"), "info", "🔊"); return; }
    const choices = (state.question.options || []).join(", ");
    speak(T("read_question_prefix", {question: state.question.question_text, choices}));
  });
  $("finishGame")?.addEventListener("click", finishRun);
  $("quitGame")?.addEventListener("click", () => {
    if (state.sessionId && !window.confirm(T("leave_confirm"))) return;
    stopTimer(); state.sessionId = null; closeLayer(); window.location.reload();
  });
  $("reminderForm")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const title = $("reminderTitle").value.trim();
    const time = $("reminderTime").value;
    if (!title || !time) return;
    try {
      await request(cfg.remindersUrl, {method: "POST", body: JSON.stringify({
        title, reminder_type: $("reminderType").value, reminder_time: time, notes: "",
      })});
      window.location.reload();
    } catch (error) { RA().toast(T("could_not_add_reminder", {error: error.message}), "warn", "⚠️"); }
  });

  loadLevels();
  loadProgress();
  loadLeaderboard();
  loadAnalytics();
  showPending();
  checkReminders();
  setInterval(checkReminders, 20000);
})();
