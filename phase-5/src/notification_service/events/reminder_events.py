import logging
import json
from uuid import UUID
from datetime import datetime

from dapr.clients import DaprClient
from dapr.ext.fastapi import DaprApp
from fastapi import FastAPI # Import FastAPI for DaprApp initialization

from src.shared.dapr_utils import DaprServiceInvoker # Assuming DaprServiceInvoker is available
from src.shared.models import NotificationType, Notification, User # Assuming these models are available
from src.shared.logging_config import configure_logging # Assuming logging is configured

logger = logging.getLogger(__name__)

# PUB_SUB_NAME and TOPIC are imported or defined here
PUB_SUB_NAME = "pubsub-kafka"
REMINDERS_TOPIC = "reminders"

async def reminder_triggered_subscriber(event_data: dict, dapr_client: DaprClient = None):
    """
    Subscribes to 'reminder_triggered' events and processes them to create notifications.
    """
    if not dapr_client:
        dapr_client = DaprClient() # Fallback if not injected

    logger.info(f"Received reminder_triggered event: {event_data}")

    try:
        # Extract data from event
        task_id = event_data.get("task_id")
        user_id = event_data.get("user_id")
        message = event_data.get("message")
        trigger_time_str = event_data.get("trigger_time") # ISO format string

        if not all([task_id, user_id, message, trigger_time_str]):
            logger.error(f"Incomplete event data received for reminder: {event_data}")
            return {"status": "DROP"} # Indicate event should be dropped if data is incomplete

        trigger_time = datetime.fromisoformat(trigger_time_str)

        # In a real scenario, we'd use a session to save this notification to the DB
        # For now, we'll simulate.
        new_notification = Notification(
            user_id=UUID(user_id),
            task_id=UUID(task_id),
            message=message,
            trigger_time=trigger_time,
            type=NotificationType.REMINDER,
            status="pending" # Will change to 'sent' when actually processed
        )
        logger.info(f"Notification to be created: {new_notification.dict()}")

        # Here, you would typically save the notification to your database via a service.
        # For a truly event-driven approach, this subscriber might directly send the notification
        # or invoke another endpoint on the Notification Service API to persist it.
        # For now, we'll just log that it was received.

        # Example of invoking internal API to save notification (requires session)
        # dapr_invoker = DaprServiceInvoker(dapr_client)
        # await dapr_invoker.invoke_service(
        #     app_id=NOTIFICATION_SERVICE_APP_ID, # This service itself
        #     method_name="/notifications",
        #     data=new_notification.dict(), # Send Pydantic dict
        #     http_verb="POST"
        # )

        logger.info(f"Successfully processed reminder for task {task_id}.")
        return {"status": "SUCCESS"} # Indicate successful processing

    except Exception as e:
        logger.error(f"Error processing reminder_triggered event: {e}", exc_info=True)
        return {"status": "RETRY"} # Indicate event should be retried
