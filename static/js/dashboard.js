/* RL Arena player dashboard. One common entry point: no domain names are shown.
   - Full-screen run layer with a 3-2-1-GO countdown and a level scan before each question.
   - Read aloud that picks an English voice, can be stopped, and says when a device has no voice.
   - Level map shows only the current batch of ten plus a preview of the next batch.
   - Reminders appear as reminder messages at their time while the page is open.
   - Full-screen congratulations only when a badge is unlocked. Other moments use toasts. */
(() => {
  const cfg = window.COGNI_CONFIG || {};
  const XP_RING = 326.7, TIMER_RING = 100.53, TIMER_CAP = 30;
  const INSTRUCTIONS = "Welcome to RL Arena. Press Start run. A countdown will show, then a question with answer choices. " +
    "Tap the answer you think is right. If you are stuck, tap Hint, or Read aloud to hear the question again. " +
    "When you are finished, press Finish and save.";
  const $ = (id) => document.getElementById(id);
  const show = (el) => el && el.classList.remove("hidden");
  const hide = (el) => el && el.classList.add("hidden");
  const esc = (t) => String(t ?? "").replace(/[&<>"']/g, (c) => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]));
  const RA = () => window.RLArena || {fx: {}, sfx: {}, toast() {}};
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const reduceMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const csrf = () => {
    const m = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : "";
  };
  const request = async (url, options = {}) => {
    const response = await fetch(url, {credentials: "same-origin", ...options,
      headers: {"Content-Type": "application/json", "X-CSRFToken": csrf(), ...(options.headers || {})}});
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || data.detail || "Request failed");
    return data;
  };
  const get = (url) => request(url);

  const state = {sessionId: null, question: null, round: null, usedHint: false, selected: null,
    started: 0, streak: 0, sessionXp: 0, busy: false, starting: false, total: 10};
  let chart = null, timerFrame = null;

  /* ---------- speech (read aloud) ---------- */
  function pickVoice(voices) {
    return voices.find((v) => /^en[-_]IN/i.test(v.lang))
      || voices.find((v) => /^en[-_]GB/i.test(v.lang))
      || voices.find((v) => /^en/i.test(v.lang))
      || null;
  }

  function speak(text) {
    if (!("speechSynthesis" in window) || !("SpeechSynthesisUtterance" in window)) {
      RA().toast("Read aloud is not supported in this browser. Try Chrome, Edge or Safari.", "warn", "🔈");
      return;
    }
    const synth = window.speechSynthesis;
    if (synth.speaking) { synth.cancel(); return; }
    synth.cancel();
    const start = (voices) => {
      const utter = new SpeechSynthesisUtterance(text);
      const voice = pickVoice(voices);
      if (voice) { utter.voice = voice; utter.lang = voice.lang; } else { utter.lang = "en-IN"; }
      utter.rate = 0.9; utter.pitch = 1; utter.volume = 1;
      let started = false;
      utter.onstart = () => { started = true; };
      utter.onerror = (event) => {
        if (event.error !== "interrupted" && event.error !== "canceled") {
          RA().toast("Read aloud could not start on this device.", "warn", "🔈");
        }
      };
      // A short gap after cancel() stops some browsers from silently dropping the next utterance.
      setTimeout(() => {
        synth.speak(utter);
        setTimeout(() => {
          if (!started && !synth.speaking) RA().toast("No English voice was found on this device.", "warn", "🔈");
        }, 2500);
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
        <span class="unlock-kicker">Unlocked</span>
        <div class="unlock-medal" style="--glow:${esc(badge.glow)}"><span>${esc(badge.icon)}</span></div>
        <h2 class="unlock-title">Congratulations!</h2>
        <p class="unlock-name">${esc(badge.name)}</p>
        <p class="muted">${esc(badge.description)}</p>
        <button class="btn btn-neon btn-lg" type="button" id="unlockContinue">Continue</button>`;
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
        if (el) el.textContent = `Level ${levelNumber}`;
        return resolve();
      }
      el.classList.add("scanning");
      let ticks = 0;
      const iv = setInterval(() => {
        el.textContent = `Level ${1 + Math.floor(Math.random() * 200)}`;
        ticks += 1;
        if (ticks >= 14) {
          clearInterval(iv);
          el.textContent = `Level ${levelNumber}`;
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
    if ($("streakChip")) $("streakChip").textContent = `🔥 ${state.streak} streak`;
    if ($("xpChip")) $("xpChip").textContent = `+${state.sessionXp} XP`;
    if ($("roundInfo") && state.round) {
      const label = state.round.phase === "calibration" ? "Warm-up" : "Adaptive";
      $("roundInfo").textContent = `Round ${state.round.number} of ${state.round.total} · ${label}`;
    }
    if ($("questionProgress") && state.round) {
      $("questionProgress").style.width = `${Math.min(100, ((state.round.number - 1) / state.round.total) * 100)}%`;
    }
    const combo = $("combo");
    if (combo) {
      combo.textContent = `🔥 x${state.streak} COMBO`;
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
    $("levelLabel").textContent = `Level ${q.level_number}`;
    const title = $("questionText");
    title.textContent = q.question_text;
    title.classList.remove("q-enter"); void title.offsetWidth; title.classList.add("q-enter");
    $("hintText").textContent = q.hint || "Take your time. Think about the clue.";
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
        state.selected = option;
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
    $("questionText").textContent = "Getting your first question…";
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
      RA().toast(`Could not start: ${error.message}`, "warn", "⚠️");
    } finally {
      state.starting = false;
    }
  }

  function floatAt(el, text, colour) {
    const rect = el.getBoundingClientRect();
    RA().fx.floatText && RA().fx.floatText(text, rect.left + rect.width / 2 - 30, rect.top, colour);
  }

  async function submitAnswer(button) {
    if (state.busy || !state.selected || !state.question || !state.sessionId) return;
    state.busy = true;
    stopTimer();
    const buttons = [...$("answerOptions").querySelectorAll("button")];
    buttons.forEach((b) => { b.disabled = true; });
    try {
      const data = await request(cfg.answerUrl, {
        method: "POST",
        body: JSON.stringify({
          session_id: state.sessionId, question_id: state.question.id, answer: state.selected,
          used_hint: state.usedHint, response_seconds: (Date.now() - state.started) / 1000,
        }),
      });
      state.streak = data.streak;
      state.sessionXp += data.xp_gained;
      buttons.forEach((b) => {
        if (b.textContent === data.correct_answer) b.classList.add("correct");
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
        floatAt(button, "Not quite", "#ff5ec8");
      }

      $("gameFeedback").textContent = `${data.feedback} Score ${data.score_percent}% · +${data.xp_gained} XP`;
      updateChips();
      if (data.cleared_now) {
        RA().sfx.levelup && RA().sfx.levelup();
        RA().fx.confetti && RA().fx.confetti();
        RA().toast(`Level ${state.question.level_number} cleared! Higher levels are opening.`, "good", "🏁");
      }
      if (data.round_complete) {
        $("questionText").textContent = "Run complete. Wonderful effort ✨";
        $("answerOptions").innerHTML = "";
        $("gameFeedback").textContent += " Press Finish & save to bank your XP.";
        $("questionProgress").style.width = "100%";
        return;
      }
      $("adaptationText").textContent = data.adaptation_reason;
      $("confidenceText").textContent = data.predicted_success != null
        ? `Predicted success for the next level: ${Math.round(data.predicted_success * 100)}%` : "";
      state.round = data.round;
      await sleep(850);
      if (data.next_question) {
        await scanReveal(data.next_question.level_number);
        renderQuestion(data.next_question);
      } else {
        $("answerOptions").innerHTML = "";
        $("questionText").textContent = "No more levels available right now.";
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
        toast: `Run saved · +${data.xp_gained} XP`,
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
    if (pending.perfect) RA().toast("Flawless run! Bonus XP earned.", "good", "💎");
    if (pending.levelUp) {
      RA().sfx.levelup && RA().sfx.levelup();
      RA().fx.confetti && RA().fx.confetti();
      RA().toast(`You reached level ${pending.levelUp}!`, "good", "🚀");
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

  function sentKey(id, day) { return `rlSms:${id}:${day}`; }
  function alreadyShown(id, day) {
    try { return localStorage.getItem(sentKey(id, day)) === "1"; } catch (_) { return false; }
  }
  function markShown(id, day) {
    try { localStorage.setItem(sentKey(id, day), "1"); } catch (_) { /* storage unavailable */ }
  }

  function smsBubble(reminder, timeLabel) {
    const stack = $("smsStack");
    if (!stack) return;
    const bubble = document.createElement("div");
    bubble.className = "sms-bubble";
    bubble.innerHTML = `
      <div class="sms-head"><span class="sms-avatar">✦</span><b>CogniCare</b><small>${esc(timeLabel)}</small></div>
      <p>Reminder: <b>${esc(reminder.title)}</b>${reminder.notes ? ` <span>${esc(reminder.notes)}</span>` : ""}</p>
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
      smsBubble(r, hhmm);
    });
  }

  /* ---------- panels ---------- */
  const LABELS = {cleared: "cleared", open: "unlocked", locked: "locked"};

  async function loadLevels() {
    try {
      const data = await get(cfg.levelsUrl);
      const batch = data.batch;
      $("nextUnlock").textContent = data.next_unlock
        ? `Your next level to unlock is ${data.next_unlock.level_number}. It needs skill ${data.next_unlock.required_skill}; you are at ${data.next_unlock.current_skill}.`
        : "Every level is unlocked. Keep training to clear them all.";
      $("batchPill").textContent = `Batch ${batch.number} · levels ${batch.start}–${batch.end}`;
      $("batchGrid").innerHTML = batch.levels.map((lv, i) => `
        <span class="lvl ${lv.state}" style="animation-delay:${i * 40}ms"
          title="Level ${lv.level_number}: ${LABELS[lv.state]}">${lv.level_number}</span>`).join("");
      $("batchNext").innerHTML = batch.next
        ? `<b>Next batch ${batch.next.number}</b> · levels ${batch.next.start}–${batch.next.end}. These open as your skill grows.`
        : `<b>You have reached the last batch.</b> All 200 levels are in the arena.`;
    } catch (error) { console.warn("Levels unavailable", error); }
  }

  async function loadProgress() {
    try {
      const data = await get(cfg.progressUrl);
      const level = data.level;
      requestAnimationFrame(() => { $("xpRing").style.strokeDashoffset = String(XP_RING * (1 - level.percent / 100)); });
      $("levelBadge").textContent = `LV ${level.level}`;
      $("xpText").textContent = `${level.into_level} / ${level.needed} XP`;
      $("badgeCount").textContent = `${data.earned_count} / ${data.total_badges}`;
      $("badgePill").textContent = `${data.earned_count} unlocked`;
      $("bestStreak").textContent = data.stats.streak;
      $("skillScore").textContent = Math.round(data.skill.score);
      requestAnimationFrame(() => requestAnimationFrame(() => {
        $("skillFill").style.width = `${Math.min(100, Math.round(data.skill.score))}%`;
      }));
      $("badgeGrid").innerHTML = data.badges.map((b, i) => `
        <div class="badge-card ${b.earned ? "earned" : "locked"}" style="--glow:${esc(b.glow)};animation-delay:${i * 40}ms" title="${esc(b.description)}">
          <span class="badge-icon">${esc(b.icon)}</span>
          <b>${esc(b.name)}</b>
          <small>${b.earned ? `Earned ${esc(b.earned_at)}` : `${b.progress} / ${b.threshold}`}</small>
        </div>`).join("");
    } catch (error) { console.warn("Progress unavailable", error); }
  }

  async function loadLeaderboard() {
    try {
      const data = await get(cfg.leaderboardUrl);
      $("myRankPill").textContent = data.my_rank ? `You're #${data.my_rank}` : "Unranked";
      if (!data.entries.length) { $("leaderboard").innerHTML = '<li class="muted">Standings appear after the first run.</li>'; return; }
      $("leaderboard").innerHTML = data.entries.map((e, i) => {
        let arrow = '<span class="arrow same">–</span>';
        if (e.change === null) arrow = '<span class="arrow new">NEW</span>';
        else if (e.change > 0) arrow = `<span class="arrow up">▲ ${e.change}</span>`;
        else if (e.change < 0) arrow = `<span class="arrow down">▼ ${Math.abs(e.change)}</span>`;
        return `<li class="lb-row ${e.is_me ? "is-me" : ""}" style="animation-delay:${i * 70}ms">
          <span class="rank">${e.rank}</span>
          <span class="lb-name">${esc(e.name)}${e.is_me ? " <em>you</em>" : ""}<small>LV ${e.level} · ${e.sessions} runs</small></span>
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
  $("hearInstructions")?.addEventListener("click", () => speak(INSTRUCTIONS));
  $("hintButton")?.addEventListener("click", () => { if (state.question) { state.usedHint = true; show($("hintText")); } });
  $("readQuestion")?.addEventListener("click", () => {
    if (!state.question) { RA().toast("Start a run first, then the question can be read aloud.", "info", "🔊"); return; }
    const choices = (state.question.options || []).join(", ");
    speak(`${state.question.question_text}. The choices are: ${choices}.`);
  });
  $("finishGame")?.addEventListener("click", finishRun);
  $("quitGame")?.addEventListener("click", () => {
    if (state.sessionId && !window.confirm("Leave this run? Answers so far are saved only when you press Finish.")) return;
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
    } catch (error) { RA().toast(`Could not add reminder: ${error.message}`, "warn", "⚠️"); }
  });

  loadLevels();
  loadProgress();
  loadLeaderboard();
  loadAnalytics();
  showPending();
  checkReminders();
  setInterval(checkReminders, 20000);
})();
