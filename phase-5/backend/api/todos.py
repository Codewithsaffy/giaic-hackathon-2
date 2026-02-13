from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Optional
import uuid # Remove if unused, but might be needed for other things? No.
import json

from models import Task, TaskCreate, TaskUpdate, TaskPublic
from database import get_session
from auth import get_current_user
import crud

router = APIRouter(tags=["Todos"])

import httpx

async def schedule_reminder_job(task: Task, event_type: str):
    """Schedule a reminder firing via Dapr Jobs API."""
    if not task.remind_at:
        return
        
    try:
        # Dapr Jobs API: POST /v1.0-alpha1/jobs/<job-name>
        job_name = f"reminder-{task.id}"
        
        # Calculate 'due' time in Dapr format (ISO string or relative)
        due_at = task.remind_at.isoformat() + "Z" # Assuming UTC
        
        job_payload = {
            "schedule": f"@at {due_at}",
            "data": {
                "type": "reminder",
                "task_id": task.id,
                "user_id": task.user_id,
                "title": task.title
            }
        }
        
        async with httpx.AsyncClient() as client:
            # We call the sidecar on 3500
            url = f"http://localhost:3500/v1.0-alpha1/jobs/{job_name}"
            resp = await client.post(url, json=job_payload)
            if resp.status_code >= 400:
                import logging
                logging.getLogger(__name__).error(f"Dapr Jobs Error ({resp.status_code}): {resp.text}")
            else:
                import logging
                logging.getLogger(__name__).info(f"⏰ Scheduled Dapr Job: {job_name} for {due_at}")
                
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Failed to schedule Dapr Job: {e}")

async def publish_task_event(request: Request, task: Task, event_type: str):
    """Helper to publish task events to Dapr pubsub."""
    try:
        dapr_client = getattr(request.app.state, "dapr_client", None)
        if not dapr_client:
            return
        
        event_data = {
            "task_id": task.id,
            "user_id": task.user_id,
            "title": task.title,
            "event_type": event_type,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "remind_at": task.remind_at.isoformat() if task.remind_at else None,
            "recurring_interval": task.recurring_interval,
            "completed": task.completed
        }
        
        # 1. Publish to 'task-events' for auditing/recurrence
        dapr_client.publish_event(
            pubsub_name="pubsub",
            topic_name="task-events",
            data=json.dumps(event_data),
            data_content_type="application/json"
        )
        
        # 2. If it's a creation/update with a reminder, publish to 'reminders' topic
        if task.remind_at and event_type in ["task_created", "task_updated"]:
             dapr_client.publish_event(
                pubsub_name="pubsub",
                topic_name="reminders",
                data=json.dumps(event_data),
                data_content_type="application/json"
            )
            
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Failed to publish Dapr event: {e}")

@router.get("/api/{user_id}/tasks", response_model=List[TaskPublic])
async def get_user_tasks(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    offset: int = 0,
    limit: int = 100,
    completed: Optional[bool] = None,
    priority: Optional[int] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> List[TaskPublic]:
    token_user_id = current_user.get("sub")
    if token_user_id != user_id:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own tasks"
        )
    # Pass all filters/sort options to CRUD
    tasks = await crud.get_tasks_by_user(
        session, 
        user_id, 
        offset=offset, 
        limit=limit,
        completed=completed,
        priority=priority,
        tag=tag,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return tasks

@router.post("/api/{user_id}/tasks", response_model=TaskPublic, status_code=status.HTTP_201_CREATED)
async def create_user_task(
    user_id: str,
    task: TaskCreate,
    request: Request,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> TaskPublic:
    token_user_id = current_user.get("sub")
    if token_user_id != user_id:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create tasks for yourself"
        )
    db_task = await crud.create_task(session, task, user_id)
    # Publish event for audit/logging
    await publish_task_event(request, db_task, "task_created")
    # Schedule exact reminder via Jobs API
    await schedule_reminder_job(db_task, "task_created")
    return db_task

@router.get("/api/{user_id}/tasks/{task_id}", response_model=TaskPublic)
async def get_user_task(
    user_id: str,
    task_id: int, # Changed to int
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> TaskPublic:
    token_user_id = current_user.get("sub")
    if token_user_id != user_id:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    task = await crud.get_task_by_id(session, task_id, user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/api/{user_id}/tasks/{task_id}", response_model=TaskPublic)
async def update_user_task(
    user_id: str,
    task_id: int, # Changed to int
    task_update: TaskUpdate,
    request: Request,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> TaskPublic:
    token_user_id = current_user.get("sub")
    if token_user_id != user_id:
         raise HTTPException(status_code=403, detail="Access denied")
    
    updated_task = await crud.update_task(session, task_id, task_update, user_id)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Publish event for changes
    await publish_task_event(request, updated_task, "task_updated")
    # Update/Schedule reminder
    await schedule_reminder_job(updated_task, "task_updated")
    return updated_task

@router.delete("/api/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_task(
    user_id: str,
    task_id: int, # Changed to int
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> None:
    token_user_id = current_user.get("sub")
    if token_user_id != user_id:
         raise HTTPException(status_code=403, detail="Access denied")

    success = await crud.delete_task(session, task_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")

@router.patch("/api/{user_id}/tasks/{task_id}/complete", response_model=TaskPublic)
async def toggle_task_completion(
    user_id: str,
    task_id: int, # Changed to int
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> TaskPublic:
    token_user_id = current_user.get("sub")
    if token_user_id != user_id:
         raise HTTPException(status_code=403, detail="Access denied")

    current_task = await crud.get_task_by_id(session, task_id, user_id)
    if not current_task:
        raise HTTPException(status_code=404, detail="Task not found")

    updated_task = await crud.update_task(
        session,
        task_id,
        TaskUpdate(completed=not current_task.completed),
        user_id
    )
    if not updated_task:
         raise HTTPException(status_code=404, detail="Task not found")

    return updated_task