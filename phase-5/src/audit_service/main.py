from fastapi import FastAPI, Request
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Audit Service")

@app.get("/")
async def root():
    return {"message": "Audit Service is running"}

@app.post("/dapr/subscribe")
async def subscribe():
    return [
        {
            "pubsubname": "pubsub",
            "topic": "task-events",
            "route": "/events/all"
        },
        {
            "pubsubname": "pubsub",
            "topic": "reminders",
            "route": "/events/all"
        }
    ]

@app.post("/events/all")
async def handle_any_event(request: Request):
    event_raw = await request.json()
    topic = event_raw.get("topic", "unknown")
    data = event_raw.get("data", {})
    
    logger.info(f"📜 [AUDIT] Topic: {topic} | Event: {data}")
    return {"status": "SUCCESS"}
