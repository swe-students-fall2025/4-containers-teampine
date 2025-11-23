# pylint: disable=RULE1, RULE2, RULE3
import os
import requests
from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, request, redirect, session, jsonify
from db import create_user, validate_user, users, samples


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "devsecret")

# ML Client URL
ML_CLIENT_URL = os.getenv("ML_CLIENT_URL", "http://ml-client:5002")

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
    hours = 0
    mins = 0

    # --- fetch today's posture samples ---
    from datetime import datetime, timedelta

    today = datetime.now(timezone.utc).date()
    start = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    today_samples = list(samples.find({"timestamp": {"$gte": start, "$lt": end}}))

    if today_samples:
        total_samples = len(today_samples)
        avg_score = round(sum(s["score"] for s in today_samples) / total_samples)
        slouch_count = sum(1 for s in today_samples if s["state"] == "slouch")

        # Calculate actual time from first to last sample
        if len(today_samples) > 1:
            timestamps = [s["timestamp"] for s in today_samples]
            first_time = min(timestamps)
            last_time = max(timestamps)
            duration_seconds = (last_time - first_time).total_seconds()
            duration_minutes = round(duration_seconds / 60)
        else:
            # Single sample = minimal time
            duration_minutes = 1

        hours = duration_minutes // 60
        mins = duration_minutes % 60

    return render_template(
        "dashboard.html",
        user=user,
        avg_score=avg_score,
        slouch_count=slouch_count,
        total_samples=total_samples,
        duration_minutes=duration_minutes,
        hours=hours,
        mins=mins,
    )


@app.route("/api/stats/weekly")
def weekly_stats():
    today = datetime.now(timezone.utc).date()
    start = today - timedelta(days=6)

    start_dt = datetime(start.year, start.month, start.day, tzinfo=timezone.utc)

    cursor = samples.find({"timestamp": {"$gte": start_dt}})

    data = list(cursor)

    daily = {}
    for s in data:
        d = s["timestamp"].date().isoformat()
        daily.setdefault(d, []).append(s["score"])

    weekly = [
        {"date": day, "avg_score": round(sum(scores) / len(scores))}
        for day, scores in sorted(daily.items())
    ]

    return jsonify(weekly)


@app.route("/api/stats/monthly")
def monthly_stats():

    today = datetime.now(timezone.utc)
    start = today.replace(day=1)

    start_dt = datetime(start.year, start.month, 1, tzinfo=timezone.utc)

    cursor = samples.find({"timestamp": {"$gte": start_dt}})

    data = list(cursor)

    # group by day
    daily = {}
    for s in data:
        d = s["timestamp"].date().isoformat()
        daily.setdefault(d, []).append(s["score"])

    monthly = [
        {"date": d, "avg_score": round(sum(scores) / len(scores))}
        for d, scores in sorted(daily.items())
    ]

    return jsonify(monthly)


@app.route("/api/stats/yearly")
def yearly_stats():

    # Get samples from the last 12 months
    today = datetime.now(timezone.utc)
    start = today.replace(year=today.year - 1)

    data = list(
        samples.find(
            {"timestamp": {"$gte": datetime(start.year, start.month, start.day)}}
        )
    )

    # Group by month
    monthly = {}
    for s in data:
        d = s["timestamp"].strftime("%Y-%m")  # YYYY-MM
        monthly.setdefault(d, []).append(s["score"])

    yearly = [
        {"month": month, "avg_score": round(sum(scores) / len(scores))}
        for month, scores in monthly.items()
    ]

    return jsonify(yearly)


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
    """Check status of ML client."""
    try:
        response = requests.get(f"{ML_CLIENT_URL}/health", timeout=2)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException:
        return jsonify({"status": "ML client unreachable"}), 503


@app.route("/process", methods=["POST"])
def process_frame():
    """Forward frame to ML client for analysis."""
    if "frame" not in request.files:
        return jsonify({"error": "missing frame"}), 400

    # Forward the frame to ML client
    try:
        files = {"frame": request.files["frame"]}
        response = requests.post(f"{ML_CLIENT_URL}/process", files=files, timeout=5)

        if response.status_code == 200:
            return jsonify(response.json()), 200
        return jsonify({"error": "ML processing failed"}), 500

    except requests.exceptions.RequestException as error:
        return jsonify({"error": f"ML client unavailable: {str(error)}"}), 503


# ============================================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
