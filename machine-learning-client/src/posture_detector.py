"""Posture detection using MediaPipe Pose."""

import cv2
import mediapipe as mp
import threading
import time

class PostureDetector:
    """Handles webcam capture and posture analysis."""

    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.running = False
        self.latest = None
        self.thread = None

    def start(self):
        """Start webcam + ML loop in a background thread."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()

    def stop(self):
        """Stop webcam loop."""
        self.running = False

    def get_latest(self):
        """Return latest posture metrics."""
        return self.latest

    def _loop(self):
        cap = cv2.VideoCapture(0)

        while self.running:
            success, frame = cap.read()
            if not success:
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = self.pose.process(rgb)

            if result.pose_landmarks:

                # extract shoulder + hip landmarks
                lm = result.pose_landmarks.landmark
                shoulder_left = lm[11]
                shoulder_right = lm[12]

                # Example simple slouch metric
                slouch = abs(shoulder_left.y - shoulder_right.y)

                # Convert to a readable score
                score = max(0, 100 - slouch * 150)

                state = "aligned"
                if score < 60:
                    state = "slouch"
                elif score < 80:
                    state = "neutral"

                self.latest = {
                    "timestamp": time.time(),
                    "score": round(score),
                    "state": state,
                    "slouch": float(slouch),
                }

            time.sleep(0.05)

        cap.release()




