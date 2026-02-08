import re
import logging
import httpx
from uuid import UUID
from datetime import datetime, timedelta
from typing import Optional, Dict

from sqlmodel import Session, select
from dapr.clients import DaprClient

from src.shared.models import Task
from src.shared.exceptions import NotFoundException, ConflictException

logger = logging.getLogger(__name__)

class TaskDueReminderService:
    def __init__(self, session: Session, dapr_client: DaprClient = None):
        self.session = session
        self.dapr_client = dapr_client

    async def set_due_date_and_reminder(
        self,
        task_id: UUID,
        user_id: UUID,
        due_date: datetime,
        reminder_offset: Optional[str] = None,
    ) -> Task:
        """
        Sets the due date and reminder settings for a given task.
        """
        task = self.session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if not task:
            raise NotFoundException(detail=f"Task with id {task_id} not found for user {user_id}")

        if due_date < datetime.utcnow():
            raise ConflictException(detail="Due date cannot be in the past.")

        task.due_date = due_date
        task.reminder_settings = self._parse_reminder_offset(due_date, reminder_offset) if reminder_offset else None

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        if task.reminder_settings:
            # Schedule via Dapr Jobs API
            reminder_trigger_time_str = task.reminder_settings.get("trigger_time")
            if reminder_trigger_time_str:
                job_name = f"reminder-task-{task.id}"
                # Dapr Jobs API (alpha1) HTTP endpoint
                dapr_jobs_url = "http://localhost:3500/v1.0-alpha1/jobs"
                
                payload = {
                    "dueTime": reminder_trigger_time_str, # ISO format
                    "data": {
                        "task_id": str(task.id),
                        "user_id": str(user_id),
                        "type": "reminder",
                        "message": f"Reminder: {task.description}"
                    }
                }
                
                try:
                    async with httpx.AsyncClient() as client:
                        resp = await client.post(f"{dapr_jobs_url}/{job_name}", json=payload)
                        if resp.status_code >= 400:
                            logger.error(f"Failed to schedule reminder job: {resp.text}")
                        else:
                            logger.info(f"Successfully scheduled reminder job {job_name}")
                except Exception as e:
                    logger.error(f"Error calling Dapr Jobs API: {str(e)}")

        return task

    def _parse_reminder_offset(self, due_date: datetime, offset_str: str) -> Dict[str, str]:
        """
        Parses a human-readable reminder offset string and returns reminder settings.
        """
        offset_str = offset_str.lower()
        reminder_time = due_date

        if "at due time" in offset_str:
            pass # Reminder is at the due date
        elif "minute before" in offset_str:
            minutes_match = re.search(r"(\d+)\s+minute", offset_str)
            if minutes_match:
                minutes = int(minutes_match.group(1))
                reminder_time = due_date - timedelta(minutes=minutes)
        elif "hour before" in offset_str:
            hours_match = re.search(r"(\d+)\s+hour", offset_str)
            if hours_match:
                hours = int(hours_match.group(1))
                reminder_time = due_date - timedelta(hours=hours)
        elif "day before" in offset_str:
            days_match = re.search(r"(\d+)\s+day", offset_str)
            if days_match:
                days = int(days_match.group(1))
                reminder_time = due_date - timedelta(days=days)

        return {"trigger_time": reminder_time.isoformat(), "method": "notification"}
