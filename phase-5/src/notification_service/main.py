from fastapi import FastAPI, Request
from pydantic import BaseModel
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Notification Service")

class ReminderEvent(BaseModel):
    task_id: int
    user_id: str
    title: str
    event_type: str

@app.get("/")
async def root():
    return {"message": "Notification Service is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/dapr/subscribe")
async def subscribe():
    """Dapr subscription endpoint for declarative pubsub."""
    subscriptions = [
        {
            "pubsubname": "pubsub",
            "topic": "reminders",
            "route": "/events/reminders"
        }
    ]
    return subscriptions

@app.post("/events/reminders")
async def handle_reminder(request: Request):
    """Handle reminder events published via Dapr."""
    event_raw = await request.json()
    logger.info(f"🔔 Received reminder event: {event_raw}")
    
    # In a real app, this would send an email/push/WebSocket
    # For this phase, we log it as a successful delivery
    data = event_raw.get("data", {})
    if isinstance(data, str):
        data = json.loads(data)
        
    logger.info(f"NOTIF: Task '{data.get('title')}' is due for user {data.get('user_id')}!")
    return {"status": "SUCCESS"}

# Dapr Jobs API callback
@app.post("/api/jobs/trigger")
async def handle_job_trigger(request: Request):
    """Callback when a Dapr Job (scheduled reminder) fires."""
    job_data = await request.json()
    logger.info(f"⏰ Dapr Job Triggered: {job_data}")
    
    # Usually we'd check job_data['data']['type'] == 'reminder'
    # and then send the actual notification
    return {"status": "SUCCESS"}
