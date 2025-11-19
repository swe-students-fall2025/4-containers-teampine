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
    

    

