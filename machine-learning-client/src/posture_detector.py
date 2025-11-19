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
