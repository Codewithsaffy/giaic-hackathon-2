from sqlmodel import SQLModel, Field
from typing import Optional
import uuid
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr


class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    completed: bool = Field(default=False)


class Task(TaskBase, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    owner_id: str = Field(index=True)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    completed: Optional[bool] = Field(default=None)


class TaskPublic(TaskBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    owner_id: str

# Define Session model for opaque token validation
class Session(SQLModel, table=True):
    id: str = Field(primary_key=True)
    userId: str
    token: str
    expiresAt: datetime
    ipAddress: Optional[str] = None
    userAgent: Optional[str] = None