from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker
from sqlalchemy.pool import NullPool
import os
import uuid


# Neon database URL format
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://username:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require"
)

# Create async engine with Neon-specific settings
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Neon works best with NullPool for serverless
    echo=False,  # Set to True for debugging
    isolation_level="AUTOCOMMIT"  # Recommended for Neon serverless
)

# Create async session maker
AsyncSessionFactory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to provide database session for FastAPI routes.

    Usage in FastAPI routes:
    ```
    from fastapi import Depends

    @app.get("/users/")
    async def get_users(session: AsyncSession = Depends(get_session)):
        # Your route logic here
        pass
    ```
    """
    async with AsyncSessionFactory() as session:
        yield session


# Example model definitions - modify according to your needs
from sqlmodel import SQLModel, Field
from typing import Optional
import uuid
from datetime import datetime
from pydantic import BaseModel


class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)


class Task(TaskBase, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: str = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = Field(default=None)


class TaskPublic(TaskBase):
    id: uuid.UUID
    owner_id: str
    created_at: datetime
    updated_at: datetime


# Example CRUD operations - modify according to your needs
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)


async def create_task(session: AsyncSession, task: TaskCreate, owner_id: str) -> Task:
    """Create a new task in the database."""
    try:
        db_task = Task.model_validate(task)
        db_task.owner_id = owner_id
        session.add(db_task)
        await session.commit()
        await session.refresh(db_task)
        logger.info(f"Successfully created task with ID: {db_task.id}")
        return db_task
    except IntegrityError as e:
        await session.rollback()
        logger.error(f"Integrity error creating task: {str(e)}")
        raise ValueError("Error creating task") from e
    except Exception as e:
        await session.rollback()
        logger.error(f"Unexpected error creating task: {str(e)}")
        raise


async def get_task_by_id(session: AsyncSession, task_id: uuid.UUID) -> Optional[Task]:
    """Get a task by ID."""
    try:
        from sqlmodel import select
        statement = select(Task).where(Task.id == task_id)
        result = await session.exec(statement)
        task = result.first()
        if task:
            logger.info(f"Retrieved task with ID: {task.id}")
        else:
            logger.info(f"Task with ID {task_id} not found")
        return task
    except Exception as e:
        logger.error(f"Error retrieving task by ID {task_id}: {str(e)}")
        raise


async def get_tasks_by_user(session: AsyncSession, user_id: str, offset: int = 0, limit: int = 100) -> list[Task]:
    """Get all tasks for a specific user with pagination."""
    try:
        from sqlmodel import select
        statement = select(Task).where(Task.owner_id == user_id).offset(offset).limit(limit)
        result = await session.exec(statement)
        tasks = result.fetchall()
        logger.info(f"Retrieved {len(tasks)} tasks for user {user_id} with offset {offset} and limit {limit}")
        return tasks
    except Exception as e:
        logger.error(f"Error retrieving tasks for user {user_id}: {str(e)}")
        raise


async def update_task(
    session: AsyncSession,
    task_id: uuid.UUID,
    task_update: TaskUpdate
) -> Optional[Task]:
    """Update a task by ID."""
    try:
        db_task = await get_task_by_id(session, task_id)
        if not db_task:
            logger.info(f"Attempt to update non-existent task with ID: {task_id}")
            return None

        task_data = task_update.model_dump(exclude_unset=True)
        db_task.sqlmodel_update(task_data)

        await session.commit()
        await session.refresh(db_task)
        logger.info(f"Successfully updated task with ID: {db_task.id}")
        return db_task
    except IntegrityError as e:
        await session.rollback()
        logger.error(f"Integrity error updating task {task_id}: {str(e)}")
        raise ValueError("Error updating task") from e
    except Exception as e:
        await session.rollback()
        logger.error(f"Unexpected error updating task {task_id}: {str(e)}")
        raise


async def delete_task(session: AsyncSession, task_id: uuid.UUID) -> bool:
    """Delete a task by ID."""
    try:
        db_task = await get_task_by_id(session, task_id)
        if not db_task:
            logger.info(f"Attempt to delete non-existent task with ID: {task_id}")
            return False

        await session.delete(db_task)
        await session.commit()
        logger.info(f"Successfully deleted task with ID: {task_id}")
        return True
    except Exception as e:
        await session.rollback()
        logger.error(f"Error deleting task {task_id}: {str(e)}")
        raise


if __name__ == "__main__":
    # Example usage for testing
    import asyncio

    async def test_connection():
        print("Testing database connection...")
        async with AsyncSessionFactory() as session:
            print("Connection successful!")

    # Uncomment to test connection
    # asyncio.run(test_connection())