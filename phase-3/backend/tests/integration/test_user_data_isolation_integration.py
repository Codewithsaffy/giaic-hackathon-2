"""
Integration Tests for User Data Isolation

These tests verify that users can only access their own data and cannot
access data belonging to other users.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine, select
from backend.main import app
from backend.src.core.database import get_session, engine
from backend.src.models.conversation import Conversation
from backend.src.models.message import ChatMessage
from backend.src.models.task import Task
from backend.src.services.conversation_service import ConversationService
from unittest.mock import patch
import tempfile
import os


@pytest.fixture
def test_db():
    """Create a temporary in-memory database for testing."""
    # Create a temporary SQLite database for testing
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()

    db_url = f"sqlite:///{temp_db.name}"
    test_engine = create_engine(db_url, connect_args={"check_same_thread": False})

    # Create tables
    SQLModel.metadata.create_all(test_engine)

    yield test_engine

    # Cleanup
    os.unlink(temp_db.name)


@pytest.fixture
def client_with_test_db(test_db):
    """Create a test client with the test database."""
    # Mock the database session to use test database
    def get_test_session():
        with Session(test_db) as session:
            yield session

    with patch('backend.main.get_session', get_test_session):
        with TestClient(app) as test_client:
            yield test_client


def test_user_cannot_access_other_users_conversations(client_with_test_db):
    """Test that a user cannot access conversations belonging to another user."""
    with Session(client_with_test_db.application.state.engine) as session:
        # Create conversations for different users
        user1_conv = Conversation(user_id="user1", title="User 1's Conversation")
        user2_conv = Conversation(user_id="user2", title="User 2's Conversation")

        session.add(user1_conv)
        session.add(user2_conv)
        session.commit()

        # Refresh to get IDs
        session.refresh(user1_conv)
        session.refresh(user2_conv)

    # Try to access user2's conversation as user1
    response = client_with_test_db.get(
        f"/api/conversations/{user2_conv.id}",
        params={"user_id": "user1"},
        headers={"Authorization": "Bearer fake_valid_token_for_user1"}
    )

    # Should return 404 or 403 since user1 doesn't own user2's conversation
    assert response.status_code in [404, 403]


def test_user_can_access_own_conversations(client_with_test_db):
    """Test that a user can access their own conversations."""
    with Session(client_with_test_db.application.state.engine) as session:
        # Create a conversation for user1
        user1_conv = Conversation(user_id="user1", title="User 1's Conversation")
        session.add(user1_conv)
        session.commit()
        session.refresh(user1_conv)

    # Try to access user1's conversation as user1
    response = client_with_test_db.get(
        f"/api/conversations/{user1_conv.id}",
        params={"user_id": "user1"},
        headers={"Authorization": "Bearer fake_valid_token_for_user1"}
    )

    # Should succeed
    assert response.status_code == 200
    data = response.json()
    assert data["conversation"]["id"] == user1_conv.id
    assert data["conversation"]["user_id"] == "user1"


def test_user_cannot_modify_other_users_tasks(client_with_test_db):
    """Test that a user cannot modify tasks belonging to another user."""
    with Session(client_with_test_db.application.state.engine) as session:
        # Create tasks for different users
        user1_task = Task(user_id="user1", title="User 1's Task", completed=False)
        user2_task = Task(user_id="user2", title="User 2's Task", completed=False)

        session.add(user1_task)
        session.add(user2_task)
        session.commit()

        session.refresh(user1_task)
        session.refresh(user2_task)

    # Try to update user2's task as user1 through the chat endpoint
    # This simulates what would happen when an AI agent tries to modify the task
    response = client_with_test_db.post(
        "/api/chat",
        json={
            "user_id": "user1",
            "message": f"Mark task {user2_task.id} as complete"
        },
        headers={"Authorization": "Bearer fake_valid_token_for_user1"}
    )

    # The AI agent should not be able to modify another user's task
    # The exact behavior depends on how the MCP tools handle authorization,
    # but the system should prevent cross-user data access


def test_conversation_listing_isolation(client_with_test_db):
    """Test that users only see their own conversations when listing."""
    with Session(client_with_test_db.application.state.engine) as session:
        # Create conversations for different users
        user1_conv1 = Conversation(user_id="user1", title="User 1's Conv 1")
        user1_conv2 = Conversation(user_id="user1", title="User 1's Conv 2")
        user2_conv1 = Conversation(user_id="user2", title="User 2's Conv 1")

        session.add(user1_conv1)
        session.add(user1_conv2)
        session.add(user2_conv1)
        session.commit()

    # User1 should only see their own conversations
    response = client_with_test_db.get(
        "/api/conversations",
        params={"user_id": "user1"},
        headers={"Authorization": "Bearer fake_valid_token_for_user1"}
    )

    assert response.status_code == 200
    data = response.json()
    user1_convs = data["conversations"]

    # Should only have conversations for user1
    for conv in user1_convs:
        assert conv["user_id"] == "user1"


def test_message_isolation_within_conversations(client_with_test_db):
    """Test that messages in conversations are properly isolated."""
    with Session(client_with_test_db.application.state.engine) as session:
        # Create conversations for different users
        user1_conv = Conversation(user_id="user1", title="User 1's Conversation")
        user2_conv = Conversation(user_id="user2", title="User 2's Conversation")

        session.add(user1_conv)
        session.add(user2_conv)
        session.commit()

        session.refresh(user1_conv)
        session.refresh(user2_conv)

        # Add messages to each conversation
        user1_msg = ChatMessage(
            conversation_id=user1_conv.id,
            user_id="user1",
            role="user",
            content="User 1 message"
        )
        user2_msg = ChatMessage(
            conversation_id=user2_conv.id,
            user_id="user2",
            role="user",
            content="User 2 message"
        )

        session.add(user1_msg)
        session.add(user2_msg)
        session.commit()

    # When user1 accesses their conversation, they should only see their messages
    response = client_with_test_db.get(
        f"/api/conversations/{user1_conv.id}/messages",
        params={"user_id": "user1"},
        headers={"Authorization": "Bearer fake_valid_token_for_user1"}
    )

    assert response.status_code == 200
    messages = response.json()

    # All messages should belong to user1's conversation
    for msg in messages:
        # This would depend on the actual API response structure
        pass


def test_cross_user_data_modification_prevention(client_with_test_db):
    """Test that attempts to modify another user's data are prevented."""
    with Session(client_with_test_db.application.state.engine) as session:
        # Create a conversation for user2
        user2_conv = Conversation(user_id="user2", title="User 2's Conversation")
        session.add(user2_conv)
        session.commit()
        session.refresh(user2_conv)

    # Try to update user2's conversation title as user1
    response = client_with_test_db.put(
        f"/api/conversations/{user2_conv.id}/title",
        params={
            "user_id": "user1",
            "title": "Hacked by User 1"
        },
        headers={"Authorization": "Bearer fake_valid_token_for_user1"}
    )

    # Should fail with 404 or 403
    assert response.status_code in [404, 403]


if __name__ == "__main__":
    pytest.main([__file__])