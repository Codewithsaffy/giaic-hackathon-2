from typing import List, Optional
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

try:
    from .models import Task, Priority
except ImportError:
    from models import Task, Priority


class TaskStore:
    """
    JSON file storage with CRUD methods and advanced features for Task objects.

    Features:
    - Auto-save/load from JSON file
    - Search and filter capabilities
    - Sorting options
    - Statistics and analytics
    """

    _instance = None

    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the task storage with JSON persistence."""
        if not self._initialized:
            self._tasks: List[Task] = []
            self._next_id: int = 1
            
            # Setup storage directory and file
            self._storage_dir = Path.home() / ".todo"
            self._storage_file = self._storage_dir / "tasks.json"
            
            # Create directory if it doesn't exist
            self._storage_dir.mkdir(exist_ok=True)
            
            # Load existing tasks
            self._load()
            
            self._initialized = True

    def _save(self) -> None:
        """Save all tasks to JSON file."""
        try:
            data = {
                "next_id": self._next_id,
                "tasks": [task.to_dict() for task in self._tasks]
            }
            
            with open(self._storage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving tasks: {e}")

    def _load(self) -> None:
        """Load tasks from JSON file."""
        try:
            if self._storage_file.exists():
                with open(self._storage_file, 'r') as f:
                    data = json.load(f)
                
                self._next_id = data.get("next_id", 1)
                self._tasks = [Task.from_dict(task_data) for task_data in data.get("tasks", [])]
        except Exception as e:
            print(f"Error loading tasks: {e}")
            self._tasks = []
            self._next_id = 1

    def create_task(
        self, 
        title: str, 
        description: str = "",
        priority: Priority = Priority.MEDIUM,
        due_date: Optional[datetime] = None,
        category: str = "General",
        tags: List[str] = None
    ) -> Task:
        """
        Creates a new task with enhanced attributes.

        Args:
            title (str): Task title (must be non-empty)
            description (str): Task description (optional)
            priority (Priority): Task priority level
            due_date (Optional[datetime]): Due date for the task
            category (str): Category for organization
            tags (List[str]): Tags for additional organization

        Returns:
            Task: The created Task object

        Raises:
            ValueError: If title is empty
        """
        if not title or not title.strip():
            raise ValueError("Title must be provided and not empty")

        task = Task(
            id=self._next_id,
            title=title.strip(),
            description=description,
            status=False,
            priority=priority,
            due_date=due_date,
            category=category,
            tags=tags if tags else [],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self._tasks.append(task)
        self._next_id += 1
        self._save()

        return task

    def get_all_tasks(self) -> List[Task]:
        """Returns all tasks in the store."""
        return self._tasks.copy()

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

    def update_task(
        self, 
        task_id: int, 
        title: str = None, 
        description: str = None,
        priority: Priority = None,
        due_date: Optional[datetime] = None,
        category: str = None,
        tags: List[str] = None
    ) -> Task:
        """
        Updates task details.

        Args:
            task_id (int): The ID of the task to update
            title (str, optional): New title
            description (str, optional): New description
            priority (Priority, optional): New priority
            due_date (datetime, optional): New due date
            category (str, optional): New category
            tags (List[str], optional): New tags

        Returns:
            Task: The updated Task object

        Raises:
            ValueError: If task doesn't exist or title is empty
        """
        task = self.get_task_by_id(task_id)

        if title is not None:
            title = title.strip()
            if not title:
                raise ValueError("Title cannot be empty")
            task.title = title

        if description is not None:
            task.description = description

        if priority is not None:
            task.priority = priority

        if due_date is not None:
            task.due_date = due_date

        if category is not None:
            task.category = category

        if tags is not None:
            task.tags = tags

        task.updated_at = datetime.now()
        self._save()

        return task

    def toggle_task_status(self, task_id: int) -> Task:
        """Toggles the completion status of a task."""
        task = self.get_task_by_id(task_id)
        task.status = not task.status
        task.updated_at = datetime.now()
        self._save()
        return task

    def delete_task(self, task_id: int) -> bool:
        """Removes a task from the store."""
        for i, task in enumerate(self._tasks):
            if task.id == task_id:
                del self._tasks[i]
                self._save()
                return True

        raise ValueError(f"Task with ID {task_id} does not exist")

    # Search and Filter Methods

    def search_tasks(self, query: str) -> List[Task]:
        """Search tasks by title or description."""
        query = query.lower()
        return [
            task for task in self._tasks
            if query in task.title.lower() or query in task.description.lower()
        ]

    def filter_by_category(self, category: str) -> List[Task]:
        """Filter tasks by category."""
        return [task for task in self._tasks if task.category.lower() == category.lower()]

    def filter_by_priority(self, priority: Priority) -> List[Task]:
        """Filter tasks by priority."""
        return [task for task in self._tasks if task.priority == priority]

    def filter_by_status(self, completed: bool) -> List[Task]:
        """Filter tasks by completion status."""
        return [task for task in self._tasks if task.status == completed]

    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks."""
        return [task for task in self._tasks if task.is_overdue()]

    def get_upcoming_tasks(self, days: int = 7) -> List[Task]:
        """Get tasks due within specified days."""
        cutoff = datetime.now() + timedelta(days=days)
        return [
            task for task in self._tasks
            if task.due_date and not task.status and task.due_date <= cutoff
        ]

    # Sorting Methods

    def sort_by_priority(self, reverse: bool = True) -> List[Task]:
        """Sort tasks by priority (High -> Low by default)."""
        priority_order = {Priority.HIGH: 3, Priority.MEDIUM: 2, Priority.LOW: 1}
        return sorted(
            self._tasks,
            key=lambda t: priority_order[t.priority],
            reverse=reverse
        )

    def sort_by_due_date(self) -> List[Task]:
        """Sort tasks by due date (earliest first, None at end)."""
        with_due = [t for t in self._tasks if t.due_date is not None]
        without_due = [t for t in self._tasks if t.due_date is None]
        with_due.sort(key=lambda t: t.due_date)
        return with_due + without_due

    def sort_by_created_date(self, reverse: bool = True) -> List[Task]:
        """Sort tasks by creation date (newest first by default)."""
        return sorted(self._tasks, key=lambda t: t.created_at, reverse=reverse)

    # Statistics Methods

    def get_completion_stats(self) -> dict:
        """Get completion statistics."""
        total = len(self._tasks)
        completed = len([t for t in self._tasks if t.status])
        pending = total - completed
        percentage = (completed / total * 100) if total > 0 else 0

        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "percentage": percentage
        }

    def get_category_breakdown(self) -> dict:
        """Get task count by category."""
        breakdown = {}
        for task in self._tasks:
            category = task.category
            breakdown[category] = breakdown.get(category, 0) + 1
        return breakdown

    def get_priority_breakdown(self) -> dict:
        """Get task count by priority."""
        breakdown = {
            "high": len([t for t in self._tasks if t.priority == Priority.HIGH]),
            "medium": len([t for t in self._tasks if t.priority == Priority.MEDIUM]),
            "low": len([t for t in self._tasks if t.priority == Priority.LOW])
        }
        return breakdown


# Create a singleton instance
task_store = TaskStore()