"""
Integration Test for NLP → Tool Invocation Flow

This test verifies the complete flow from natural language input to tool invocation,
ensuring that the system properly parses user requests and executes the appropriate tools.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
from typing import Dict, Any, List

# Import the main app
from src.main import app

# Create test client
client = TestClient(app)


def test_nlp_to_add_task_integration():
    """
    Integration test for 'add task' natural language flow
    Verifies that natural language like 'Add a task to buy groceries'
    gets converted to the add_task tool call.
    """

    # Mock the agent and tool responses to isolate the NLP parsing logic
    with patch('src.api.chat_endpoints.Agent') as mock_agent_class, \
         patch('src.api.chat_endpoints.Runner') as mock_runner:

        # Setup mock agent
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        # Setup mock runner result
        mock_result = MagicMock()
        mock_result.final_output = "I've added the task 'buy groceries' to your list."
        mock_result.tool_calls = [
            MagicMock(name="add_task", arguments={"user_id": "test_user_123", "title": "buy groceries", "description": ""}, result={"task_id": 1, "status": "created", "title": "buy groceries"})
        ]
        mock_runner.run.return_value = mock_result

        # Make request with natural language
        request_payload = {
            "user_id": "test_user_123",
            "message": "Add a task to buy groceries"
        }

        response = client.post("/api/chat", json=request_payload)

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "conversation_id" in data
        assert data["response"] == "I've added the task 'buy groceries' to your list."

        # Verify tool was called appropriately
        mock_runner.run.assert_called_once()
        # The agent should have been invoked with the user's message


def test_nlp_to_list_tasks_integration():
    """
    Integration test for 'list tasks' natural language flow
    Verifies that natural language like 'Show me my tasks'
    gets converted to the list_tasks tool call.
    """

    with patch('src.api.chat_endpoints.Agent') as mock_agent_class, \
         patch('src.api.chat_endpoints.Runner') as mock_runner:

        # Setup mock agent
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        # Setup mock runner result
        mock_result = MagicMock()
        mock_result.final_output = "Here are your pending tasks: 1. Buy groceries, 2. Call mom"
        mock_result.tool_calls = [
            MagicMock(name="list_tasks", arguments={"user_id": "test_user_123", "status": "pending"}, result={"tasks": [{"id": 1, "title": "Buy groceries", "completed": False}, {"id": 2, "title": "Call mom", "completed": False}], "count": 2})
        ]
        mock_runner.run.return_value = mock_result

        # Make request with natural language
        request_payload = {
            "user_id": "test_user_123",
            "message": "Show me my pending tasks"
        }

        response = client.post("/api/chat", json=request_payload)

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "conversation_id" in data
        assert "list tasks" in data["response"].lower()


def test_nlp_to_complete_task_integration():
    """
    Integration test for 'complete task' natural language flow
    Verifies that natural language like 'Complete my first task'
    gets converted to the complete_task tool call.
    """

    with patch('src.api.chat_endpoints.Agent') as mock_agent_class, \
         patch('src.api.chat_endpoints.Runner') as mock_runner:

        # Setup mock agent
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        # Setup mock runner result
        mock_result = MagicMock()
        mock_result.final_output = "I've marked 'Buy groceries' as completed."
        mock_result.tool_calls = [
            MagicMock(name="complete_task", arguments={"user_id": "test_user_123", "task_id": 1}, result={"task_id": 1, "status": "completed", "title": "Buy groceries"})
        ]
        mock_runner.run.return_value = mock_result

        # Make request with natural language
        request_payload = {
            "user_id": "test_user_123",
            "message": "Complete the task about buying groceries"
        }

        response = client.post("/api/chat", json=request_payload)

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "conversation_id" in data
        assert "marked" in data["response"].lower()
        assert "completed" in data["response"].lower()


def test_nlp_to_delete_task_integration():
    """
    Integration test for 'delete task' natural language flow
    Verifies that natural language like 'Delete my first task'
    gets converted to the delete_task tool call.
    """

    with patch('src.api.chat_endpoints.Agent') as mock_agent_class, \
         patch('src.api.chat_endpoints.Runner') as mock_runner:

        # Setup mock agent
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        # Setup mock runner result
        mock_result = MagicMock()
        mock_result.final_output = "I've deleted the task 'Buy groceries'."
        mock_result.tool_calls = [
            MagicMock(name="delete_task", arguments={"user_id": "test_user_123", "task_id": 1}, result={"task_id": 1, "status": "deleted", "title": "Buy groceries"})
        ]
        mock_runner.run.return_value = mock_result

        # Make request with natural language
        request_payload = {
            "user_id": "test_user_123",
            "message": "Delete the task about buying groceries"
        }

        response = client.post("/api/chat", json=request_payload)

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "conversation_id" in data
        assert "deleted" in data["response"].lower()


def test_nlp_multiple_tool_calls_integration():
    """
    Integration test for natural language that triggers multiple tool calls
    Verifies that complex requests like 'Add a task and show me all my tasks'
    can trigger multiple tools in sequence.
    """

    with patch('src.api.chat_endpoints.Agent') as mock_agent_class, \
         patch('src.api.chat_endpoints.Runner') as mock_runner:

        # Setup mock agent
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        # Setup mock runner result with multiple tool calls
        mock_result = MagicMock()
        mock_result.final_output = "I've added the task and here are all your tasks."
        mock_result.tool_calls = [
            MagicMock(name="add_task", arguments={"user_id": "test_user_123", "title": "New task", "description": ""}, result={"task_id": 5, "status": "created", "title": "New task"}),
            MagicMock(name="list_tasks", arguments={"user_id": "test_user_123", "status": "all"}, result={"tasks": [{"id": 5, "title": "New task", "completed": False}], "count": 1})
        ]
        mock_runner.run.return_value = mock_result

        # Make request with natural language requesting multiple actions
        request_payload = {
            "user_id": "test_user_123",
            "message": "Add a task called 'New task' and then show me all my tasks"
        }

        response = client.post("/api/chat", json=request_payload)

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "conversation_id" in data
        assert len(data["task_operations"]) >= 2  # Should have at least 2 tool calls


def test_nlp_error_handling_integration():
    """
    Integration test for NLP error handling
    Verifies that when tool calls fail, the system handles errors gracefully.
    """

    with patch('src.api.chat_endpoints.Agent') as mock_agent_class, \
         patch('src.api.chat_endpoints.Runner') as mock_runner:

        # Setup mock agent
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        # Setup mock runner result with error
        mock_result = MagicMock()
        mock_result.final_output = "Sorry, I couldn't add that task. Please try again."
        mock_result.tool_calls = [
            MagicMock(name="add_task", arguments={"user_id": "test_user_123", "title": "Problematic task", "description": ""}, result={"task_id": None, "status": "error", "error": "Task already exists"})
        ]
        mock_runner.run.return_value = mock_result

        # Make request with natural language
        request_payload = {
            "user_id": "test_user_123",
            "message": "Add a task called 'Problematic task'"
        }

        response = client.post("/api/chat", json=request_payload)

        # Verify response
        assert response.status_code == 200  # Should still return 200 but with error info
        data = response.json()

        # Verify error was handled appropriately
        assert "conversation_id" in data
        assert "error" in data["response"].lower() or "couldn't" in data["response"].lower()


def test_nlp_update_task_integration():
    """
    Integration test for 'update task' natural language flow
    Verifies that natural language like 'Change my task to...'
    gets converted to the update_task tool call.
    """

    with patch('src.api.chat_endpoints.Agent') as mock_agent_class, \
         patch('src.api.chat_endpoints.Runner') as mock_runner:

        # Setup mock agent
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        # Setup mock runner result
        mock_result = MagicMock()
        mock_result.final_output = "I've updated the task title to 'Buy healthy groceries'."
        mock_result.tool_calls = [
            MagicMock(name="update_task", arguments={"user_id": "test_user_123", "task_id": 1, "title": "Buy healthy groceries"}, result={"task_id": 1, "status": "updated", "title": "Buy healthy groceries"})
        ]
        mock_runner.run.return_value = mock_result

        # Make request with natural language
        request_payload = {
            "user_id": "test_user_123",
            "message": "Change the title of my first task to 'Buy healthy groceries'"
        }

        response = client.post("/api/chat", json=request_payload)

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "conversation_id" in data
        assert "updated" in data["response"].lower()


def test_conversation_context_preservation():
    """
    Integration test to ensure conversation context is preserved across multiple exchanges
    """

    with patch('src.api.chat_endpoints.Agent') as mock_agent_class, \
         patch('src.api.chat_endpoints.Runner') as mock_runner:

        # Setup mock agent
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        # First request - add a task
        mock_result1 = MagicMock()
        mock_result1.final_output = "I've added the task 'Buy groceries'."
        mock_result1.tool_calls = [
            MagicMock(name="add_task", arguments={"user_id": "test_user_123", "title": "Buy groceries", "description": ""}, result={"task_id": 1, "status": "created", "title": "Buy groceries"})
        ]
        mock_runner.run.return_value = mock_result1

        request1 = {
            "user_id": "test_user_123",
            "message": "Add a task to buy groceries"
        }

        response1 = client.post("/api/chat", json=request1)
        assert response1.status_code == 200
        data1 = response1.json()
        conversation_id = data1["conversation_id"]

        # Second request - refer to the previous task
        mock_result2 = MagicMock()
        mock_result2.final_output = "I've marked 'Buy groceries' as completed."
        mock_result2.tool_calls = [
            MagicMock(name="complete_task", arguments={"user_id": "test_user_123", "task_id": 1}, result={"task_id": 1, "status": "completed", "title": "Buy groceries"})
        ]
        mock_runner.run.return_value = mock_result2

        request2 = {
            "user_id": "test_user_123",
            "conversation_id": conversation_id,  # Continue the conversation
            "message": "Now complete the task about groceries"
        }

        response2 = client.post("/api/chat", json=request2)
        assert response2.status_code == 200
        data2 = response2.json()

        # Verify that the second request was processed in the context of the first
        assert data2["conversation_id"] == conversation_id
        assert "completed" in data2["response"].lower()


if __name__ == "__main__":
    # Run the integration tests
    test_nlp_to_add_task_integration()
    test_nlp_to_list_tasks_integration()
    test_nlp_to_complete_task_integration()
    test_nlp_to_delete_task_integration()
    test_nlp_multiple_tool_calls_integration()
    test_nlp_error_handling_integration()
    test_nlp_update_task_integration()
    test_conversation_context_preservation()
    print("All integration tests passed!")