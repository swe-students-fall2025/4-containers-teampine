"""
main.py

Main loop for the posture detection ML client.
Runs inside its own Docker container.

Steps:
1. Open the webcam
2. Capture a frame every few seconds
3. Analyze posture using Mediapipe
4. Save results to MongoDB
"""

import cv2
import time
from posture_detector import PostureDetector
from database import DatabaseClient

# Check posture every X seconds (tunable)
CHECK_INTERVAL = 5


def main():
    print("[ML] Starting posture detection client...")

    # Initialize posture detector + database client
    detector = PostureDetector()
    db = DatabaseClient()

    # Open webcam (0 = default laptop camera)
    cap = cv2.VideoCapture(0)

    # If webcam cannot be opened, exit gracefully
    if not cap.isOpened():
        print("[ERROR] Camera not found!")
        return

    # Main detection loop
    while True:
        ret, frame = cap.read()

        # If frame not captured, skip this cycle
        if not ret:
            continue

        # Analyze posture in current frame
        posture, metrics = detector.analyze(frame)

        # Print posture to console
        print(f"[POSTURE] {posture} | {metrics}")

        # Save into MongoDB
        db.insert_posture(posture, metrics)

        # Wait before next capture
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
