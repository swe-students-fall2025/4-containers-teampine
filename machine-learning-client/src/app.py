# ml-client/src/app.py
from flask import Flask, request, jsonify
import mediapipe as mp
import cv2
import numpy as np

app = Flask(__name__)

@app.route("/analyze_frame", methods=["POST"])
def analyze_frame():
    file = request.files.get("frame")
    if not file:
        return jsonify({"error": "No frame received"})

    # Convert JPEG → numpy array
    jpg = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(jpg, cv2.IMREAD_COLOR)

    # TODO: apply posture model
    # For now, return dummy slouch detection:
    return jsonify({
        "slouching": False,
        "angle": 0,
        "confidence": 0.90
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
