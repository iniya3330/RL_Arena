/* RL Arena shared experience layer: particles, 3D tilt, toasts, confetti, shake, floating text,
   sound effects, count-up numbers, scroll reveal and the splash intro. */
(() => {
  const reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const $ = (id) => document.getElementById(id);

  /* ---------- sound (WebAudio, no files needed) ---------- */
  let audioCtx = null;
  const soundOn = () => { try { return localStorage.getItem("rlSound") !== "off"; } catch (_) { return true; } };
  const setSound = (on) => { try { localStorage.setItem("rlSound", on ? "on" : "off"); } catch (_) { /* private mode */ } };
  function tone(freq, dur = 0.12, type = "sine", vol = 0.08, when = 0) {
    if (!soundOn()) return;
    try {
      audioCtx = audioCtx || new (window.AudioContext || window.webkitAudioContext)();
      const t = audioCtx.currentTime + when;
      const osc = audioCtx.createOscillator(), gain = audioCtx.createGain();
      osc.type = type; osc.frequency.setValueAtTime(freq, t);
      gain.gain.setValueAtTime(0.0001, t);
      gain.gain.exponentialRampToValueAtTime(vol, t + 0.01);
      gain.gain.exponentialRampToValueAtTime(0.0001, t + dur);
      osc.connect(gain).connect(audioCtx.destination);
      osc.start(t); osc.stop(t + dur + 0.02);
    } catch (_) { /* audio unavailable */ }
  }
  const SFX = {
    correct: () => { tone(660, 0.12); tone(880, 0.16, "sine", 0.08, 0.09); },
    wrong: () => tone(170, 0.28, "sawtooth", 0.05),
    tick: () => tone(520, 0.06, "square", 0.04),
    go: () => { tone(880, 0.2, "triangle", 0.09); tone(1320, 0.25, "triangle", 0.09, 0.1); },
    levelup: () => [523, 659, 784, 1046].forEach((f, i) => tone(f, 0.22, "triangle", 0.08, i * 0.11)),
    badge: () => [784, 988, 1175].forEach((f, i) => tone(f, 0.18, "sine", 0.07, i * 0.08)),
    click: () => tone(420, 0.05, "square", 0.03),
  };

  /* ---------- canvas: particles (background) ---------- */
  function startParticles() {
    const canvas = $("particles");
    if (!canvas || reduceMotion) return;
    const ctx = canvas.getContext("2d");
    const colours = ["94,200,255", "255,94,200", "139,92,246", "94,242,176"];
    let particles = [];
    const resize = () => {
      canvas.width = window.innerWidth; canvas.height = window.innerHeight;
      const count = Math.min(70, Math.round(window.innerWidth / 22));
      particles = Array.from({length: count}, () => ({
        x: Math.random() * canvas.width, y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.25, vy: (Math.random() - 0.5) * 0.25,
        r: Math.random() * 1.6 + 0.4, c: colours[Math.floor(Math.random() * colours.length)],
      }));
    };
    const frame = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      particles.forEach((p, i) => {
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${p.c},0.85)`; ctx.fill();
        for (let j = i + 1; j < particles.length; j++) {
          const q = particles[j], d = Math.hypot(p.x - q.x, p.y - q.y);
          if (d < 110) {
            ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(q.x, q.y);
            ctx.strokeStyle = `rgba(139,92,246,${(1 - d / 110) * 0.22})`; ctx.lineWidth = 0.6; ctx.stroke();
          }
        }
      });
      requestAnimationFrame(frame);
    };
    resize(); window.addEventListener("resize", resize); requestAnimationFrame(frame);
  }

  /* ---------- canvas: foreground effects (confetti bursts) ---------- */
  const fx = {pieces: [], ctx: null, canvas: null, running: false};
  function fxSetup() {
    fx.canvas = $("fx");
    if (!fx.canvas) return;
    fx.ctx = fx.canvas.getContext("2d");
    const resize = () => { fx.canvas.width = window.innerWidth; fx.canvas.height = window.innerHeight; };
    resize(); window.addEventListener("resize", resize);
  }
  function fxLoop() {
    if (!fx.ctx) return;
    fx.ctx.clearRect(0, 0, fx.canvas.width, fx.canvas.height);
    fx.pieces = fx.pieces.filter((p) => p.life > 0);
    fx.pieces.forEach((p) => {
      p.vy += 0.22; p.vx *= 0.99; p.x += p.vx; p.y += p.vy; p.rot += p.vr; p.life -= 1;
      fx.ctx.save(); fx.ctx.globalAlpha = Math.max(0, p.life / p.max);
      fx.ctx.translate(p.x, p.y); fx.ctx.rotate(p.rot);
      fx.ctx.fillStyle = p.c;
      if (p.shape === "dot") { fx.ctx.beginPath(); fx.ctx.arc(0, 0, p.size / 2, 0, Math.PI * 2); fx.ctx.fill(); }
      else fx.ctx.fillRect(-p.size / 2, -p.size / 4, p.size, p.size / 2);
      fx.ctx.restore();
    });
    if (fx.pieces.length) requestAnimationFrame(fxLoop); else fx.running = false;
  }
  const PALETTE = ["#5ec8ff", "#ff5ec8", "#ffe05e", "#5ef2b0", "#8b5cf6", "#ff9f5e"];
  function burst(x, y, count = 60, colours = PALETTE) {
    if (reduceMotion || !fx.ctx) return;
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2, speed = 3 + Math.random() * 7;
      fx.pieces.push({x, y, vx: Math.cos(angle) * speed, vy: Math.sin(angle) * speed - 4,
        rot: Math.random() * 6, vr: (Math.random() - 0.5) * 0.4, size: 6 + Math.random() * 6,
        c: colours[i % colours.length], life: 70 + Math.random() * 30, max: 100,
        shape: Math.random() < 0.3 ? "dot" : "rect"});
    }
    if (!fx.running) { fx.running = true; requestAnimationFrame(fxLoop); }
  }
  function confetti() {
    if (!fx.canvas) return;
    [0.2, 0.5, 0.8].forEach((x, i) => setTimeout(() => burst(fx.canvas.width * x, fx.canvas.height * 0.35, 80), i * 220));
  }

  function shake(el) {
    if (!el || reduceMotion) return;
    el.classList.remove("shake"); void el.offsetWidth; el.classList.add("shake");
  }
  function flash(kind) {
    if (reduceMotion) return;
    const node = document.createElement("div");
    node.className = `screen-flash flash-${kind}`;
    document.body.appendChild(node);
    setTimeout(() => node.remove(), 600);
  }
  function floatText(text, x, y, colour = "#5ef2b0") {
    if (reduceMotion) return;
    const node = document.createElement("div");
    node.className = "float-text";
    node.textContent = text; node.style.left = `${x}px`; node.style.top = `${y}px`; node.style.color = colour;
    document.body.appendChild(node);
    setTimeout(() => node.remove(), 1300);
  }
  function countUp(el, duration = 900) {
    const target = Number(el.dataset.count || el.textContent.replace(/[^\d.-]/g, "")) || 0;
    const suffix = el.dataset.suffix || "";
    if (reduceMotion) { el.textContent = target + suffix; return; }
    const start = performance.now();
    const step = (now) => {
      const t = Math.min(1, (now - start) / duration), eased = 1 - Math.pow(1 - t, 3);
      el.textContent = Math.round(target * eased) + suffix;
      if (t < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  /* ---------- toasts ---------- */
  window.RLArena = {
    fx: {burst, confetti, shake, flash, floatText, countUp},
    sfx: SFX,
    toast(message, kind = "info", icon = "✦") {
      const stack = $("toastStack");
      if (!stack) return;
      const node = document.createElement("div");
      node.className = `toast toast-${kind}`;
      node.innerHTML = `<span class="toast-icon"></span><span class="toast-text"></span>`;
      node.querySelector(".toast-icon").textContent = icon;
      node.querySelector(".toast-text").textContent = message;
      stack.appendChild(node);
      setTimeout(() => node.classList.add("toast-out"), 3200);
      setTimeout(() => node.remove(), 3700);
    },
    sound: soundOn,
    setSound,
    unlockAudio() { try { audioCtx = audioCtx || new (window.AudioContext || window.webkitAudioContext)(); } catch (_) { /* none */ } },
  };

  /* ---------- tilt, reveal, ripple, splash ---------- */
  function enableTilt() {
    if (reduceMotion) return;
    document.querySelectorAll("[data-tilt]").forEach((el) => {
      el.addEventListener("pointermove", (event) => {
        const box = el.getBoundingClientRect();
        const x = (event.clientX - box.left) / box.width - 0.5, y = (event.clientY - box.top) / box.height - 0.5;
        el.style.transform = `perspective(900px) rotateX(${(-y * 7).toFixed(2)}deg) rotateY(${(x * 9).toFixed(2)}deg)`;
      });
      el.addEventListener("pointerleave", () => { el.style.transform = ""; });
    });
  }
  function enableReveal() {
    const items = document.querySelectorAll(".reveal");
    if (!("IntersectionObserver" in window) || reduceMotion) { items.forEach((i) => i.classList.add("in")); return; }
    const io = new IntersectionObserver((entries) => entries.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
    }), {threshold: 0.12});
    items.forEach((i) => io.observe(i));
  }
  function enableRipple() {
    document.addEventListener("pointerdown", (event) => {
      const btn = event.target.closest(".btn, .mode-tile, .answer-option, .icon-btn");
      if (!btn || reduceMotion) return;
      const rect = btn.getBoundingClientRect(), ripple = document.createElement("span");
      ripple.className = "ripple";
      ripple.style.left = `${event.clientX - rect.left}px`; ripple.style.top = `${event.clientY - rect.top}px`;
      btn.appendChild(ripple); setTimeout(() => ripple.remove(), 600);
    });
  }
  function splash() {
    const node = $("splash");
    if (!node) return;
    if (sessionStorage.getItem("rlSplash")) { node.remove(); return; }
    sessionStorage.setItem("rlSplash", "1");
    setTimeout(() => node.classList.add("gone"), reduceMotion ? 0 : 1300);
    setTimeout(() => node.remove(), reduceMotion ? 0 : 1900);
  }

  document.addEventListener("DOMContentLoaded", () => {
    fxSetup(); startParticles(); enableTilt(); enableReveal(); enableRipple(); splash();
    document.querySelectorAll("[data-count]").forEach(countUp);
    const toggle = $("soundToggle");
    if (toggle) {
      const paint = () => { toggle.textContent = soundOn() ? "🔊" : "🔇"; };
      paint();
      toggle.addEventListener("click", () => { setSound(!soundOn()); paint(); if (soundOn()) SFX.click(); });
    }
    document.addEventListener("pointerdown", () => window.RLArena.unlockAudio(), {once: true});
    document.querySelectorAll("[data-confirm]").forEach((el) => {
      el.addEventListener("click", (event) => { if (!window.confirm(el.dataset.confirm || "Continue?")) event.preventDefault(); });
    });
  });
})();
