from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Optional
import uuid
import logging

from models import Task, TaskCreate, TaskUpdate

logger = logging.getLogger(__name__)

# Task CRUD operations
async def create_task(session: AsyncSession, task: TaskCreate, owner_id: str) -> Task:
    """Create a new task for a user."""
    try:
        db_task = Task.model_validate(task, update={"owner_id": owner_id})
        session.add(db_task)
        await session.commit()
        await session.refresh(db_task)
        logger.info(f"Successfully created task {db_task.id} for user {owner_id}")
        return db_task
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating task for user {owner_id}: {str(e)}")
        raise


async def get_task_by_id(session: AsyncSession, task_id: uuid.UUID, owner_id: str) -> Optional[Task]:
    """Get a task by ID ensuring it belongs to the owner."""
    try:
        statement = select(Task).where(Task.id == task_id, Task.owner_id == owner_id)
        result = await session.exec(statement)
        task = result.first()
        if task:
            logger.info(f"Retrieved task {task.id} for user {owner_id}")
        else:
            logger.info(f"Task {task_id} not found for user {owner_id}")
        return task
    except Exception as e:
        logger.error(f"Error retrieving task {task_id} for user {owner_id}: {str(e)}")
        raise


async def get_tasks_by_owner(session: AsyncSession, owner_id: str, offset: int = 0, limit: int = 100) -> List[Task]:
    """Get all tasks for a specific user with pagination."""
    try:
        statement = select(Task).where(Task.owner_id == owner_id).offset(offset).limit(limit)
        result = await session.exec(statement)
        tasks = result.fetchall()
        logger.info(f"Retrieved {len(tasks)} tasks for user {owner_id}")
        return tasks
    except Exception as e:
        logger.error(f"Error retrieving tasks for user {owner_id}: {str(e)}")
        raise


async def update_task(
    session: AsyncSession,
    task_id: uuid.UUID,
    task_update: TaskUpdate,
    owner_id: str
) -> Optional[Task]:
    """Update a task ensuring it belongs to the owner."""
    try:
        db_task = await get_task_by_id(session, task_id, owner_id)
        if not db_task:
            return None

        user_data = task_update.model_dump(exclude_unset=True)
        db_task.sqlmodel_update(user_data)

        await session.commit()
        await session.refresh(db_task)
        logger.info(f"Successfully updated task {db_task.id} for user {owner_id}")
        return db_task
    except Exception as e:
        await session.rollback()
        logger.error(f"Error updating task {task_id} for user {owner_id}: {str(e)}")
        raise


async def delete_task(session: AsyncSession, task_id: uuid.UUID, owner_id: str) -> bool:
    """Delete a task ensuring it belongs to the owner."""
    try:
        db_task = await get_task_by_id(session, task_id, owner_id)
        if not db_task:
            return False

        await session.delete(db_task)
        await session.commit()
        logger.info(f"Successfully deleted task {task_id} for user {owner_id}")
        return True
    except Exception as e:
        await session.rollback()
        logger.error(f"Error deleting task {task_id} for user {owner_id}: {str(e)}")
        raise