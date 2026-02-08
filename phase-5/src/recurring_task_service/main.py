from fastapi import FastAPI, Depends, Request
from sqlmodel import Session, create_engine, SQLModel
from dapr.clients import DaprClient

from src.shared.logging_config import configure_logging
from src.shared.dapr_utils import DaprServiceInvoker
from src.shared.models import BaseSQLModel, RecurringTask # Ensure RecurringTask is imported for metadata
from src.recurring_task_service.api.recurring_task_api import router as recurring_router

import os
import logging

configure_logging("recurring_task_service")
logger = logging.getLogger("recurring_task_service")

from dapr.ext.fastapi import DaprApp

app = FastAPI(title="Recurring Task Service")
dapr_app = DaprApp(app)
app.include_router(recurring_router)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@host:port/database")
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Dependency for database session
def get_session():
    with Session(engine) as session:
        yield session

# Dependency for Dapr client
def get_dapr_client():
    with DaprClient() as client:
        yield client

# Dependency for Dapr service invoker
def get_dapr_invoker(dapr_client: DaprClient = Depends(get_dapr_client)):
    return DaprServiceInvoker(dapr_client)


@app.get("/healthz", status_code=200)
async def health_check():
    return {"status": "ok"}

@app.post("/api/jobs/trigger")
async def handle_job_trigger(
    request: Request,
    dapr_client: DaprClient = Depends(get_dapr_client)
):
    """
    Dapr calls this endpoint when a scheduled job (recurring task) fires.
    """
    try:
        job_data = await request.json()
        logger.info(f"Received job trigger: {job_data}")
        
        data = job_data.get("data", {})
        if data.get("type") == "recurring_task":
            # Publish 'task_created' event to Kafka via Dapr PubSub
            # Task Service should subscribe to this to create the actual task instance
            publisher = DaprServiceInvoker(dapr_client)
            event_payload = {
                "event_type": "task_created",
                "description": data.get("description"),
                "user_id": data.get("user_id"),
                "priority": data.get("priority", "Medium"),
                "status": "pending",
                "source": "recurring_task_service",
                "timestamp": os.getenv("TIMESTAMP", "") # Optional
            }
            
            await publisher.publish_event(
                pubsub_name="pubsub-kafka",
                topic_name="task-events",
                data=event_payload
            )
            logger.info(f"Published task_created event from recurring trigger: {data.get('description')}")

        return {"status": "SUCCESS"}
    except Exception as e:
        logger.error(f"Error handling job trigger: {str(e)}")
        return {"status": "ERROR", "detail": str(e)}
