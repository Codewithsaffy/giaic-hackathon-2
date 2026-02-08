"""
Task Service - Main Application
Refactored using fastapi-sqlmodel-ai-backend patterns
"""
from fastapi import FastAPI, Depends, Body, Request
from sqlmodel import Session
from uuid import UUID
from typing import Optional
import logging
from datetime import datetime
from dapr.clients import DaprClient

from src.shared.logging_config import configure_logging
from src.shared.models import Task, Priority
from src.shared.database import init_db, get_session
from src.shared.dapr_utils import DaprServiceInvoker
from src.task_service.api.task_api import router as task_router

configure_logging("task_service")
logger = logging.getLogger("task_service")

app = FastAPI(title="Task Service")

@app.on_event("startup")
def on_startup():
    """Initialize database on startup"""
    init_db()
    logger.info("Task Service started - database initialized")

# Include API router
app.include_router(task_router, prefix="/api")

# Dependency for Dapr client
def get_dapr_client():
    with DaprClient() as client:
        yield client

@app.get("/healthz", status_code=200)
async def health_check():
    return {"status": "ok"}

@app.post("/api/events/task-created")
async def handle_task_created_event(
    event: dict = Body(...),
    session: Session = Depends(get_session)
):
    """
    Handles task_created events from Pub/Sub (published by Recurring Task Service).
    """
    try:
        logger.info(f"Received task_created event: {event}")
        data = event.get("data", {})
        event_type = data.get("event_type")
        
        if event_type == "task_created":
            new_task = Task(
                description=data.get("description"),
                user_id=UUID(data.get("user_id")),
                priority=Priority(data.get("priority", "Medium")),
                status="pending"
            )
            session.add(new_task)
            session.commit()
            logger.info(f"Successfully created task instance for user {new_task.user_id}")
            
        return {"status": "SUCCESS"}
    except Exception as e:
        logger.error(f"Error processing task_created event: {str(e)}")
        return {"status": "ERROR", "detail": str(e)}

@app.post("/job/{job_name}")
@app.post("/api/jobs/trigger")
async def handle_job_trigger(
    request: Request,
    job_name: Optional[str] = None,
    dapr_client: DaprClient = Depends(get_dapr_client)
):
    """
    Dapr calls this endpoint when a scheduled job (reminder) fires.
    """
    try:
        job_data = await request.json()
        logger.info(f"Received job trigger: {job_data}")
        
        data = job_data.get("data", {})
        if data.get("type") == "reminder":
            # Publish 'reminder_triggered' event to Kafka via Dapr PubSub
            publisher = DaprServiceInvoker(dapr_client)
            event_payload = {
                "event_type": "reminder_triggered",
                "task_id": data.get("task_id"),
                "user_id": data.get("user_id"),
                "message": data.get("message"),
                "trigger_time": data.get("trigger_time") or datetime.utcnow().isoformat(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Publish to Kafka
            dapr_client.publish_event(
                pubsub_name="pubsub-kafka",
                topic_name="reminders",
                data=event_payload
            )
            logger.info(f"Published reminder_triggered event for task {data.get('task_id')}")
            
        return {"status": "SUCCESS"}
    except Exception as e:
        logger.error(f"Error processing job trigger: {str(e)}")
        return {"status": "ERROR", "detail": str(e)}
