/* Sign-up helpers: live password strength and a role hint that reacts to the email. */
(() => {
  const email = document.getElementById("email");
  const password = document.getElementById("password");
  const confirm = document.getElementById("confirm");
  const bar = document.getElementById("strengthBar");
  const hint = document.getElementById("roleHint");

  const strength = (value) => {
    let score = 0;
    if (value.length >= 8) score++;
    if (value.length >= 12) score++;
    if (/[A-Z]/.test(value) && /[a-z]/.test(value)) score++;
    if (/\d/.test(value)) score++;
    if (/[^A-Za-z0-9]/.test(value)) score++;
    return score;
  };
  const colours = ["#ff5ec8", "#ff9f5e", "#ffe05e", "#5ec8ff", "#5ef2b0"];

  password?.addEventListener("input", () => {
    const score = strength(password.value);
    bar.style.width = `${(score / 5) * 100}%`;
    bar.style.background = colours[Math.max(0, score - 1)];
  });

  confirm?.addEventListener("input", () => {
    const mismatch = (window.RL_I18N && RL_I18N.strings && RL_I18N.strings.passwords_mismatch) || "Passwords do not match";
    confirm.setCustomValidity(confirm.value && confirm.value !== password.value ? mismatch : "");
  });

  email?.addEventListener("input", () => {
    if (!hint) return;
    const isAdmin = email.value.toLowerCase().includes("admin");
    hint.innerHTML = isAdmin
      ? "<b>Admin account:</b> this email opens the admin panel and the player list with accuracy."
      : "<b>Player account:</b> this email opens your arena. Add the word <code>admin</code> to the email for a caregiver account.";
    hint.classList.toggle("hint-admin", isAdmin);
  });
})();
