from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict

from pydantic import BaseModel, Field

from src.shared.models import Task


class EventBase(BaseModel):
    event_type: str = Field(..., description="Type of the event")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Time the event occurred")
    event_initiator: str = Field(..., description="Service that initiated the event")
    user_id: UUID = Field(..., description="ID of the user related to the event")


class TaskCreatedEvent(EventBase):
    event_type: str = "task_created"
    task_id: UUID
    task_details: Task # Full task details at creation


class TaskUpdatedEvent(EventBase):
    event_type: str = "task_updated"
    task_id: UUID
    updated_fields: Dict # Dictionary of updated fields and their new values


class ReminderTriggeredEvent(EventBase):
    event_type: str = "reminder_triggered"
    task_id: UUID
    reminder_message: str
    trigger_time: datetime


class RecurringTaskInstanceCreatedEvent(EventBase):
    event_type: str = "recurring_task_instance_created"
    original_recurring_task_id: UUID
    new_task_id: UUID
    new_task_details: Task # Details of the new instance created
