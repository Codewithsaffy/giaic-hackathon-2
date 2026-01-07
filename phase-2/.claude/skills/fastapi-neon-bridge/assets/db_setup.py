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


class UserBase(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(unique=True, min_length=5, max_length=100)
    age: Optional[int] = Field(default=None, ge=0, le=150)


class User(UserBase, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)


class UserCreate(UserBase):
    pass


class UserUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[str] = Field(default=None, unique=True, min_length=5, max_length=100)
    age: Optional[int] = Field(default=None, ge=0, le=150)


class UserPublic(UserBase):
    id: uuid.UUID


# Example CRUD operations - modify according to your needs
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)


async def create_user(session: AsyncSession, user: UserCreate) -> User:
    """Create a new user in the database."""
    try:
        db_user = User.model_validate(user)
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        logger.info(f"Successfully created user with ID: {db_user.id}")
        return db_user
    except IntegrityError as e:
        await session.rollback()
        logger.error(f"Integrity error creating user: {str(e)}")
        raise ValueError("User with this email already exists") from e
    except Exception as e:
        await session.rollback()
        logger.error(f"Unexpected error creating user: {str(e)}")
        raise


async def get_user_by_id(session: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
    """Get a user by ID."""
    try:
        from sqlmodel import select
        statement = select(User).where(User.id == user_id)
        result = await session.exec(statement)
        user = result.first()
        if user:
            logger.info(f"Retrieved user with ID: {user.id}")
        else:
            logger.info(f"User with ID {user_id} not found")
        return user
    except Exception as e:
        logger.error(f"Error retrieving user by ID {user_id}: {str(e)}")
        raise


async def get_users(session: AsyncSession, offset: int = 0, limit: int = 100) -> list[User]:
    """Get all users with pagination."""
    try:
        from sqlmodel import select
        statement = select(User).offset(offset).limit(limit)
        result = await session.exec(statement)
        users = result.fetchall()
        logger.info(f"Retrieved {len(users)} users with offset {offset} and limit {limit}")
        return users
    except Exception as e:
        logger.error(f"Error retrieving users: {str(e)}")
        raise


async def update_user(
    session: AsyncSession,
    user_id: uuid.UUID,
    user_update: UserUpdate
) -> Optional[User]:
    """Update a user by ID."""
    try:
        db_user = await get_user_by_id(session, user_id)
        if not db_user:
            logger.info(f"Attempt to update non-existent user with ID: {user_id}")
            return None

        user_data = user_update.model_dump(exclude_unset=True)
        db_user.sqlmodel_update(user_data)

        await session.commit()
        await session.refresh(db_user)
        logger.info(f"Successfully updated user with ID: {db_user.id}")
        return db_user
    except IntegrityError as e:
        await session.rollback()
        logger.error(f"Integrity error updating user {user_id}: {str(e)}")
        raise ValueError("Another user with this email already exists") from e
    except Exception as e:
        await session.rollback()
        logger.error(f"Unexpected error updating user {user_id}: {str(e)}")
        raise


async def delete_user(session: AsyncSession, user_id: uuid.UUID) -> bool:
    """Delete a user by ID."""
    try:
        db_user = await get_user_by_id(session, user_id)
        if not db_user:
            logger.info(f"Attempt to delete non-existent user with ID: {user_id}")
            return False

        await session.delete(db_user)
        await session.commit()
        logger.info(f"Successfully deleted user with ID: {user_id}")
        return True
    except Exception as e:
        await session.rollback()
        logger.error(f"Error deleting user {user_id}: {str(e)}")
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