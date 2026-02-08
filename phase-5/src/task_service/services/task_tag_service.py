from uuid import UUID
from typing import List, Set

from sqlmodel import Session, select
from dapr.clients import DaprClient # Import DaprClient

from src.shared.models import Task
from src.shared.exceptions import NotFoundException, ConflictException
from src.task_service.events.task_events import publish_task_updated_event # Import the event publisher


class TaskTagService:
    def __init__(self, session: Session, dapr_client: DaprClient = None): # Inject DaprClient
        self.session = session
        self.dapr_client = dapr_client # Store DaprClient


    async def add_tags_to_task(self, task_id: UUID, user_id: UUID, new_tags: List[str]) -> Task:
        """
        Adds new tags to a task.
        """
        task = self.session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if not task:
            raise NotFoundException(detail=f"Task with id {task_id} not found for user {user_id}")

        existing_tags = set(task.tags)
        tags_to_add = set(t.strip().lower() for t in new_tags if t.strip())

        if not tags_to_add.difference(existing_tags):
            raise ConflictException(detail="All provided tags already exist on the task.")

        task.tags = sorted(list(existing_tags.union(tags_to_add)))
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        # Publish task_updated event
        await publish_task_updated_event(task, user_id, dapr_client=self.dapr_client)

        return task

    async def remove_tags_from_task(self, task_id: UUID, user_id: UUID, tags_to_remove: List[str]) -> Task:
        """
        Removes tags from a task.
        """
        task = self.session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if not task:
            raise NotFoundException(detail=f"Task with id {task_id} not found for user {user_id}")

        existing_tags = set(task.tags)
        tags_to_remove_set = set(t.strip().lower() for t in tags_to_remove if t.strip())

        if not tags_to_remove_set.intersection(existing_tags):
            raise ConflictException(detail="None of the provided tags exist on the task.")

        task.tags = sorted(list(existing_tags.difference(tags_to_remove_set)))
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        # Publish task_updated event
        await publish_task_updated_event(task, user_id, dapr_client=self.dapr_client)

        return task

    async def get_tasks_by_tag(self, user_id: UUID, tag: str) -> List[Task]:
        """
        Retrieves tasks filtered by a specific tag for a given user.
        Note: This requires a database that supports querying JSON/Array fields effectively.
        For simple cases, fetching all and filtering in Python might be necessary if DB support is limited.
        """
        # For a simple SQLModel setup without advanced JSON/Array column querying,
        # we might need to load all tasks and filter in Python.
        # For a more performant solution, consider a native database query or full-text search.
        all_user_tasks = self.session.exec(
            select(Task).where(Task.user_id == user_id)
        ).all()
        return [task for task in all_user_tasks if tag.lower() in [t.lower() for t in task.tags]]
