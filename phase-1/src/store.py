from typing import List, Optional

try:
    from .models import Task
except ImportError:
    from models import Task


class TaskStore:
    """
    In-memory list storage with CRUD methods for Task objects.

    Implements the TaskStore (In-Memory) operations as specified in data-model.md:
    - create_task(title: str, description: str) -> Task
    - get_all_tasks() -> List[Task]
    - get_task_by_id(task_id: int) -> Task
    - update_task(task_id: int, title: str = None, description: str = None) -> Task
    - toggle_task_status(task_id: int) -> Task
    - delete_task(task_id: int) -> bool
    """

    _instance = None

    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Initialize instance attributes only once
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the in-memory task storage if not already initialized."""
        if not self._initialized:
            self._tasks: List[Task] = []
            self._next_id: int = 1
            self._initialized = True

    def create_task(self, title: str, description: str = "") -> Task:
        """
        Creates a new task with unique ID and incomplete status.

        Args:
            title (str): Task title (must be non-empty)
            description (str): Task description (optional)

        Returns:
            Task: The created Task object with unique ID and incomplete status

        Raises:
            ValueError: If title is empty
        """
        if not title or not title.strip():
            raise ValueError("Title must be provided and not empty")

        task = Task(
            id=self._next_id,
            title=title.strip(),
            description=description,
            status=False  # New tasks are incomplete by default
        )

        self._tasks.append(task)
        self._next_id += 1

        return task

    def get_all_tasks(self) -> List[Task]:
        """
        Returns all tasks in the store.

        Returns:
            List[Task]: List of all Task objects in the store
        """
        return self._tasks.copy()  # Return a copy to prevent external modification

    def get_task_by_id(self, task_id: int) -> Task:
        """
        Retrieves a specific task by ID.

        Args:
            task_id (int): The ID of the task to retrieve

        Returns:
            Task: The Task object with matching ID

        Raises:
            ValueError: If task with task_id does not exist
        """
        for task in self._tasks:
            if task.id == task_id:
                return task

        raise ValueError(f"Task with ID {task_id} does not exist")

    def update_task(self, task_id: int, title: str = None, description: str = None) -> Task:
        """
        Updates task details.

        Args:
            task_id (int): The ID of the task to update
            title (str, optional): New title (if provided, must be non-empty)
            description (str, optional): New description

        Returns:
            Task: The updated Task object

        Raises:
            ValueError: If task with task_id does not exist, or if title is provided but is empty
        """
        task = self.get_task_by_id(task_id)

        # Validate new title if provided
        if title is not None:
            title = title.strip()
            if not title:
                raise ValueError("Title cannot be empty")
            task.title = title

        # Update description if provided
        if description is not None:
            task.description = description

        return task

    def toggle_task_status(self, task_id: int) -> Task:
        """
        Toggles the completion status of a task.

        Args:
            task_id (int): The ID of the task to toggle

        Returns:
            Task: The Task object with toggled status

        Raises:
            ValueError: If task with task_id does not exist
        """
        task = self.get_task_by_id(task_id)
        task.status = not task.status
        return task

    def delete_task(self, task_id: int) -> bool:
        """
        Removes a task from the store.

        Args:
            task_id (int): The ID of the task to delete

        Returns:
            bool: True if task was deleted, False if task did not exist

        Raises:
            ValueError: If task with task_id does not exist
        """
        for i, task in enumerate(self._tasks):
            if task.id == task_id:
                del self._tasks[i]
                return True

        raise ValueError(f"Task with ID {task_id} does not exist")


# Create a singleton instance
task_store = TaskStore()