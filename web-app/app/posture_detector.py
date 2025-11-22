"""Posture detection using MediaPipe Pose."""

import cv2
import mediapipe as mp
import threading
import time
import numpy as np

class PostureDetector:
    """Handles webcam capture and posture analysis."""

    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.running = False
        self.latest = None
        self.thread = None

    # =====================================================
    # LIVE MODE (background webcam loop)
    # =====================================================
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

            result = self._analyze(frame)
            if result:
                self.latest = result

            time.sleep(0.05)

        cap.release()

    # =====================================================
    # API MODE — process a SINGLE UPLOADED FRAME
    # =====================================================
    def process_frame(self, frame_bytes):
        """
        Processes a single uploaded frame (from /process API).
        Takes raw bytes → decodes → returns ML analysis dict.
        """

        # Decode JPEG bytes into numpy array
        np_arr = np.frombuffer(frame_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            print("Frame decode error")
            return None

        return self._analyze(img)

    # =====================================================
    # SHARED ANALYSIS LOGIC
    # =====================================================
    def _analyze(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.pose.process(rgb)

        if not result.pose_landmarks:
            return {"timestamp": time.time(), "score": 0, "state": "unknown"}

        lm = result.pose_landmarks.landmark

        # Helper: angle between 2 points
        def angle(p1, p2):
            return abs(np.degrees(np.arctan2(
                p2.y - p1.y,
                p2.x - p1.x
            )))

        # LANDMARKS
        L_shoulder = lm[11]
        R_shoulder = lm[12]
        L_ear = lm[7]
        R_ear = lm[8]
        L_hip = lm[23]
        R_hip = lm[24]

        # ==============================================================
        # 1) HEAD TILT (ear → shoulder angle)
        # Normal if 70–110 degrees. Bad if <60 or >120.
        # ==============================================================
        head_tilt_L = angle(L_shoulder, L_ear)
        head_tilt_R = angle(R_shoulder, R_ear)

        head_tilt = min(head_tilt_L, head_tilt_R)     # pick best side
        head_penalty = max(0, abs(head_tilt - 90) - 15) / 25  # normalized 0–1

        # ==============================================================
        # 2) SHOULDER SLOPE (left shoulder → right shoulder angle)
        # Normal if nearly horizontal
        # ==============================================================    
        shoulder_angle = angle(L_shoulder, R_shoulder)
        shoulder_penalty = min(abs(shoulder_angle - 0), abs(shoulder_angle - 180)) / 30
        shoulder_penalty = min(1, shoulder_penalty)

        # ==============================================================
        # 3) UPPER BODY LEAN (mid-shoulder → mid-hip vertical angle)
        # ==============================================================
        mid_shoulder = np.array([(L_shoulder.x + R_shoulder.x)/2,
                                (L_shoulder.y + R_shoulder.y)/2])

        mid_hip = np.array([(L_hip.x + R_hip.x)/2,
                            (L_hip.y + R_hip.y)/2])

        torso_angle = abs(np.degrees(np.arctan2(
            mid_hip[1] - mid_shoulder[1],
            mid_hip[0] - mid_shoulder[0]
        )))

        torso_penalty = abs(torso_angle - 89) / 35       # normalized 0–1
        torso_penalty = min(1, torso_penalty)

        # ==============================================================
        # FINAL SCORE (weighted)
        # ==============================================================
        slouch = (
            0.48 * head_penalty +
            0.38 * shoulder_penalty +
            0.23 * torso_penalty
        )  # 0 = perfect, 1 = horrible

        score = 100 - (slouch * 100)
        score = max(0, min(100, score))

        # classification
        if score >= 85:
            state = "aligned"
        elif score >= 65:
            state = "neutral"
        else:
            state = "slouch"

        print({
            "head_tilt": head_tilt,
            "shoulder_angle": shoulder_angle,
            "torso_angle": torso_angle,
            "slouch": slouch,
            "score": score,
            "state": state
        })

        return {
            "timestamp": time.time(),
            "score": round(score),
            "state": state,
            "slouch_raw": float(slouch)
        }
