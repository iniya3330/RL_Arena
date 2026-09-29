const colors = ["red", "blue", "green", "yellow"];

let pattern = [];
let user = localStorage.getItem("currentUser");
let level = parseInt(localStorage.getItem(user + "_unlocked")) || 1;
let currentQuestion = "";
let correctAnswer = "";
let questionGenerated = false;

const levelPlan = [
  "color","number","math","memory","pattern",
  "color","number","math","memory","pattern",
  "color","number","math","memory","pattern",
  "color","number","math","memory","pattern",
  "color","number","math","memory","pattern"
];

function getDifficulty(level) {
  if (level <= 5) return "easy";
  if (level <= 10) return "medium";
  if (level <= 15) return "easy";
  if (level <= 20) return "medium";
  return "medium";
}

// START LEVEL
function startLevel() {
  document.getElementById("level").innerText = level;

  document.getElementById("startSection").style.display = "none";

  questionGenerated = false;

  const box = document.getElementById("patternBox");
  box.innerHTML = "";
  box.classList.remove("fadeIn","fadeOut");

  document.getElementById("questionBox").innerText = "";
  document.getElementById("answerInput").value = "";
  document.getElementById("answerSection").style.display = "none";

  let type = levelPlan[level - 1];
  let diff = getDifficulty(level);

  if (type === "color") generateColor(diff);
  else if (type === "number") generateNumber(diff);
  else if (type === "math") generateMath(diff);
  else if (type === "memory") generateMemory(diff);
  else if (type === "pattern") generateLogic(diff);
}

// ================= COLOR =================
function generateColor(diff) {
  let size = diff === "easy" ? 3 : 5;

  pattern = [];
  for (let i = 0; i < size; i++) {
    pattern.push(colors[Math.floor(Math.random() * colors.length)]);
  }

  showPattern();
}

// ================= NUMBER =================
function generateNumber(diff) {
  let size = diff === "easy" ? 3 : 5;
  let nums = [];

  for (let i = 0; i < size; i++) {
    nums.push(Math.floor(Math.random() * 10));
  }

  const box = document.getElementById("patternBox");
  box.classList.add("fadeIn");
  box.innerText = nums.join(" ");

  correctAnswer = nums.reverse().join("");
  currentQuestion = "Enter numbers in reverse";

  showAfterDelay();
}

// ================= MATH =================
function generateMath(diff) {
  let a = Math.floor(Math.random() * (diff === "easy" ? 10 : 20));
  let b = Math.floor(Math.random() * (diff === "easy" ? 10 : 20));

  const box = document.getElementById("patternBox");
  box.classList.add("fadeIn");
  box.innerText = `${a}   ${b}`;

  let ops = ["add", "sub", "mul"];
  let op = ops[Math.floor(Math.random() * ops.length)];

  if (op === "add") {
    correctAnswer = (a + b).toString();
    currentQuestion = "Add the numbers";
  } else if (op === "sub") {
    correctAnswer = (a - b).toString();
    currentQuestion = "Subtract the numbers";
  } else {
    correctAnswer = (a * b).toString();
    currentQuestion = "Multiply the numbers";
  }

  setTimeout(() => {
    box.classList.add("fadeOut");

    setTimeout(() => {
      box.innerText = "";
      box.classList.remove("fadeOut");

      showQuestion();
      document.getElementById("answerSection").style.display = "block";
    }, 500);

  }, 3000);
}

// ================= MEMORY =================
function generateMemory(diff) {
  let words = diff === "easy"
    ? ["cat", "dog", "sun"]
    : ["apple", "train", "school"];

  let word = words[Math.floor(Math.random() * words.length)];

  const box = document.getElementById("patternBox");
  box.classList.add("fadeIn");
  box.innerText = word;

  correctAnswer = word;
  currentQuestion = "Type the same word";

  showAfterDelay();
}

