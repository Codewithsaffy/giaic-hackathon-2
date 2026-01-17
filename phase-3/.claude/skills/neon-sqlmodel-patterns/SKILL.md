---
name: neon-sqlmodel-patterns
description: Work with Neon Serverless PostgreSQL using SQLModel ORM. Use when defining models, writing queries, or managing database connections.
---

# Neon PostgreSQL + SQLModel

## Overview

Work with Neon Serverless PostgreSQL using SQLModel ORM. This skill provides patterns for connection setup, model definition, query optimization, and performance best practices when using Neon with SQLModel.

## Connection Setup

### 1. Async Connection Pooling
```python
# database.py
from sqlmodel import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
import asyncio

# Async engine for Neon PostgreSQL
DATABASE_URL = os.getenv("NEON_DATABASE_URL")

# Create async engine with connection pooling
async_engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    pool_size=20,  # Adjust based on your Neon plan
    max_overflow=30,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,  # Recycle connections every 5 minutes
)

# Session factory for async operations
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

async def get_async_session():
    async with AsyncSessionLocal() as session:
        yield session
```

### 2. Connection String from Environment
```python
# config.py
import os
from typing import Optional

class DatabaseConfig:
    DATABASE_URL: Optional[str] = os.getenv("NEON_DATABASE_URL")

    @classmethod
    def validate_connection_string(cls) -> bool:
        if not cls.DATABASE_URL:
            raise ValueError("NEON_DATABASE_URL environment variable is required")

        # Check for required connection parameters
        required_params = ["postgresql+asyncpg://", "user=", "password=", "host=", "port=", "dbname="]
        return all(param in cls.DATABASE_URL for param in required_params)
```

### 3. Health Check Endpoints
```python
# routers/health.py
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from sqlalchemy import text
from database import async_engine

router = APIRouter(tags=["health"])

@router.get("/health/db")
async def db_health_check():
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            await result.fetchone()

        return {
            "status": "healthy",
            "database": "Neon PostgreSQL",
            "connection": "successful"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")
```

### 4. Proper Connection Lifecycle
```python
# services/base_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from typing import AsyncGenerator

class BaseService:
    def __init__(self, session: AsyncSession):
        self.session = session

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Context manager for session handling with proper cleanup"""
        session = AsyncSessionLocal()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

## SQLModel Patterns

### 1. Pydantic-Based Models
```python
# models/user.py
from sqlmodel import SQLModel, Field, create_engine
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
from datetime import datetime

class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True)
    name: str = Field(min_length=1, max_length=100)
    is_active: bool = True

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "John Doe"
            }
        }

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class UserRead(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
```

### 2. Type Hints Throughout
```python
# services/user_service.py
from sqlmodel import select, Session
from typing import List, Optional, Union
from models.user import User, UserCreate, UserUpdate

class UserService:
    def __init__(self, session: Session):
        self.session = session

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user with type hints"""
        user = User(
            email=user_data.email,
            name=user_data.name,
            # Hash password before storing
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID with proper typing"""
        statement = select(User).where(User.id == user_id)
        result = await self.session.exec(statement)
        return result.first()

    async def list_users(
        self,
        offset: int = 0,
        limit: int = 100
    ) -> List[User]:
        """List users with typing and pagination"""
        statement = select(User).offset(offset).limit(limit)
        result = await self.session.exec(statement)
        return result.all()
```

### 3. Relationships with Foreign Keys
```python
# models/document.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
import uuid
from datetime import datetime

class DocumentBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    content: Optional[str] = None

class Document(DocumentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", ondelete="CASCADE", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to user
    user: "User" = Relationship(back_populates="documents")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "My Document",
                "content": "Document content here..."
            }
        }

# Update User model to include relationship
User.model_rebuild()  # This handles circular references

class User(UserBase, table=True):
    # ... (previous fields remain the same)
    documents: List["Document"] = Relationship(back_populates="user")
```

### 4. Migrations with Alembic
```python
# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from models import SQLModel
import os

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata
target_metadata = SQLModel.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = os.getenv("NEON_DATABASE_URL")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## Performance

