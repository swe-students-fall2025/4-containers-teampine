"""Tests for database module."""

from unittest.mock import patch, Mock
import pytest


@patch("app.db.MongoClient")
def test_database_connection(mock_mongo):
    """Test database connection."""
    # This will be imported after mocking
    mock_client = Mock()
    mock_mongo.return_value = mock_client

    # Import after mocking
    from app import db

    assert db is not None


def test_email_validation():
    """Test email validation function."""
    from app.db import is_valid_email

    assert is_valid_email("test@example.com") is True
    assert is_valid_email("invalid.email") is False
    assert is_valid_email("@example.com") is False


def test_password_strength():
    """Test password strength validation."""
    from app.db import is_strong_password

    # Valid password
    strong, msg = is_strong_password("Passw0rd")
    assert strong is True

    # Too short
    strong, msg = is_strong_password("Pas1")
    assert strong is False

    # No uppercase
    strong, msg = is_strong_password("password1")
    assert strong is False

    # No number
    strong, msg = is_strong_password("Password")
    assert strong is False
