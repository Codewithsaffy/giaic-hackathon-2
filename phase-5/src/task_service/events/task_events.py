from uuid import UUID
from typing import Optional
import json
import logging
from datetime import datetime

from dapr.clients import DaprClient

from src.shared.models import Task
from src.shared.dapr_utils import DaprServiceInvoker

logger = logging.getLogger(__name__)

PUB_SUB_NAME = "pubsub-kafka" # Defined in deploy/dapr-components/kafka-pubsub.yaml
TASK_EVENTS_TOPIC = "task-events"
REMINDERS_TOPIC = "reminders"


async def publish_task_updated_event(
    task: Task,
    user_id: UUID,
    event_initiator: str = "task_service",
    dapr_client: DaprClient = None
):
    """
    Publishes a task_updated event to the task-events topic.
    """
    dapr_invoker = DaprServiceInvoker(dapr_client) # Use shared invoker
    event_payload = {
        "event_type": "task_updated",
        "task_id": str(task.id),
        "user_id": str(user_id),
        "updated_fields": json.loads(task.model_dump_json()), # Send the whole updated task for simplicity
        "event_initiator": event_initiator,
        "timestamp": datetime.utcnow().isoformat(),
    }
    await dapr_invoker.publish_event(
        pubsub_name=PUB_SUB_NAME,
        topic_name=TASK_EVENTS_TOPIC,
        data=event_payload
    )
    logger.info(f"Published task_updated event for task {task.id} to topic {TASK_EVENTS_TOPIC}")


async def publish_reminder_triggered_event(
    task: Task,
    user_id: UUID,
    trigger_time: datetime,
    message: str,
    event_initiator: str = "task_service",
    dapr_client: DaprClient = None
):
    """
    Publishes a reminder_triggered event to the reminders topic.
    """
    dapr_invoker = DaprServiceInvoker(dapr_client)
    event_payload = {
        "event_type": "reminder_triggered",
        "task_id": str(task.id),
        "user_id": str(user_id),
        "message": message,
        "trigger_time": trigger_time.isoformat(),
        "event_initiator": event_initiator,
        "timestamp": datetime.utcnow().isoformat(),
    }
    await dapr_invoker.publish_event(
        pubsub_name=PUB_SUB_NAME,
        topic_name=REMINDERS_TOPIC,
        data=event_payload
    )
    logger.info(f"Published reminder_triggered event for task {task.id} to topic {REMINDERS_TOPIC} at {trigger_time}")
