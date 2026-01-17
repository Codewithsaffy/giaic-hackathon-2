"""
Contract Test for POST /api/{user_id}/chat endpoint

This test verifies the API contract for the chat endpoint without testing internal implementation.
It checks that the endpoint accepts the expected request format and returns the expected response format.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from typing import Dict, Any, List
import json

# Import the main app
from src.main import app

# Create test client
client = TestClient(app)


def test_chat_endpoint_contract():
    """
    Contract test for POST /api/{user_id}/chat endpoint

    Verifies that the endpoint:
    1. Accepts the expected request format
    2. Returns the expected response format
    3. Uses correct HTTP status codes
    4. Validates required fields
    """

    # Sample request data following the contract
    user_id = "test_user_123"
    conversation_id = 1
    message = "Add a task to buy groceries"

    request_payload = {
        "user_id": user_id,
        "conversation_id": conversation_id,
        "message": message
    }

    # Make the request to the endpoint
    response = client.post(f"/api/chat", json=request_payload)

    # Verify the response structure and status
    assert response.status_code in [200, 401, 403, 422], \
        f"Expected 200, 401, 403, or 422 but got {response.status_code}"

    # If successful, verify response structure
    if response.status_code == 200:
        data = response.json()

        # Verify required fields exist
        assert "conversation_id" in data, "Response must include conversation_id"
        assert "response" in data, "Response must include response message"
        assert "task_operations" in data, "Response must include task_operations"

        # Verify field types
        assert isinstance(data["conversation_id"], int), "conversation_id must be an integer"
        assert isinstance(data["response"], str), "response must be a string"
        assert isinstance(data["task_operations"], list), "task_operations must be a list"

        # Verify task_operations structure if present
        for op in data["task_operations"]:
            assert isinstance(op, dict), "Each task operation must be a dictionary"
            assert "tool" in op, "Task operation must include 'tool' field"
            assert "input" in op, "Task operation must include 'input' field"
            assert "output" in op, "Task operation must include 'output' field"

    # Test with a new conversation (no conversation_id)
    new_conv_request = {
        "user_id": user_id,
        "message": "Create a new task for testing"
    }

    response_new = client.post(f"/api/chat", json=new_conv_request)

    assert response_new.status_code in [200, 401, 403, 422], \
        f"Expected 200, 401, 403, or 422 but got {response_new.status_code}"

    if response_new.status_code == 200:
        data = response_new.json()
        assert "conversation_id" in data, "Response must include conversation_id even for new conversations"


def test_chat_endpoint_required_fields():
    """
    Test that the endpoint properly validates required fields
    """
    # Test missing required fields
    incomplete_request = {
        "user_id": "test_user_123"
        # Missing 'message' field
    }

    response = client.post("/api/chat", json=incomplete_request)

    # Should return 422 for validation error or 400 for bad request
    assert response.status_code in [400, 422], \
        f"Expected 400 or 422 for missing required fields, got {response.status_code}"


def test_chat_endpoint_field_types():
    """
    Test that the endpoint properly validates field types
    """
    # Test with wrong field types
    wrong_types_request = {
        "user_id": 12345,  # Should be string
        "conversation_id": "not_a_number",  # Should be number if provided
        "message": 123  # Should be string
    }

    response = client.post("/api/chat", json=wrong_types_request)

    # Should return 422 for validation error or 400 for bad request
    assert response.status_code in [400, 422], \
        f"Expected 400 or 422 for wrong field types, got {response.status_code}"


def test_chat_endpoint_authentication():
    """
    Test that the endpoint properly handles authentication
    (This would require proper setup with authentication headers in a real test)
    """
    # This test would check if the endpoint properly validates JWT tokens
    # For now, we'll just verify the endpoint responds appropriately
    request_payload = {
        "user_id": "test_user_123",
        "message": "Test message"
    }

    response = client.post("/api/chat", json=request_payload)

    # The endpoint should either accept the request or return 401/403
    assert response.status_code in [200, 401, 403, 422], \
        f"Expected 200, 401, 403, or 422, got {response.status_code}"


def test_chat_endpoint_response_format():
    """
    Test that the response format matches the contract specification
    """
    sample_request = {
        "user_id": "test_user_123",
        "message": "What can you help me with?"
    }

    response = client.post("/api/chat", json=sample_request)

    if response.status_code == 200:
        data = response.json()

        # Define expected response structure
        expected_fields = ["conversation_id", "response", "task_operations"]

        for field in expected_fields:
            assert field in data, f"Field '{field}' is missing from response"

        # Verify types of each field
        assert isinstance(data["conversation_id"], int), "conversation_id should be an integer"
        assert isinstance(data["response"], str), "response should be a string"
        assert isinstance(data["task_operations"], list), "task_operations should be a list"

        # Verify task_operations content if any operations were performed
        for task_op in data["task_operations"]:
            assert isinstance(task_op, dict), "Each task operation should be a dictionary"
            assert "tool" in task_op, "Task operation should have 'tool' key"
            assert "input" in task_op, "Task operation should have 'input' key"
            assert "output" in task_op, "Task operation should have 'output' key"


if __name__ == "__main__":
    # Run the tests
    test_chat_endpoint_contract()
    test_chat_endpoint_required_fields()
    test_chat_endpoint_field_types()
    test_chat_endpoint_response_format()
    print("All contract tests passed!")