// ================= LOGIC =================
function generateLogic(diff) {
  let sequence;

  if (diff === "easy") {
    sequence = [2, 4, 6];
    correctAnswer = "8";
  } else {
    sequence = [3, 6, 12];
    correctAnswer = "24";
  }

  const box = document.getElementById("patternBox");
  box.classList.add("fadeIn");
  box.innerText = sequence.join(", ");

  currentQuestion = "Find next number";

  showAfterDelay();
}

// ================= COLOR PATTERN =================
function showPattern() {
  const box = document.getElementById("patternBox");

  box.classList.add("fadeIn");

  pattern.forEach(color => {
    let div = document.createElement("div");
    div.className = "colorBlock";
    div.style.background = color;
    box.appendChild(div);
  });

  setTimeout(() => {
    box.classList.add("fadeOut");

    setTimeout(() => {
      box.innerHTML = "";
      box.classList.remove("fadeOut");

      document.getElementById("answerSection").style.display = "block";

      if (!questionGenerated) {
        generateQuestion();
        questionGenerated = true;
      }
    }, 500);

  }, 3000);
}

// ================= QUESTIONS =================
function generateQuestion() {
  let types = ["position", "count", "reverse", "missing"];
  let type = types[Math.floor(Math.random() * types.length)];
  createQuestion(type);
}

function createQuestion(type) {

  if (type === "position") {
    let pos = Math.floor(Math.random() * pattern.length);
    currentQuestion = `What is the color in position ${pos + 1}?`;
    correctAnswer = pattern[pos];
  }

  else if (type === "count") {
    let target = colors[Math.floor(Math.random() * colors.length)];
    let count = pattern.filter(c => c === target).length;

    currentQuestion = `How many ${target} colors?`;
    correctAnswer = count.toString();
  }

  else if (type === "reverse") {
    currentQuestion = "Enter colors in reverse (comma separated)";
    correctAnswer = [...pattern].reverse().join(",");
  }

  else if (type === "missing") {
    let pos = Math.floor(Math.random() * pattern.length);
    correctAnswer = pattern[pos];

    let temp = [...pattern];
    temp[pos] = "?";

    currentQuestion = `Find the missing color: ${temp.join(", ")}`;
  }

  showQuestion();
}

// ================= HELPERS =================
function showAfterDelay() {
  const box = document.getElementById("patternBox");

  setTimeout(() => {
    box.classList.add("fadeOut");

    setTimeout(() => {
      box.innerText = "";
      box.classList.remove("fadeOut");

      showQuestion();
      document.getElementById("answerSection").style.display = "block";
    }, 500);

  }, 3000);
}

function showQuestion() {
  document.getElementById("questionBox").innerText = currentQuestion;
}

// ================= ANSWER =================
function submitAnswer() {
  let userAns = document.getElementById("answerInput").value
    .toLowerCase()
    .replace(/\s+/g, "");

  if (userAns == correctAnswer) {
    alert("Correct!");
    nextLevel();
  } else {
    gameOver();
  }
}

// ================= NEXT LEVEL =================
function nextLevel() {
  level++;

  localStorage.setItem(user + "_unlocked", level);

  let users = JSON.parse(localStorage.getItem("leaderboard")) || [];
  let existing = users.find(u => u.name === user);

  if (existing) {
    existing.score = level - 1;
  } else {
    users.push({ name: user, score: level - 1 });
  }

  localStorage.setItem("leaderboard", JSON.stringify(users));

  if (level > 25) {
    alert("You completed all levels!");
    return;
  }

  startLevel();
}

// ================= GAME OVER =================
function gameOver() {
  document.getElementById("failPopup").style.display = "flex";
}

// ================= EXTRA =================
function retryLevel() {
  document.getElementById("failPopup").style.display = "none";
  startLevel();
}

function goDashboard() {
  window.location.replace("dashboard.html");
}

function exitGame() {
  document.getElementById("exitPopup").style.display = "flex";
}

function confirmExit() {
  window.location.replace("dashboard.html");
}

function closeExit() {
  document.getElementById("exitPopup").style.display = "none";
}