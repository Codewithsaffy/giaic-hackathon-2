---
name: fastapi-neon-bridge
description: |
  This skill should be used when creating CRUD endpoints in FastAPI backed by Neon Postgres database using SQLModel. It enforces async patterns and proper dependency injection for database sessions.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# FastAPI-Neon Bridge Skill

This skill provides expert guidance for creating CRUD endpoints in FastAPI backed by Neon Postgres using SQLModel with proper async patterns and dependency injection.

## Skill Purpose

This skill helps configure and implement FastAPI CRUD endpoints with Neon Postgres database following these constraints:
- **Async Only:** All routes and DB calls must be `async/await`
- **Driver:** Must use `postgresql+asyncpg` in the connection string
- **Dependency:** Must use a `get_session` dependency for all routes

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing project structure, current database models, environment variables, existing API routes |
| **Conversation** | User's specific requirements for models, endpoints, validation, authentication |
| **Skill References** | Domain patterns from `assets/db_setup.py` and best practices |
| **User Guidelines** | Project-specific conventions, team standards, security requirements |

Ensure all required context is gathered before implementing.

## Neon Database Connection String Format

The correct format for Neon database connection string with asyncpg:
```
postgresql+asyncpg://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname?sslmode=require
```

## Implementation Patterns

### ✅ CORRECT: Async Database Setup with Neon

```python
# database.py
from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker
from sqlalchemy.pool import NullPool
import os

# Neon database URL format
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require")

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
    """Dependency to provide database session for FastAPI routes."""
    async with AsyncSessionFactory() as session:
        yield session
```

### ✅ CORRECT: Model Definition

```python
# models.py
from sqlmodel import SQLModel, Field
from typing import Optional
import uuid

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
```

### ✅ CORRECT: FastAPI CRUD Endpoints

```python
# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from contextlib import asynccontextmanager
import logging

from .database import get_session, engine
from .models import User, UserCreate, UserUpdate, UserPublic
from . import crud

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables on startup."""
    logger.info("Initializing database...")
    async with engine.begin() as conn:
        # Create all tables - only in development, consider migrations for production
        await conn.run_sync(SQLModel.metadata.create_all)
    logger.info("Database initialized.")
    yield
    # Cleanup on shutdown
    await engine.dispose()
    logger.info("Database disposed.")

app = FastAPI(lifespan=lifespan)

@app.post("/users/", response_model=UserPublic, status_code=201)
async def create_user(
    user: UserCreate,
    session: AsyncSession = Depends(get_session)
) -> UserPublic:
    """Create a new user."""
    try:
        db_user = await crud.create_user(session, user)
        logger.info(f"Created user with ID: {db_user.id}")
        return db_user
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/{user_id}", response_model=UserPublic)
async def get_user(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_session)
) -> UserPublic:
    """Get a user by ID."""
    db_user = await crud.get_user_by_id(session, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/users/", response_model=List[UserPublic])
async def get_users(
    session: AsyncSession = Depends(get_session),
    offset: int = 0,
    limit: int = 100
) -> List[UserPublic]:
    """Get all users with pagination."""
    users = await crud.get_users(session, offset=offset, limit=limit)
    return users

@app.put("/users/{user_id}", response_model=UserPublic)
async def update_user(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    session: AsyncSession = Depends(get_session)
) -> UserPublic:
    """Update a user by ID."""
    db_user = await crud.update_user(session, user_id, user_update)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"Updated user with ID: {db_user.id}")
    return db_user

@app.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_session)
) -> None:
    """Delete a user by ID."""
    success = await crud.delete_user(session, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"Deleted user with ID: {user_id}")
    return None
```

### ✅ CORRECT: CRUD Operations

```python
# crud.py
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound
from typing import List, Optional
import uuid
import logging

from .models import User, UserCreate, UserUpdate

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

async def get_users(session: AsyncSession, offset: int = 0, limit: int = 100) -> List[User]:
    """Get all users with pagination."""
    try:
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
```

### ❌ INCORRECT: Synchronous Approach

```python
# DON'T DO THIS - Synchronous approach violates async constraint
from sqlmodel import Session  # Wrong - not AsyncSession
from sqlmodel import create_engine  # Wrong - not create_async_engine

def get_session():  # Wrong - not async
    with Session(engine) as session:  # Wrong - not AsyncSession
        yield session

@app.get("/users/")
def get_users(session: Session = Depends(get_session)):  # Wrong - not async
    # This violates all constraints
    pass
```

### ❌ INCORRECT: Direct Database Calls

```python
# DON'T DO THIS - Direct DB calls without dependency
@app.get("/users/")
async def get_users():
    # Wrong - creating session directly instead of using dependency
    engine = create_async_engine(DATABASE_URL)
    async with AsyncSession(engine) as session:
        # This bypasses the dependency injection pattern
        pass
```

## Required Dependencies

Install the necessary packages:

```bash
pip install fastapi[all] sqlmodel sqlalchemy[asyncio] asyncpg python-multipart
# Or if using poetry
poetry add fastapi[all] sqlmodel sqlalchemy[asyncio] asyncpg python-multipart
```

## Environment Variables

Set up your environment variables:

```bash
# .env
DATABASE_URL=postgresql+asyncpg://username:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
```

## Testing Considerations

For testing, you can override the database dependency:

```python
# test_main.py
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock
from fastapi import FastAPI

from app.database import get_session
from app.main import app

@pytest.fixture
async def async_client():
    # Create a mock session for testing
    mock_session = AsyncMock()

    # Override the dependency
    async def override_get_session():
        yield mock_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    # Clean up
    app.dependency_overrides.clear()
```

## Security Considerations

1. **Connection Pooling**: Use appropriate connection pooling settings for Neon's serverless architecture
2. **SSL**: Always use `sslmode=require` for Neon connections
3. **Environment Variables**: Store database credentials in environment variables
4. **Input Validation**: Use Pydantic models for request validation
5. **SQL Injection**: SQLModel and SQLAlchemy protect against SQL injection when using parameterized queries

## Performance Tips

1. **NullPool**: Use `NullPool` for Neon serverless connections to avoid connection retention overhead
2. **Autocommit**: Consider using `AUTOCOMMIT` isolation level for Neon serverless
3. **Short-lived Connections**: Neon works best with short-lived connections
4. **Connection Lifecycle**: Always use the dependency injection pattern to ensure proper connection cleanup