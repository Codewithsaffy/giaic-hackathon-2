import pytest
from src.models import Task


class TestTaskModel:
    """Tests for the Task dataclass."""

    def test_task_creation_with_valid_data(self):
        """Test creating a Task with valid data."""
        task = Task(id=1, title="Test Task", description="Test Description", status=False)

        assert task.id == 1
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.status is False

    def test_task_creation_defaults(self):
        """Test that Task has correct defaults."""
        task = Task(id=1, title="Test Task", description="Test Description")

        assert task.id == 1
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.status is False  # Should default to False

    def test_task_title_validation_non_empty(self):
        """Test that Task raises ValueError for empty title."""
        with pytest.raises(ValueError, match="Title must be provided and not empty"):
            Task(id=1, title="", description="Test Description")

    def test_task_title_validation_whitespace_only(self):
        """Test that Task raises ValueError for whitespace-only title."""
        with pytest.raises(ValueError, match="Title must be provided and not empty"):
            Task(id=1, title="   ", description="Test Description")

    def test_task_id_type_validation(self):
        """Test that Task raises TypeError for non-integer ID."""
        with pytest.raises(TypeError, match="ID must be an integer"):
            Task(id="1", title="Test Task", description="Test Description")

    def test_task_status_type_validation(self):
        """Test that Task raises TypeError for non-boolean status."""
        with pytest.raises(TypeError, match="Status must be a boolean"):
            Task(id=1, title="Test Task", description="Test Description", status="False")