/**
 * SitStraight – Shared Login & Register Script
 * ------------------------------------------------------------
 * Works on BOTH login.html and register.html.
 * Handles:
 *  - Login submit behavior
 *  - Password visibility toggle (login + signup)
 *  - Basic UI messaging
 */

document.addEventListener("DOMContentLoaded", () => {
  // ============================================================
  // ELEMENT REFERENCES (exist on different pages)
  // ============================================================
  const loginForm = document.getElementById("login-form");
  const loginEmail = document.getElementById("email");
  const loginPassword = document.getElementById("password");
  const loginButton = document.getElementById("login-button");
  const loginToggle = document.getElementById("toggle-password");

  const signupPassword = document.getElementById("signup-password");
  const signupToggle = document.getElementById("toggle-signup-password");

  // ============================================================
  // 1. LOGIN FORM HANDLER (only runs on login page)
  // ============================================================
  if (loginForm) {
    loginForm.addEventListener("submit", (event) => {
      event.preventDefault(); // prevent instant reload

      const email = loginEmail.value.trim();
      const pw = loginPassword.value.trim();

      if (!email || !pw) {
        alert("Please enter both email and password.");
        return;
      }

      if (pw.length < 6) {
        alert("Password must be at least 6 characters.");
        return;
      }

      // Disable button briefly
      loginButton.disabled = true;
      loginButton.textContent = "Loading…";

      setTimeout(() => {
        loginButton.disabled = false;
        loginButton.textContent = "Continue to dashboard";
        loginForm.submit(); // now submit normally
      }, 400);
    });
  }

  // ============================================================
  // 2. PASSWORD TOGGLE — LOGIN PAGE
  // ============================================================
  if (loginPassword && loginToggle) {
    loginToggle.addEventListener("click", () => {
      const hidden = loginPassword.type === "password";
      loginPassword.type = hidden ? "text" : "password";
      loginToggle.textContent = hidden ? "Hide" : "Show";
    });
  }

  // ============================================================
  // 3. PASSWORD TOGGLE — SIGNUP PAGE
  // ============================================================
  if (signupPassword && signupToggle) {
    signupToggle.addEventListener("click", () => {
      const hidden = signupPassword.type === "password";
      signupPassword.type = hidden ? "text" : "password";
      signupToggle.textContent = hidden ? "Hide" : "Show";
    });
  }
});
