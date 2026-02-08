from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Optional
import logging

from models import Task, TaskCreate, TaskUpdate

logger = logging.getLogger(__name__)

# Task CRUD operations
async def create_task(session: AsyncSession, task: TaskCreate, user_id: str) -> Task:
    """Create a new task for a user."""
    try:
        # Explicitly set user_id from the argument
        db_task = Task.model_validate(task, update={"user_id": user_id})
        session.add(db_task)
        await session.commit()
        await session.refresh(db_task)
        logger.info(f"Successfully created task {db_task.id} for user {user_id}")
        return db_task
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating task for user {user_id}: {str(e)}")
        raise

async def get_task_by_id(session: AsyncSession, task_id: int, user_id: str) -> Optional[Task]:
    """Get a task by ID ensuring it belongs to the user."""
    try:
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.exec(statement)
        task = result.first()
        return task
    except Exception as e:
        logger.error(f"Error retrieving task {task_id} for user {user_id}: {str(e)}")
        raise

async def get_tasks_by_user(session: AsyncSession, user_id: str, offset: int = 0, limit: int = 100) -> List[Task]:
    """Get all tasks for a specific user with pagination."""
    try:
        statement = select(Task).where(Task.user_id == user_id).offset(offset).limit(limit)
        result = await session.exec(statement)
        tasks = result.fetchall()
        return tasks
    except Exception as e:
        logger.error(f"Error retrieving tasks for user {user_id}: {str(e)}")
        raise

async def update_task(
    session: AsyncSession,
    task_id: int,
    task_update: TaskUpdate,
    user_id: str
) -> Optional[Task]:
    """Update a task ensuring it belongs to the user."""
    try:
        db_task = await get_task_by_id(session, task_id, user_id)
        if not db_task:
            return None

        user_data = task_update.model_dump(exclude_unset=True)
        db_task.sqlmodel_update(user_data)

        await session.commit()
        await session.refresh(db_task)
        return db_task
    except Exception as e:
        await session.rollback()
        logger.error(f"Error updating task {task_id} for user {user_id}: {str(e)}")
        raise

async def delete_task(session: AsyncSession, task_id: int, user_id: str) -> bool:
    """Delete a task ensuring it belongs to the user."""
    try:
        db_task = await get_task_by_id(session, task_id, user_id)
        if not db_task:
            return False

        await session.delete(db_task)
        await session.commit()
        return True
    except Exception as e:
        await session.rollback()
        logger.error(f"Error deleting task {task_id} for user {user_id}: {str(e)}")
        raise