from uuid import UUID
from typing import List, Optional

from sqlmodel import Session, select
from sqlalchemy import or_, and_

from src.shared.models import Task, Priority


class TaskQueryService:
    def __init__(self, session: Session):
        self.session = session

    async def search_and_filter_tasks(
        self,
        user_id: UUID,
        query: Optional[str] = None,
        priority: Optional[Priority] = None,
        tags: Optional[List[str]] = None,
        sort_by: Optional[str] = None, # e.g., "created_at", "due_date", "priority"
        sort_order: Optional[str] = "asc" # "asc" or "desc"
    ) -> List[Task]:
        """
        Searches, filters, and sorts tasks for a given user.
        """
        statement = select(Task).where(Task.user_id == user_id)

        if query:
            statement = statement.where(
                or_(
                    Task.description.ilike(f"%{query}%"),
                )
            )

        if priority:
            statement = statement.where(Task.priority == priority)

        if tags:
            # This is a basic way to query tags stored as a List[str] in PostgreSQL.
            # For more complex scenarios, consider full-text search or a separate many-to-many table.
            for tag in tags:
                statement = statement.where(Task.tags.contains([tag.lower()])) # Assumes tags are lowercased in DB

        # Apply sorting
        if sort_by:
            if sort_by == "created_at":
                order_column = Task.created_at
            elif sort_by == "due_date":
                order_column = Task.due_date
            elif sort_by == "priority":
                # Custom sorting for Priority Enum - will fetch all and sort in Python
                # For DB-level sorting, would need a CASE statement or equivalent
                pass
            else:
                order_column = Task.created_at # Default sort

            if sort_by != "priority": # Don't apply DB sorting if sorting by priority
                if sort_order == "desc":
                    statement = statement.order_by(order_column.desc())
                else:
                    statement = statement.order_by(order_column.asc())

        tasks = self.session.exec(statement).all()

        if sort_by == "priority":
            priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
            tasks.sort(key=lambda t: priority_order.get(t.priority, 99), reverse=(sort_order == "desc"))

        return tasks
