from datetime import datetime
from enum import Enum
from typing import Optional, List, Any
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, JSON


class UUIDModel(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)


class TimeStampedModel(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, nullable=False, sa_column_kwargs={"onupdate": datetime.utcnow}
    )


class BaseSQLModel(UUIDModel, TimeStampedModel):
    """
    Base model for all SQLModel entities, providing UUID primary key and timestamps.
    """
    pass


class Priority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class TaskBase(SQLModel):
    description: str
    status: str = "pending"  # e.g., "pending", "completed", "archived"
    priority: Priority = Field(default=Priority.MEDIUM, description="Priority of the task")
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON), description="List of tags for the task")
    due_date: Optional[datetime] = Field(default=None, description="Due date and time for the task")
    recurrence_pattern: Optional[str] = Field(default=None, description="Pattern for recurring tasks")
    reminder_settings: Optional[dict] = Field(default=None, sa_column=Column(JSON), description="Settings for task reminders")


class Task(BaseSQLModel, TaskBase, table=True):
    __tablename__ = "tasks"

    user_id: UUID = Field(foreign_key="users.id", index=True)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="tasks")
    notifications: List["Notification"] = Relationship(back_populates="task")


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)


class User(BaseSQLModel, UserBase, table=True):
    __tablename__ = "users"

    tasks: List["Task"] = Relationship(back_populates="user")
    notifications: List["Notification"] = Relationship(back_populates="user")
    recurring_tasks: List["RecurringTask"] = Relationship(back_populates="user")


class RecurringTaskBase(SQLModel):
    description: str
    recurrence_pattern: str  # e.g., "daily", "weekly on Monday"
    priority: Priority = Field(default=Priority.MEDIUM)
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    next_run: Optional[datetime] = Field(default=None)
    status: str = "active" # e.g., "active", "paused", "deleted"


class RecurringTask(BaseSQLModel, RecurringTaskBase, table=True):
    __tablename__ = "recurring_tasks"

    user_id: UUID = Field(foreign_key="users.id", index=True)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="recurring_tasks")


class NotificationType(str, Enum):
    REMINDER = "reminder"
    SYSTEM_ALERT = "system_alert"
    INFO = "info"


class NotificationBase(SQLModel):
    message: str
    trigger_time: datetime
    sent_at: Optional[datetime] = None
    status: str = "pending"  # e.g., "pending", "sent", "failed", "cancelled"
    type: NotificationType = Field(default=NotificationType.REMINDER)


class Notification(BaseSQLModel, NotificationBase, table=True):
    __tablename__ = "notifications"

    user_id: UUID = Field(foreign_key="users.id", index=True)
    task_id: Optional[UUID] = Field(default=None, foreign_key="tasks.id", index=True)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="notifications")
    task: Optional["Task"] = Relationship(back_populates="notifications")


class EventPayload(SQLModel):
    """
    Base class for event payloads. Actual payloads will inherit from this or be specific dicts.
    """
    event_type: str


class Event(BaseSQLModel, table=False): # Event is not a table, it's a concept for Kafka
    type: str = Field(description="Describes the type of event (e.g., task_created, reminder_triggered)")
    payload: dict = Field(default_factory=dict, description="Contains the relevant data for the event")
    source_service: str = Field(description="The microservice that originated the event")
    version: int = Field(default=1, description="Schema version of the event payload")
