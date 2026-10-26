// GET CURRENT USER
let user = localStorage.getItem("currentUser");

// Redirect if not logged in
if (!user) {
  window.location.replace("index.html");
}

// SHOW USER NAME
document.getElementById("user").innerText = user;


// 🔒 Disable back button (go to login)
window.history.pushState(null, null, location.href);

window.onpopstate = function () {
  window.location.replace("index.html");
};


// 🎮 LOAD LEVELS ONLY (NO LEADERBOARD HERE)
function loadLevels() {
  let container = document.getElementById("levelContainer");
  container.innerHTML = "";

  let unlocked = parseInt(localStorage.getItem(user + "_unlocked")) || 1;

  for (let i = 1; i <= 25; i++) {
    let card = document.createElement("div");
    card.classList.add("levelCard");
    card.innerText = i;

    if (i <= unlocked) {
      card.onclick = () => startLevel(i);
    } else {
      card.classList.add("locked");
    }

    container.appendChild(card);
  }
}


// ▶️ START LEVEL
function startLevel(level) {
  localStorage.setItem("selectedLevel", level);
  window.location.replace("game.html");
}


// 🏆 OPEN LEADERBOARD PAGE
function openLeaderboard() {
  window.location.href = "leaderboard.html";
}


// 🚀 INIT
loadLevels();