### 1. Use Connection Pooling
```python
# config/database_config.py
from sqlalchemy.pool import QueuePool
import os

class DatabasePoolConfig:
    POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
    MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "30"))
    POOL_PRE_PING = os.getenv("DB_POOL_PRE_PING", "True").lower() == "true"
    POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "300"))  # seconds
    POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))   # seconds

# Apply these settings when creating the engine
async_engine = create_async_engine(
    DATABASE_URL,
    pool_size=DatabasePoolConfig.POOL_SIZE,
    max_overflow=DatabasePoolConfig.MAX_OVERFLOW,
    pool_pre_ping=DatabasePoolConfig.POOL_PRE_PING,
    pool_recycle=DatabasePoolConfig.POOL_RECYCLE,
    pool_timeout=DatabasePoolConfig.POOL_TIMEOUT,
)
```

### 2. Index Frequently Queried Fields
```sql
-- Create indexes for frequently queried fields
-- For the User table
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_user_created_at ON users(created_at);
CREATE INDEX idx_user_is_active ON users(is_active);

-- For the Document table
CREATE INDEX idx_document_user_id ON documents(user_id);
CREATE INDEX idx_document_created_at ON documents(created_at);
CREATE INDEX idx_document_title ON documents(title);
```

### 3. Batch Operations Where Possible
```python
# services/bulk_service.py
from sqlmodel import select
from typing import List
from models.document import Document

class BulkService:
    def __init__(self, session):
        self.session = session

    async def bulk_insert_documents(self, documents_data: List[dict]) -> List[Document]:
        """Efficiently insert multiple documents"""
        documents = [Document(**data) for data in documents_data]

        # Use bulk insert for better performance
        self.session.add_all(documents)
        await self.session.commit()

        # Refresh to get IDs
        for doc in documents:
            await self.session.refresh(doc)

        return documents

    async def bulk_update_documents(self, updates: List[dict]) -> int:
        """Bulk update documents efficiently"""
        updated_count = 0

        for update_data in updates:
            doc_id = update_data.pop('id')
            statement = select(Document).where(Document.id == doc_id)
            result = await self.session.exec(statement)
            doc = result.first()

            if doc:
                for key, value in update_data.items():
                    setattr(doc, key, value)
                updated_count += 1

        await self.session.commit()
        return updated_count
```

### 4. Proper Transaction Management
```python
# services/transaction_service.py
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager
from typing import AsyncGenerator

class TransactionService:
    def __init__(self, session):
        self.session = session

    @asynccontextmanager
    async def transaction_scope(self) -> AsyncGenerator[None, None]:
        """Context manager for transaction handling"""
        try:
            yield
            await self.session.commit()
        except SQLAlchemyError:
            await self.session.rollback()
            raise

    async def transfer_document_ownership(self, doc_id: uuid.UUID, new_user_id: uuid.UUID, old_user_id: uuid.UUID):
        """Example of transaction with multiple operations"""
        async with self.transaction_scope():
            # Update document ownership
            doc = await self.session.get(Document, doc_id)
            if not doc:
                raise ValueError("Document not found")

            if doc.user_id != old_user_id:
                raise ValueError("Document does not belong to user")

            doc.user_id = new_user_id
            await self.session.commit()
```

## Implementation Checklist

Before implementation, ensure:

| Check | Requirement |
|-------|-------------|
| **Async Connection Pooling** | Set up proper async engine with appropriate pool size for Neon |
| **Environment Variables** | Use NEON_DATABASE_URL with proper connection string format |
| **Health Checks** | Implement database health check endpoints |
| **Connection Lifecycle** | Proper session management with try/finally blocks |
| **SQLModel Models** | Use Pydantic-compatible models with proper type hints |
| **Relationships** | Define foreign keys and relationships correctly |
| **Alembic Migrations** | Set up proper migration configuration |
| **Performance Indexes** | Create indexes on frequently queried fields |
| **Bulk Operations** | Implement batch operations where appropriate |
| **Transaction Management** | Use proper transaction scope for multi-step operations |

## Common Performance Issues to Avoid

- ❌ Not using connection pooling (leads to connection exhaustion)
- ❌ Missing indexes on frequently queried fields (slow queries)
- ❌ Not managing transaction boundaries properly (deadlocks)
- ❌ Executing N+1 queries without proper joins
- ❌ Not using async/await properly (blocking operations)

This implementation provides efficient patterns for working with Neon PostgreSQL using SQLModel ORM with proper performance considerations and best practices.