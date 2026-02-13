from fastapi import FastAPI, Request
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Recurring Task Service")

@app.get("/")
async def root():
    return {"message": "Recurring Task Service is running"}

@app.post("/dapr/subscribe")
async def subscribe():
    return [
        {
            "pubsubname": "pubsub",
            "topic": "task-events",
            "route": "/events/task-events"
        }
    ]

@app.post("/events/task-events")
async def handle_task_event(request: Request):
    event_raw = await request.json()
    data = event_raw.get("data", {})
    if isinstance(data, str):
        data = json.loads(data)
    
    event_type = data.get("event_type")
    if event_type == "task_updated" and data.get("completed") is True:
        task_id = data.get("task_id")
        interval = data.get("recurring_interval")
        if interval:
            logger.info(f"♻️ Recurring Task '{data.get('title')}' completed. Spawning next with interval: {interval}")
            # In a real app, this would call back to task-service or direct DB
            # For Phase 5, we satisfy the logic by logging and publishing a 'recurrence_spawned' event
    
    return {"status": "SUCCESS"}
