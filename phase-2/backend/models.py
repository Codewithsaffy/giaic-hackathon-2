from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

# --------------------------
# Better Auth Tables
# --------------------------

class User(SQLModel, table=True):
    __tablename__ = "user"
    id: str = Field(primary_key=True)
    name: str
    email: str = Field(index=True)
    emailVerified: bool
    image: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime


class Session(SQLModel, table=True):
    __tablename__ = "session"
    id: str = Field(primary_key=True)
    expiresAt: datetime
    token: str = Field(unique=True, index=True)
    createdAt: datetime
    updatedAt: datetime
    ipAddress: Optional[str] = None
    userAgent: Optional[str] = None
    userId: str = Field(index=True)


class Account(SQLModel, table=True):
    __tablename__ = "account"
    id: str = Field(primary_key=True)
    accountId: str
    providerId: str
    userId: str = Field(index=True)
    accessToken: Optional[str] = None
    refreshToken: Optional[str] = None
    idToken: Optional[str] = None
    accessTokenExpiresAt: Optional[datetime] = None
    refreshTokenExpiresAt: Optional[datetime] = None
    scope: Optional[str] = None
    password: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime


class Verification(SQLModel, table=True):
    __tablename__ = "verification"
    id: str = Field(primary_key=True)
    identifier: str
    value: str
    expiresAt: datetime
    createdAt: datetime
    updatedAt: Optional[datetime] = None


# --------------------------
# Application Tables
# --------------------------

# Shared properties
class TaskBase(SQLModel):
    title: str = Field(index=True)
    description: Optional[str] = None
    completed: bool = False

# Properties to receive on task creation
class TaskCreate(TaskBase):
    pass

# Properties to receive on task update
class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

# Database Model
class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Links to User.id (Better Auth)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Properties to return to client
class TaskPublic(TaskBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
