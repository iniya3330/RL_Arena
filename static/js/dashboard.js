(() => {
  const cfg = window.COGNI_CONFIG || {};
  const csrf = () => {
    const match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : "";
  };
  const request = async (url, options = {}) => {
    const response = await fetch(url, {
      credentials: "same-origin",
      headers: {"Content-Type": "application/json", "X-CSRFToken": csrf(), ...(options.headers || {})},
      ...options
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || "Request failed");
    return data;
  };

  let sessionId = null, currentQuestion = null, questionNo = 0;
  let usedHint = false, selectedAnswer = null, questionStart = 0, chart = null;

  const $ = (id) => document.getElementById(id);
  const gameBox = $("gameBox"), photoBox = $("photoBox");
  const show = (el) => el?.classList.remove("hidden");
  const hide = (el) => el?.classList.add("hidden");

  const speak = (text) => {
    if (!("speechSynthesis" in window)) {
      alert("Voice assistance is not supported by this browser.");
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-IN";
    utterance.rate = 0.88;
    window.speechSynthesis.speak(utterance);
  };

  function updateProgress() {
    const progress = Math.min(100, Math.round((questionNo / 7) * 100));
    if ($("questionProgress")) $("questionProgress").style.width = `${progress}%`;
    if ($("questionCount")) $("questionCount").textContent = `Question ${questionNo} of 7`;
  }

  function renderQuestion(q) {
    if (!q) return;
    currentQuestion = q;
    selectedAnswer = null;
    usedHint = false;
    questionStart = Date.now();

    $("domainPill").textContent = (q.domain || "memory").toUpperCase();
    $("questionText").textContent = q.question_text;
    $("hintText").textContent = q.hint || "Take your time. Think about the clue.";
    hide($("hintText"));
    $("gameFeedback").textContent = "";
    updateProgress();

    const wrap = $("answerOptions");
    wrap.innerHTML = "";
    (q.options || []).forEach((option) => {
      const button = document.createElement("button");
      button.className = "answer-option";
      button.textContent = option;
      button.type = "button";
      button.addEventListener("click", () => {
        wrap.querySelectorAll("button").forEach((item) => item.classList.remove("selected"));
        button.classList.add("selected");
        selectedAnswer = option;
        submitAnswer();
      });
      wrap.appendChild(button);
    });
  }

  async function startGame() {
    try {
      const data = await request(cfg.startUrl, {method: "POST", body: JSON.stringify({})});
      sessionId = data.session_id;
      questionNo = 1;
      show(gameBox); hide(photoBox);
      renderQuestion(data.question);
      gameBox.scrollIntoView({behavior: "smooth", block: "nearest"});
    } catch (error) {
      alert(error.message + "\nPlease sign in again.");
    }
  }

  async function submitAnswer() {
    if (!selectedAnswer || !currentQuestion || !sessionId) return;

    const buttons = $("answerOptions").querySelectorAll("button");
    buttons.forEach((button) => button.disabled = true);

    try {
      const data = await request(cfg.answerUrl, {
        method: "POST",
        body: JSON.stringify({
          session_id: sessionId,
          question_id: currentQuestion.id,
          answer: selectedAnswer,
          used_hint: usedHint,
          response_seconds: (Date.now() - questionStart) / 1000
        })
      });

      $("gameFeedback").textContent =
        `${data.feedback} Current score: ${data.score_percent}%.`;
      if ($("adaptationText")) {
        $("adaptationText").textContent =
          data.adaptation_reason || "The next activity is selected from recent engagement.";
      }

      if (questionNo >= 7) {
        $("questionText").textContent = "Wonderful effort! Your 7-question mission is complete. ✨";
        $("answerOptions").innerHTML = "";
        $("gameFeedback").textContent += " Press Finish & save to keep your result.";
        if ($("questionProgress")) $("questionProgress").style.width = "100%";
        return;
      }

      if (data.next_question) {
        window.setTimeout(() => {
          questionNo += 1;
          renderQuestion(data.next_question);
        }, 850);
      } else {
        $("questionText").textContent = "Wonderful effort! You completed the available activities.";
        $("answerOptions").innerHTML = "";
      }
    } catch (error) {
      $("gameFeedback").textContent = error.message;
      buttons.forEach((button) => button.disabled = false);
    }
  }

  $("startGame")?.addEventListener("click", startGame);

  $("hintButton")?.addEventListener("click", () => {
    usedHint = true;
    show($("hintText"));
  });

  $("readQuestion")?.addEventListener("click", () => {
    if (currentQuestion) speak(currentQuestion.question_text);
  });

  $("voiceHelp")?.addEventListener("click", () => {
    speak("Welcome to CogniCare. Choose Memory and Thinking to begin a short activity. Take your time. You can ask for a hint whenever you need one.");
  });

  $("finishGame")?.addEventListener("click", async () => {
    if (!sessionId) {
      hide(gameBox);
      return;
    }
    try {
      const data = await request(cfg.finishUrl, {
        method: "POST",
        body: JSON.stringify({session_id: sessionId})
      });
      $("gameFeedback").textContent =
        `Session saved. Final score: ${data.score_percent}%. Great work!`;
      sessionId = null;
      window.setTimeout(() => {
        hide(gameBox);
        loadAnalytics();
        window.location.reload();
      }, 900);
    } catch (error) {
      $("gameFeedback").textContent = error.message;
    }
  });

  $("photoGame")?.addEventListener("click", () => {
    hide(gameBox); show(photoBox);
    photoBox.scrollIntoView({behavior: "smooth", block: "nearest"});
  });

  $("closePhoto")?.addEventListener("click", () => hide(photoBox));

  $("photoInput")?.addEventListener("change", (event) => {
    const file = event.target.files && event.target.files[0];
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      alert("Please choose an image file.");
      return;
    }
    $("photoPreview").src = URL.createObjectURL(file);
    show($("photoPreview"));
  });

  $("reminderForm")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const title = $("reminderTitle").value.trim();
    if (!title) return;
    try {
      await request(cfg.remindersUrl, {
        method: "POST",
        body: JSON.stringify({
          title,
          reminder_type: $("reminderType").value,
          notes: "Added from dashboard"
        })
      });
      window.location.reload();
    } catch (error) {
      alert("Could not add reminder: " + error.message);
    }
  });

  async function loadAnalytics() {
    try {
      const data = await request(cfg.analyticsUrl);
      $("averageScore").textContent = data.average_score + "%";
      $("totalSessions").textContent = data.total_sessions;

      const canvas = $("progressChart");
      if (canvas && window.Chart) {
        if (chart) chart.destroy();
        chart = new Chart(canvas, {
          type: "line",
          data: {
            labels: data.sessions.map((item) => item.date),
            datasets: [{
              label: "Game score (%)",
              data: data.sessions.map((item) => item.score),
              borderColor: "#8171e4",
              backgroundColor: "rgba(129,113,228,.10)",
              fill: true,
              tension: .38,
              pointRadius: 4,
              pointHoverRadius: 6
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {min: 0, max: 100, ticks: {stepSize: 25}, grid: {color: "#eeeaf5"}},
              x: {grid: {display: false}}
            },
            plugins: {legend: {display: false}}
          }
        });
      }
    } catch (error) {
      console.warn("Analytics unavailable", error);
    }
  }

  loadAnalytics();
})();
