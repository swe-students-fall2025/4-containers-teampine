"""Tests for posture detection module."""

import numpy as np
import cv2
from src.posture_detector import PostureDetector


def test_posture_detector_initialization():
    """Test that PostureDetector initializes correctly."""
    detector = PostureDetector()
    assert detector is not None
    assert detector.mp_pose is not None


def test_analyze_with_empty_frame():
    """Test analyze with a blank frame (no person detected)."""
    detector = PostureDetector()
    # Create a blank black image
    blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    state, metrics = detector.analyze(blank_frame)

    assert state == "unknown"
    assert metrics["state"] == "unknown"
    assert metrics["score"] == 0


def test_analyze_returns_correct_format():
    """Test that analyze returns the expected data structure."""
    detector = PostureDetector()
    # Create a test frame
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    state, metrics = detector.analyze(frame)

    # Check return format
    assert isinstance(state, str)
    assert isinstance(metrics, dict)
    assert "score" in metrics
    assert "state" in metrics
    assert "slouch_raw" in metrics
    assert "timestamp" in metrics
