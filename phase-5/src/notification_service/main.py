from fastapi import FastAPI, Depends
from sqlmodel import Session, create_engine, SQLModel
from dapr.clients import DaprClient

from src.shared.logging_config import configure_logging
from src.shared.dapr_utils import DaprServiceInvoker
from src.shared.models import BaseSQLModel # Import BaseSQLModel to create tables

import os

from dapr.ext.fastapi import DaprApp
from src.notification_service.events.reminder_events import reminder_triggered_subscriber, PUB_SUB_NAME, REMINDERS_TOPIC

configure_logging("notification_service")

app = FastAPI(title="Notification Service")
dapr_app = DaprApp(app)

@dapr_app.subscribe(pubsub=PUB_SUB_NAME, topic=REMINDERS_TOPIC)
async def handle_reminder_event(event_data: dict):
    return await reminder_triggered_subscriber(event_data)

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
