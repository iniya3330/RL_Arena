/* Admin panel: player list with accuracy bands, search, filters, sort, live refresh,
   enable/disable accounts, accuracy distribution and the decision-tree predictor. */
(() => {
  const cfg = window.RL_CONFIG || {};
  const $ = (id) => document.getElementById(id);
  const esc = (t) => String(t ?? "").replace(/[&<>"']/g, (c) => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]));
  const csrf = () => {
    const formToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
    if (formToken) return formToken;
    const m = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : "";
  };
  const fx = () => window.RLArena || {};

  let players = JSON.parse($("initialPlayers")?.textContent || "[]");
  let band = "all", query = "", sortKey = "accuracy";

  const SORTERS = {
    accuracy: (a, b) => (b.accuracy ?? -1) - (a.accuracy ?? -1),
    xp: (a, b) => b.xp - a.xp,
    runs: (a, b) => b.runs - a.runs,
    name: (a, b) => a.name.localeCompare(b.name),
    last: (a, b) => (b.last_active || "").localeCompare(a.last_active || ""),
  };

  function accChip(p) {
    if (p.accuracy === null) return '<span class="acc acc-none">No answers</span>';
    return `<span class="acc acc-${p.band}">${p.accuracy}%</span><span class="mini"><span style="width:${p.accuracy}%"></span></span>`;
  }

  function renderDistribution() {
    const counts = {high: 0, mid: 0, low: 0, none: 0};
    players.forEach((p) => { counts[p.band] = (counts[p.band] || 0) + 1; });
    const total = Math.max(1, players.length);
    $("dist").innerHTML = ["high", "mid", "low", "none"].map((b) => `
      <div class="dist-seg dist-${b}" style="flex:${counts[b] || 0.0001}" title="${counts[b]} ${b}">
        <b>${counts[b]}</b></div>`).join("") + `<p class="muted dist-total">${players.length} players · ${Math.round(((counts.high || 0) / total) * 100)}% high accuracy</p>`;
  }

  function visiblePlayers() {
    return players
      .filter((p) => band === "all" || p.band === band)
      .filter((p) => !query || `${p.name} ${p.email}`.toLowerCase().includes(query))
      .sort(SORTERS[sortKey]);
  }

  function renderRows() {
    const list = visiblePlayers();
    $("shownCount").textContent = `${list.length} shown`;
    if (!list.length) {
      $("playersBody").innerHTML = `<tr><td colspan="7" class="empty-cell">No players match these filters.</td></tr>`;
      return;
    }
    $("playersBody").innerHTML = list.map((p, i) => `
      <tr class="player-row" style="animation-delay:${Math.min(i, 20) * 40}ms" data-id="${p.id}">
        <td><div class="who"><span class="avatar-chip">${esc(p.name.slice(0, 1).toUpperCase())}</span>
          <span><b>${esc(p.name)}</b><small>${esc(p.email)}</small></span></div></td>
        <td class="acc-cell">${accChip(p)}</td>
        <td>${p.runs}</td>
        <td>LV ${p.level}<small class="muted"> · ${p.xp} XP</small></td>
        <td>${p.cleared}</td>
        <td><span class="status ${p.active ? "on" : "off"}">${p.active ? "Active" : "Disabled"}</span></td>
        <td class="actions">
          <a class="btn btn-ghost btn-sm" href="${cfg.userBase}${p.id}/">View</a>
          <button class="btn btn-sm ${p.active ? "btn-danger" : "btn-neon"}" data-toggle="${p.id}" type="button">${p.active ? "Disable" : "Enable"}</button>
        </td>
      </tr>`).join("");
    $("playersBody").querySelectorAll("[data-toggle]").forEach((btn) =>
      btn.addEventListener("click", () => toggle(Number(btn.dataset.toggle), btn)));
  }

  function renderAll() { renderDistribution(); renderRows(); }

  async function refresh(manual = false) {
    try {
      const response = await fetch(cfg.playersUrl, {credentials: "same-origin"});
      if (!response.ok) throw new Error("refresh failed");
      const data = await response.json();
      const before = JSON.stringify(players);
      players = data.players;
      renderAll();
      if (manual && before !== JSON.stringify(players)) fx().toast("Player list updated", "info", "↻");
    } catch (error) {
      if (manual) fx().toast("Could not refresh the list", "warn", "⚠️");
    }
  }

  async function toggle(id, button) {
    button.disabled = true;
    try {
      const token = csrf();
      if (!token) throw new Error("CSRF token is missing. Reload the page and try again.");
      const body = new FormData();
      body.append("csrfmiddlewaretoken", token);
      body.append("next", `${cfg.userBase}${id}/`);
      const response = await fetch(`${cfg.toggleBase}${id}/toggle/`, {method: "POST", body, credentials: "same-origin"});
      if (!response.ok) throw new Error("request failed");
      await refresh();
      const player = players.find((p) => p.id === id);
      if (player) fx().toast(`${player.name} is now ${player.active ? "active" : "disabled"}`, player.active ? "good" : "warn", player.active ? "✅" : "⛔");
    } catch (error) {
      button.disabled = false;
      fx().toast("Could not change this account", "warn", "⚠️");
    }
  }

  /* filters */
  $("playerSearch")?.addEventListener("input", (e) => { query = e.target.value.trim().toLowerCase(); renderRows(); });
  $("sortBy")?.addEventListener("change", (e) => { sortKey = e.target.value; renderRows(); });
  document.querySelectorAll("#bandFilters [data-band]").forEach((btn) => btn.addEventListener("click", () => {
    band = btn.dataset.band;
    document.querySelectorAll("#bandFilters [data-band]").forEach((b) => b.classList.toggle("is-on", b === btn));
    renderRows();
  }));
  $("refreshBtn")?.addEventListener("click", () => refresh(true));
  setInterval(() => refresh(false), 30000);

  renderAll();

  /* ---------- decision-tree predictor ---------- */
  const form = $("predictForm");
  if (form) {
    const format = {accuracy: (v) => `${Math.round(v * 100)}%`, overall_skill: (v) => `${Math.round(v * 100)}%`};
    const predict = async () => {
      const params = new URLSearchParams();
      form.querySelectorAll("input[type=range]").forEach((input) => {
        params.set(input.name, input.value);
        const out = form.querySelector(`[data-out="${input.name}"]`);
        if (out) out.textContent = (format[input.name] || ((v) => v))(input.value);
      });
      try {
        const response = await fetch(`${cfg.predictUrl}?${params}`, {credentials: "same-origin"});
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Prediction failed");
        $("predLevel").textContent = `Next band ${data.next_difficulty}`;
        $("predConfidence").style.width = `${Math.round(data.confidence * 100)}%`;
        $("predReason").textContent = `${data.reason} Confidence ${Math.round(data.confidence * 100)}%.`;
        $("predImportance").innerHTML = Object.entries(data.feature_importances)
          .sort((a, b) => b[1] - a[1])
          .map(([name, w]) => `<li><span>${esc(name.replace(/_/g, " "))}</span><b>${Math.round(w * 100)}%</b></li>`).join("");
      } catch (error) { $("predReason").textContent = error.message; }
    };
    form.addEventListener("input", predict);
    predict();
  }
})();
