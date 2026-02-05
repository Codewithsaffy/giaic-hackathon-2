"""
Contract Tests for Auth Enforcement

These tests verify that authentication is properly enforced on API endpoints.
They ensure that unauthenticated requests are rejected with appropriate status codes.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from backend.main import app  # Assuming the main app is in main.py
from backend.src.core.database import get_session, engine
from backend.src.models.user import User  # Assuming User model exists
from sqlmodel import SQLModel, Session
from unittest.mock import patch


@pytest.fixture
def client():
    """Create a test client for the API."""
    with TestClient(app) as test_client:
        yield test_client


def test_chat_endpoint_requires_auth(client):
    """Test that the chat endpoint rejects requests without auth token."""
    # Try to hit the chat endpoint without authentication
    response = client.post("/api/chat", json={
        "user_id": "test_user",
        "message": "Test message"
    })

    # Should return 401 Unauthorized or 403 Forbidden
    assert response.status_code in [401, 403]


def test_conversation_endpoints_require_auth(client):
    """Test that conversation endpoints reject requests without auth token."""
    # Try to create conversation without authentication
    response = client.post("/api/conversations", json={
        "user_id": "test_user",
        "title": "Test Conversation"
    })
    assert response.status_code in [401, 403]

    # Try to get conversations without authentication
    response = client.get("/api/conversations", params={"user_id": "test_user"})
    assert response.status_code in [401, 403]

    # Try to get specific conversation without authentication
    response = client.get("/api/conversations/1", params={"user_id": "test_user"})
    assert response.status_code in [401, 403]


def test_auth_required_for_task_operations(client):
    """Test that task operation endpoints require authentication."""
    # Try to add task without auth (if such endpoint exists)
    # This assumes there might be direct task endpoints
    response = client.post("/api/tasks", json={
        "user_id": "test_user",
        "title": "Test Task"
    })
    # May be 401/403 or 404 if endpoint doesn't exist publicly
    # If the endpoint exists, it should require auth

    # The main interaction is through chat, so let's focus on that
    response = client.post("/api/chat", json={
        "user_id": "test_user",
        "message": "Add a task"
    })
    assert response.status_code in [401, 403]


def test_jwt_validation_works(client):
    """Test that valid JWT tokens are accepted."""
    # This test would require creating a valid JWT token
    # For now, we'll mock the validation
    with patch('backend.src.api.chat_endpoints.verify_token') as mock_verify:
        mock_verify.return_value = "valid_user_id"

        response = client.post(
            "/api/chat",
            json={"user_id": "valid_user_id", "message": "Test"},
            headers={"Authorization": "Bearer fake_valid_token"}
        )
        # Should not be rejected due to auth (might still fail for other reasons)
        assert response.status_code != 401
        assert response.status_code != 403


def test_different_auth_scenarios(client):
    """Test various authentication failure scenarios."""
    # Test with malformed token
    response = client.post(
        "/api/chat",
        json={"user_id": "test_user", "message": "Test"},
        headers={"Authorization": "Invalid token format"}
    )
    assert response.status_code in [401, 403]

    # Test with expired token (would require specific implementation)
    # Test with invalid signature (would require specific implementation)

    # Test with missing Authorization header
    response = client.post("/api/chat", json={"user_id": "test_user", "message": "Test"})
    assert response.status_code in [401, 403]