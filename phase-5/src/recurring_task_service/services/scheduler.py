import httpx
from uuid import UUID
from datetime import datetime
import json
import logging

from src.shared.models import RecurringTask
from src.shared.exceptions import ConflictException

logger = logging.getLogger(__name__)

DAPR_JOBS_URL = "http://localhost:3500/v1.0-alpha1/jobs"

class RecurringTaskScheduler:
    def __init__(self, dapr_invoker=None):
        self.dapr_invoker = dapr_invoker

    async def schedule_recurring_task(self, task: RecurringTask):
        """
        Schedules a recurring task using Dapr Jobs API (alpha1).
        """
        if not task.recurrence_pattern:
            raise ValueError("Task must have a recurrence_pattern to be scheduled.")

        job_name = f"recurring-task-{task.id}"
        logger.info(f"Scheduling job {job_name} with pattern: {task.recurrence_pattern}")

        # The Jobs API expects a JSON payload
        # For recurring tasks, we use 'schedule' field (cron format)
        payload = {
            "schedule": task.recurrence_pattern,
            "data": {
                "id": str(task.id),
                "type": "recurring_task",
                "description": task.description,
                "user_id": str(task.user_id)
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{DAPR_JOBS_URL}/{job_name}", json=payload)
                if response.status_code >= 400:
                    logger.error(f"Failed to schedule job via Dapr: {response.text}")
                    raise ConflictException(detail=f"Dapr Jobs API error: {response.text}")
                logger.info(f"Successfully scheduled job {job_name}")
        except Exception as e:
            logger.error(f"Exception while scheduling job: {str(e)}")
            raise ConflictException(detail=f"Failed to schedule recurring task: {str(e)}")

    async def unschedule_recurring_task(self, task_id: UUID):
        """
        Unschedules a recurring task using Dapr Jobs API.
        """
        job_name = f"recurring-task-{task_id}"
        logger.info(f"Unscheduling job {job_name}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(f"{DAPR_JOBS_URL}/{job_name}")
                if response.status_code == 404:
                    logger.warning(f"Job {job_name} not found in Dapr Jobs store.")
                elif response.status_code >= 400:
                    logger.error(f"Failed to unschedule job via Dapr: {response.text}")
                else:
                    logger.info(f"Successfully unscheduled job {job_name}")
        except Exception as e:
            logger.error(f"Exception while unscheduling job: {str(e)}")
