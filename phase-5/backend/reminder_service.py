import logging
import json
from fastapi import FastAPI, Request
from dapr.ext.fastapi import DaprApp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
dapr_app = DaprApp(app)

@dapr_app.subscribe(pubsub_name="pubsub", topic="task-events")
async def task_event_handler(event_data):
    """Handle task events from the main backend."""
    data = json.loads(event_data.data) if isinstance(event_data.data, str) else event_data.data
    logger.info(f"Received task event: {data}")
    
    event_type = data.get("event_type")
    task_id = data.get("task_id")
    remind_at = data.get("remind_at")
    
    if remind_at:
        logger.info(f"Scheduling reminder for task {task_id} at {remind_at}")
        # In a real implementation, we could use Dapr's Scheduler or Cron binding
        # For this phase, we log the scheduled event
    
    if event_type == "task_created":
        logger.info(f"Initializing state for new task {task_id}")

@app.get("/health")
async def health():
    return {"status": "ok"}
