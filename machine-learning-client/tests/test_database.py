"""Tests for database module."""

import sys
from unittest.mock import Mock, patch
import pytest


def test_database_client_initialization():
    """Test that DatabaseClient initializes correctly."""
    # Mock pymongo to avoid actual database connection during tests
    with patch("src.database.MongoClient"):
        from src.database import DatabaseClient

        db_client = DatabaseClient()
        assert db_client is not None


def test_insert_posture():
    """Test inserting posture data."""
    with patch("src.database.MongoClient"):
        from src.database import DatabaseClient

        db_client = DatabaseClient()
        db_client.samples = Mock()

        # Test data
        state = "slouch"
        metrics = {"score": 65, "slouch_raw": 0.35}

        # Call insert
        db_client.insert_posture(state, metrics)

        # Verify insert_one was called
        assert db_client.samples.insert_one.called
