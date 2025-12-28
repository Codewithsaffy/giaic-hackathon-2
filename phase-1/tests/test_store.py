import pytest
from src.models import Task
from src.store import TaskStore


class TestTaskStore:
    """Tests for the TaskStore class."""

    def setup_method(self):
        """Reset the singleton instance before each test."""
        # Get the singleton instance and reset its state
        self.store = TaskStore()
        # Clear all tasks and reset the ID counter by creating a fresh instance
        self.store._tasks = []
        self.store._next_id = 1

    def test_create_task_success(self):
        """Test creating a task successfully."""
        task = self.store.create_task("Test Title", "Test Description")

        assert isinstance(task, Task)
        assert task.id == 1
        assert task.title == "Test Title"
        assert task.description == "Test Description"
        assert task.status is False

    def test_create_task_without_description(self):
        """Test creating a task without providing a description."""
        task = self.store.create_task("Test Title")

        assert isinstance(task, Task)
        assert task.id == 1
        assert task.title == "Test Title"
        assert task.description == ""
        assert task.status is False

    def test_create_task_empty_title_fails(self):
        """Test that creating a task with empty title raises ValueError."""
        with pytest.raises(ValueError, match="Title must be provided and not empty"):
            self.store.create_task("", "Test Description")

    def test_create_task_whitespace_title_fails(self):
        """Test that creating a task with whitespace-only title raises ValueError."""
        with pytest.raises(ValueError, match="Title must be provided and not empty"):
            self.store.create_task("   ", "Test Description")

    def test_get_all_tasks_initially_empty(self):
        """Test that initially get_all_tasks returns an empty list."""
        tasks = self.store.get_all_tasks()

        assert tasks == []
        assert len(tasks) == 0

    def test_get_all_tasks_after_creating_tasks(self):
        """Test that get_all_tasks returns all created tasks."""
        task1 = self.store.create_task("Task 1", "Description 1")
        task2 = self.store.create_task("Task 2", "Description 2")

        tasks = self.store.get_all_tasks()

        assert len(tasks) == 2
        assert task1 in tasks
        assert task2 in tasks
        # Verify that it returns a copy (not the internal list)
        assert tasks is not self.store._tasks

    def test_get_task_by_id_success(self):
        """Test getting a task by its ID."""
        created_task = self.store.create_task("Test Task", "Test Description")

        retrieved_task = self.store.get_task_by_id(created_task.id)

        assert retrieved_task.id == created_task.id
        assert retrieved_task.title == created_task.title
        assert retrieved_task.description == created_task.description
        assert retrieved_task.status == created_task.status

    def test_get_task_by_id_not_found_raises_error(self):
        """Test that getting a non-existent task ID raises ValueError."""
        with pytest.raises(ValueError, match="Task with ID 999 does not exist"):
            self.store.get_task_by_id(999)

    def test_update_task_title_success(self):
        """Test updating a task's title."""
        original_task = self.store.create_task("Original Title", "Original Description")

        updated_task = self.store.update_task(original_task.id, title="Updated Title")

        assert updated_task.id == original_task.id
        assert updated_task.title == "Updated Title"
        assert updated_task.description == "Original Description"
        assert updated_task.status == original_task.status

    def test_update_task_description_success(self):
        """Test updating a task's description."""
        original_task = self.store.create_task("Original Title", "Original Description")

        updated_task = self.store.update_task(original_task.id, description="Updated Description")

        assert updated_task.id == original_task.id
        assert updated_task.title == "Original Title"
        assert updated_task.description == "Updated Description"
        assert updated_task.status == original_task.status

    def test_update_task_title_and_description_success(self):
        """Test updating both title and description."""
        original_task = self.store.create_task("Original Title", "Original Description")

        updated_task = self.store.update_task(
            original_task.id,
            title="Updated Title",
            description="Updated Description"
        )

        assert updated_task.id == original_task.id
        assert updated_task.title == "Updated Title"
        assert updated_task.description == "Updated Description"
        assert updated_task.status == original_task.status

    def test_update_task_empty_title_fails(self):
        """Test that updating with empty title raises ValueError."""
        original_task = self.store.create_task("Original Title", "Original Description")

        with pytest.raises(ValueError, match="Title cannot be empty"):
            self.store.update_task(original_task.id, title="")

    def test_toggle_task_status(self):
        """Test toggling task status."""
        task = self.store.create_task("Test Task", "Test Description")
        # Initially False
        assert task.status is False

        toggled_task = self.store.toggle_task_status(task.id)
        # Should now be True
        assert toggled_task.status is True

        # Toggle again to False
        toggled_task2 = self.store.toggle_task_status(task.id)
        assert toggled_task2.status is False

    def test_delete_task_success(self):
        """Test deleting a task successfully."""
        task = self.store.create_task("Test Task", "Test Description")

        result = self.store.delete_task(task.id)

        assert result is True
        assert len(self.store.get_all_tasks()) == 0

    def test_delete_task_not_found_raises_error(self):
        """Test that deleting a non-existent task ID raises ValueError."""
        with pytest.raises(ValueError, match="Task with ID 999 does not exist"):
            self.store.delete_task(999)