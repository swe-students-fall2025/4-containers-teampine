from flask import Flask, render_template, request, redirect, session
import os
from db import create_user, validate_user

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "devsecret")


# ===============================
# LOGIN PAGE
# ===============================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("username")
        password = request.form.get("password")

        valid, result = validate_user(email, password)

        if not valid:
            return render_template("login.html", error=result)

        # Save session
        session["user"] = result["email"]
        return redirect("/dashboard")

    return render_template("login.html")


# ===============================
# REGISTER PAGE
# ===============================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("password_confirm")

        # Check if passwords match
        if password != confirm:
            return render_template("register.html", error="Passwords do not match.")

        # Attempt to create user
        created, error_msg = create_user(name, email, password)

        if not created:
            return render_template("register.html", error=error_msg)

        # Success → go to login
        return redirect("/")

    return render_template("register.html")


# ===============================
# DASHBOARD
# ===============================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html")


# ===============================
# LOGOUT
# ===============================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
