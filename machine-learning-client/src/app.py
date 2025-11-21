"""ML service for SitStraight – provides live posture data and stores results."""

from flask import Flask, jsonify
from posture_detector import PostureDetector
from database import save_posture_sample

app = Flask(__name__)

# global detector instance
detector = PostureDetector()

@app.route("/start", methods=["POST"])
def start_tracking():
    """Start the posture detection loop."""
    detector.start()
    return jsonify({"status": "tracking started"})

@app.route("/stop", methods=["POST"])
def stop_tracking():
    """Stop posture detection."""
    detector.stop()
    return jsonify({"status": "tracking stopped"})

@app.route("/live", methods=["GET"])
def get_live_posture():
    """Return the latest posture result."""
    data = detector.get_latest()

    if data is None:
        return jsonify({"error": "no data yet"}), 404

    # save sample to database
    save_posture_sample(data)

    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)
