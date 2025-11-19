"""
posture_detector.py

This file handles all posture analysis logic.
It uses Mediapipe Pose to extract body landmarks
and classifies posture into simple categories:

- good
- slouch
- lean_left
- lean_right
"""

import mediapipe as mp
import cv2
import math

# Initialize Mediapipe pose module
mp_pose = mp.solutions.pose


#A simple posture detection class using Mediapipe.
class PostureDetector:

    def __init__(self):
        # Mediapipe Pose model initialization
        self.pose = mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    """
    Calculates the angle between three points a, b, c.
    (Not used heavily in option A but available for expansion)
    """
    def calculate_angle(self, a, b, c):

            ang = math.degrees(
                math.atan2(c[1] - b[1], c[0] - b[0]) -
                math.atan2(a[1] - b[1], a[0] - b[0])
            )
            if ang < 0:
                ang += 360
            return ang
    
    """
    Analyzes a webcam frame and returns:
    - posture classification (string)
    - metrics (dictionary of extracted values)

    Returns:
        ("good"|"slouch"|"lean_left"|"lean_right"|"no_person", metrics_dict)
    """
    def analyze(self, frame):
        # Convert image to Mediapipe's expected RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)

        # If no body landmarks detected → no person
        if not results.pose_landmarks:
            return "no_person", {"confidence": 0}

        # Extract pose landmarks
        landmarks = results.pose_landmarks.landmark
         
        # Key points used for simple posture detection
        shoulder_left = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        shoulder_right = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        nose = landmarks[mp_pose.PoseLandmark.NOSE]

        # Convert normalized coordinates → easier to read values
        sl = (shoulder_left.x, shoulder_left.y)
        sr = (shoulder_right.x, shoulder_right.y)
        n = (nose.x, nose.y)

        # 1. Shoulder alignment (left vs right height)
        shoulder_diff = abs(sl[1] - sr[1])

        # 2. Head forward distance relative to shoulders
        mid_shoulder = ((sl[0] + sr[0]) / 2, (sl[1] + sr[1]) / 2)
        head_forward_distance = abs(n[1] - mid_shoulder[1])

        # Posture classification logic (simple, easy thresholds)
        if shoulder_diff > 0.05:
            # If left shoulder is lower → leaning left, else right
            posture = "lean_left" if sl[1] > sr[1] else "lean_right"
        elif head_forward_distance > 0.12:
            posture = "slouch"
        else:
            posture = "good"

    

    



