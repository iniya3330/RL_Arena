// 🔐 SIGNUP
function signup() {
  let user = document.getElementById("newUser").value.toLowerCase();
  let pass = document.getElementById("newPass").value;

  if (user.trim() === "" || pass.trim() === "") {
    alert("Enter username and password");
    return;
  }

  let users = JSON.parse(localStorage.getItem("users")) || {};

  if (users[user]) {
    alert("User already exists!");
    return;
  }

  users[user] = pass;
  localStorage.setItem("users", JSON.stringify(users));

  alert("Signup Successful!");
  window.location.replace("index.html");
}

// 🔑 LOGIN
function login() {
  let username = document.getElementById("username").value.toLowerCase();
  let password = document.getElementById("password").value;

  if (username.trim() === "" || password.trim() === "") {
    alert("Enter username and password");
    return;
  }

  let users = JSON.parse(localStorage.getItem("users")) || {};

  if (!users[username]) {
    alert("User not found! Please signup.");
    return;
  }

  if (users[username] !== password) {
    alert("Incorrect password!");
    return;
  }

  localStorage.setItem("currentUser", username);
  window.location.replace("dashboard.html");
}