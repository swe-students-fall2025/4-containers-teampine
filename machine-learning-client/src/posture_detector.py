"""Posture detection using MediaPipe Pose."""

import time
import cv2
import numpy as np
import mediapipe as mp


class PostureDetector:
    """Handles posture analysis using MediaPipe Pose."""

    def __init__(self):
        self.mp_pose = mp.solutions.pose
        # Use static_image_mode=True for processing independent frames
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
        )

    def analyze(self, frame):
        """
        Analyze posture from a video frame.
        Returns: (state, metrics_dict)
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.pose.process(rgb)

        if not result.pose_landmarks:
            return "unknown", {
                "timestamp": time.time(),
                "score": 0,
                "state": "unknown",
                "slouch_raw": 1.0,
            }

        lm = result.pose_landmarks.landmark

        # Helper: angle between 2 points
        def angle(p1, p2):
            return abs(np.degrees(np.arctan2(p2.y - p1.y, p2.x - p1.x)))

        # LANDMARKS
        l_shoulder = lm[11]
        r_shoulder = lm[12]
        l_ear = lm[7]
        r_ear = lm[8]
        l_hip = lm[23]
        r_hip = lm[24]

        # 1) HEAD TILT (ear → shoulder angle) - More sensitive
        head_tilt_l = angle(l_shoulder, l_ear)
        head_tilt_r = angle(r_shoulder, r_ear)
        head_tilt = min(head_tilt_l, head_tilt_r)
        # Reduced tolerance window from 15 to 10 degrees, reduced divisor for more sensitivity
        head_penalty = max(0, abs(head_tilt - 90) - 10) / 20

        # 2) SHOULDER SLOPE - More sensitive
        shoulder_angle = angle(l_shoulder, r_shoulder)
        # Reduced divisor from 30 to 20 for more sensitivity
        shoulder_penalty = min(abs(shoulder_angle - 0), abs(shoulder_angle - 180)) / 20
        shoulder_penalty = min(1, shoulder_penalty)

        # 3) UPPER BODY LEAN - More sensitive
        mid_shoulder = np.array(
            [(l_shoulder.x + r_shoulder.x) / 2, (l_shoulder.y + r_shoulder.y) / 2]
        )
        mid_hip = np.array([(l_hip.x + r_hip.x) / 2, (l_hip.y + r_hip.y) / 2])
        torso_angle = abs(
            np.degrees(
                np.arctan2(mid_hip[1] - mid_shoulder[1], mid_hip[0] - mid_shoulder[0])
            )
        )
        # Reduced divisor from 35 to 25 for more sensitivity
        torso_penalty = abs(torso_angle - 89) / 25
        torso_penalty = min(1, torso_penalty)

        # FINAL SCORE - Normalized weights (must sum to 1.0)
        # Head: 50%, Shoulders: 30%, Torso: 20%
        slouch = 0.50 * head_penalty + 0.30 * shoulder_penalty + 0.20 * torso_penalty

        # Clamp slouch to valid range [0, 1]
        slouch = max(0.0, min(1.0, slouch))

        print(
            f"Head: {head_penalty:.2f}, Shoulder: {shoulder_penalty:.2f}, Torso: {torso_penalty:.2f} → Slouch: {slouch:.2f}"
        )

        score = 100 - (slouch * 100)
        score = max(0, min(100, score))

        # Classification - More sensitive thresholds
        if score >= 80:
            state = "aligned"
        elif score >= 60:
            state = "neutral"
        else:
            state = "slouch"

        metrics = {
            "timestamp": time.time(),
            "score": round(score),
            "state": state,
            "slouch_raw": float(slouch),
            "head_tilt": float(head_tilt),
            "shoulder_angle": float(shoulder_angle),
            "torso_angle": float(torso_angle),
        }

        return state, metrics
