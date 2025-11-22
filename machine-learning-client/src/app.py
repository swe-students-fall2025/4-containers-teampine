"""ML service for SitStraight – provides live posture data and stores results."""

from flask import Flask, jsonify, request
from posture_detector import PostureDetector
from database import save_posture_sample
import cv2
import numpy as np

app = Flask(__name__)

# global detector instance
detector = PostureDetector()





# ===========================================
#   OPTION A — Browser uploads frames
#   ML processes them (NO webcam in Python)
# ===========================================


@app.route("/")
def root():
    return {"status": "ML service running"}, 200

@app.route("/process", methods=["POST"])
def process_frame():
    """Accept one frame from frontend, return posture analysis."""
    if "frame" not in request.files:
        return jsonify({"error": "missing frame"}), 400

    file = request.files["frame"]
    frame_bytes = file.read()

    result = detector.process_frame(frame_bytes)

    if result is None:
        return jsonify({"error": "processing failed"}), 500

    # Save to DB
    save_posture_sample(result)

    return jsonify(result)




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
    app.run(host="0.0.0.0", port=5002)

