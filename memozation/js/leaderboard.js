function loadLeaderboard() {
  let users = JSON.parse(localStorage.getItem("leaderboard")) || [];

  // ✅ remove users without score
  users = users.filter(u => u.score && u.score > 0);

  // sort
  users.sort((a, b) => b.score - a.score);

  let container = document.getElementById("leaderboardCards");
  container.innerHTML = "";

  users.forEach((u, index) => {
    let card = document.createElement("div");
    card.classList.add("rankCard");

    let rank = "";
    if (index === 0) rank = "🥇";
    else if (index === 1) rank = "🥈";
    else if (index === 2) rank = "🥉";
    else rank = "#" + (index + 1);

    card.innerHTML = `
      <span class="rank">${rank}</span>
      <span class="name">${u.name}</span>
      <span class="score">Level ${u.score}</span>
    `;

    container.appendChild(card);
  });
}

function goBack() {
  window.location.href = "dashboard.html";
}

loadLeaderboard();