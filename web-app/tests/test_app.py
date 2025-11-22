"""Tests for Flask web app."""

import pytest
from unittest.mock import patch, Mock
from app.app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_login_page_loads(client):
    """Test that the login page loads successfully."""
    response = client.get("/")
    assert response.status_code == 200


def test_register_page_loads(client):
    """Test that the register page loads successfully."""
    response = client.get("/register")
    assert response.status_code == 200


def test_dashboard_requires_login(client):
    """Test that dashboard redirects when not logged in."""
    response = client.get("/dashboard")
    assert response.status_code == 302  # Redirect to login


@patch("app.app.requests.get")
def test_api_status(mock_get, client):
    """Test API status endpoint."""
    # Mock ML client response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "healthy"}
    mock_get.return_value = mock_response

    response = client.get("/api/status")
    assert response.status_code == 200

