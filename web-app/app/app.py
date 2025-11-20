# app/app.py

"""Main Flask application for SitStraight."""

import os
from flask import Flask, render_template, request, redirect, session
from db import create_user, validate_user
from db import users  # import the collection

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "devsecret")


# ===============================
# LOGIN PAGE
# ===============================
@app.route("/", methods=["GET", "POST"])
def login():
    """Render login page and authenticate user."""
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
    """Render registration page and create user in MongoDB."""

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
# DASHBOARD PAGE
# ===============================
@app.route("/dashboard")
def dashboard():
    """Display dashboard for logged-in user."""
    if "user" not in session:
        return redirect("/")


    # Load user from MongoDB
    user_data = users.find_one({"email": session["user"]})

    return render_template("dashboard.html", user=user_data)


'''
# in app/app.py

@app.route("/tracking")
def tracking():
    if "user" not in session:
        return redirect("/")
    return render_template("tracking.html")
'''





# ===============================
# LOGOUT
# ===============================
@app.route("/logout")
def logout():
    """Clear session and logout."""
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
