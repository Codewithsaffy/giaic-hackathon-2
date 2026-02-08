from uuid import UUID
from typing import Optional, List

from sqlmodel import Session, select
from dapr.clients import DaprClient

from src.shared.models import Task, Priority
from src.shared.exceptions import NotFoundException, ConflictException
from src.task_service.events.task_events import publish_task_updated_event # Import the new event publisher


class TaskPriorityService:
    def __init__(self, session: Session, dapr_client: DaprClient = None):
        self.session = session
        self.dapr_client = dapr_client # Dapr client injected


    async def set_task_priority(self, task_id: UUID, user_id: UUID, new_priority: Priority) -> Task:
        """
        Sets the priority for a given task.
        """
        task = self.session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if not task:
            raise NotFoundException(detail=f"Task with id {task_id} not found for user {user_id}")

        if task.priority == new_priority:
            raise ConflictException(detail=f"Task priority is already set to {new_priority.value}")

        task.priority = new_priority
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        # Publish task_updated event
        await publish_task_updated_event(task, user_id, dapr_client=self.dapr_client) # Pass dapr_client

        return task

    async def get_tasks_by_priority(self, user_id: UUID, priority: Priority) -> List[Task]:
        """
        Retrieves tasks filtered by priority for a given user.
        """
        tasks = self.session.exec(
            select(Task).where(Task.user_id == user_id, Task.priority == priority)
        ).all()
        return tasks

    async def get_all_tasks_sorted_by_priority(self, user_id: UUID) -> List[Task]:
        """
        Retrieves all tasks for a user, sorted by priority (High -> Medium -> Low).
        """
        # SQLModel/SQLAlchemy doesn't have a direct way to order by Enum values naturally.
        # We'll fetch and sort in application for now, or use a custom CASE statement in a more complex query.
        # For simplicity, sorting in Python.
        tasks = self.session.exec(
            select(Task).where(Task.user_id == user_id)
        ).all()

        priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        tasks.sort(key=lambda t: priority_order.get(t.priority, 99))
        return tasks
