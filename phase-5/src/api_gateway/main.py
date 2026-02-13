import os
import json
import logging
import httpx
from typing import Dict, Any, List, Optional
from uuid import UUID

from fastapi import FastAPI, Depends, HTTPException, Request, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from dapr.clients import DaprClient

from src.shared.logging_config import configure_logging
from src.api_gateway.auth import get_current_user
from src.api_gateway.nl_processor import NLProcessor

# Setup Logging
configure_logging("api_gateway")
logger = logging.getLogger("api_gateway")

app = FastAPI(title="Evolution of Todo - API Gateway")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize NLP Processor
nlp = NLProcessor()

@app.get("/healthz")
async def health_check():
    return {"status": "ok", "service": "api_gateway"}

@app.post("/api/chat")
async def chat_endpoint(
    request: Request,
    payload: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Main Chat Endpoint.
    1. Parses user message via NLProcessor.
    2. Routes to the appropriate microservice via Dapr.
    """
    user_id = current_user.get("sub")
    message = payload.get("message", "")
    
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    logger.info(f"Processing chat message from user {user_id}: {message}")

    # 1. Extract intent and params
    result = nlp.process_command(message)
    
    if not result:
        # Fallback to general conversational response or basic task creation
        # For Phase 5, we focus on the routed commands
        return {
            "response": "I'm not sure how to handle that command yet. Try 'Show me my tasks' or 'Set priority of task [ID] to high'.",
            "intent": None
        }

    intent, params = result
    logger.info(f"Inferred intent: {intent} with params: {params}")

    # 2. Route to appropriate service via Dapr Service Invocation
    # Standard Dapr Invocation URL: http://localhost:3500/v1.0/invoke/{app_id}/method/{method}
    
    try:
        # Extract user ID from current request for forwarding
        from src.shared.auth import get_current_user
        current_user = get_current_user(request)
        
        async with httpx.AsyncClient() as client:
            dapr_base_url = "http://localhost:3500/v1.0/invoke"
            
            if intent in ["create_task", "set_task_priority", "add_task_tags", "remove_task_tags", "get_tasks_by_tag", "search_filter_sort_tasks", "set_task_due_reminder"]:
                service_id = "task-service"
                endpoint_map = {
                    "create_task": "/api/tasks/",
                    "set_task_priority": f"/api/tasks/{params.get('task_id')}/priority",
                    "add_task_tags": f"/api/tasks/{params.get('task_id')}/tags",
                    "remove_task_tags": f"/api/tasks/{params.get('task_id')}/tags/{params.get('tag')}",
                    "get_tasks_by_tag": f"/api/tasks/search/?tags={params.get('tag')}",
                    "search_filter_sort_tasks": "/api/tasks/search/",
                    "set_task_due_reminder": f"/api/tasks/{params.get('task_id')}/due-reminder"
                }
                
                method = "POST" if "add" in intent or "set" in intent or "create" in intent else "DELETE" if "remove" in intent else "GET"
                target_url = f"{dapr_base_url}/{service_id}/method{endpoint_map[intent]}"
                
                # Forward request with user context
                headers = {
                    "Authorization": request.headers.get("Authorization", ""),
                    "X-User-ID": str(current_user.id),  # Pass user context to downstream service
                    "Content-Type": "application/json"
                }
                
                if method == "POST":
                    # Clean up params for the target service (remove task_id from payload if in URL)
                    body = params.copy()
                    if "task_id" in body: del body["task_id"]
                    if "tag" in body: del body["tag"]  # Remove tag if it's in URL
                    
                    # Handle Priority Enum for JSON
                    if "priority" in body: body["priority"] = body["priority"].value
                        
                    response = await client.post(target_url, json=body, headers=headers)
                else:
                    response = await client.get(target_url, params=params, headers=headers)
                
                if response.status_code >= 400:
                    logger.error(f"Upstream service error: {response.text}")
                    return {"response": f"Sorry, there was an error processing that: {response.text}", "intent": intent}
                
                return {
                    "response": f"I've updated your task as requested.",
                    "data": response.json(),
                    "intent": intent
                }

            elif intent == "create_recurring_task":
                service_id = "recurring-task-service"
                target_url = f"{dapr_base_url}/{service_id}/method/api/recurring-tasks/"
                headers = {"Authorization": request.headers.get("Authorization")}
                
                response = await client.post(target_url, json=params, headers=headers)
                return {
                    "response": "I've set up that recurring task for you!",
                    "data": response.json(),
                    "intent": intent
                }

    except Exception as e:
        logger.error(f"Dapr invocation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Service communication failure: {str(e)}")

    return {"response": "Command recognized but routing not yet implemented.", "intent": intent}

# Passthrough endpoints for direct task management if needed
@app.get("/api/tasks")
async def list_tasks(current_user: dict = Depends(get_current_user)):
    # Direct call to task-service via Dapr
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:3500/v1.0/invoke/task-service/method/api/tasks/",
            headers={"X-User-ID": str(current_user.get("sub"))}
        )
        return response.json()
