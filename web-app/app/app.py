import os
from flask import Flask, render_template, request, redirect, session, jsonify
from app.db import (
    create_user,
    validate_user,
    users,
    samples,            # <-- REQUIRED FIX
    save_posture_sample
)
from app.posture_detector import PostureDetector


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "devsecret")

detector = PostureDetector()

# ============================================================
# AUTH ROUTES
# ============================================================

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("username")
        password = request.form.get("password")

        valid, result = validate_user(email, password)
        if not valid:
            return render_template("login.html", error=result)

        session["user"] = result["email"]
        return redirect("/dashboard")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("password_confirm")

        if password != confirm:
            return render_template("register.html", error="Passwords do not match.")

        created, msg = create_user(name, email, password)
        if not created:
            return render_template("register.html", error=msg)

        return redirect("/")

    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    user = users.find_one({"email": session["user"]})

    # --- default safe values ---
    avg_score = 0
    slouch_count = 0
    total_samples = 0
    duration_minutes = 0

    # --- fetch today's posture samples ---
    from datetime import datetime, timedelta
    today = datetime.utcnow().date()
    start = datetime(today.year, today.month, today.day)
    end = start + timedelta(days=1)

    today_samples = list(samples.find({"timestamp": {"$gte": start, "$lt": end}}))

    if today_samples:
        total_samples = len(today_samples)
        avg_score = round(sum(s["score"] for s in today_samples) / total_samples)
        slouch_count = sum(1 for s in today_samples if s["state"] == "slouch")
        duration_minutes = round(total_samples * 0.35)  # ~350ms per frame

    return render_template(
        "dashboard.html",
        user=user,
        avg_score=avg_score,
        slouch_count=slouch_count,
        total_samples=total_samples,
        duration_minutes=duration_minutes,
    )



@app.route("/tracking")
def tracking():
    if "user" not in session:
        return redirect("/")
    return render_template("tracking.html")

# ============================================================
# ML API ROUTES
# ============================================================

@app.route("/api/status")
def status():
    return {"status": "ML service running"}, 200


@app.route("/process", methods=["POST"])
def process_frame():
    if "frame" not in request.files:
        return jsonify({"error": "missing frame"}), 400

    frame_bytes = request.files["frame"].read()
    result = detector.process_frame(frame_bytes)

    if result is None:
        return jsonify({"error": "processing failed"}), 500

    save_posture_sample(result)
    return jsonify(result)

# ============================================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
