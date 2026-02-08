from uuid import UUID
import logging
from datetime import datetime
from typing import Optional

from dapr.clients import DaprClient

from src.shared.models import Task
from src.shared.dapr_utils import DaprServiceInvoker

logger = logging.getLogger(__name__)

PUB_SUB_NAME = "pubsub-kafka"
TASK_UPDATES_TOPIC = "task-updates"


async def publish_recurring_task_instance_created_event(
    task: Task,
    user_id: UUID,
    event_initiator: str = "recurring_task_service",
    dapr_client: DaprClient = None
):
    """
    Publishes a recurring_task_instance_created event to the task-updates topic.
    """
    dapr_invoker = DaprServiceInvoker(dapr_client)
    event_payload = {
        "event_type": "recurring_task_instance_created",
        "task_id": str(task.id),
        "user_id": str(user_id),
        "created_task_details": json.loads(task.model_dump_json()),
        "event_initiator": event_initiator,
        "timestamp": datetime.utcnow().isoformat(),
    }
    await dapr_invoker.publish_event(
        pubsub_name=PUB_SUB_NAME,
        topic_name=TASK_UPDATES_TOPIC,
        data=event_payload
    )
    logger.info(f"Published recurring_task_instance_created event for task {task.id} to topic {TASK_UPDATES_TOPIC}")