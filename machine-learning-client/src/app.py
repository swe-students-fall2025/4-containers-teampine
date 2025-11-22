"""ML service for SitStraight – provides live posture data and stores results."""

from flask import Flask, jsonify, request
import numpy as np
from posture_detector import PostureDetector
from database import DatabaseClient

app = Flask(__name__)

# global detector instance
detector = PostureDetector()
db = DatabaseClient()





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

    # Decode image
    import cv2
    np_arr = np.frombuffer(frame_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img is None:
        return jsonify({"error": "failed to decode frame"}), 400

    # Analyze posture
    state, metrics = detector.analyze(img)

    # Save to DB
    db.insert_posture(state, metrics)

    return jsonify(metrics)




@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "ml-client"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)

