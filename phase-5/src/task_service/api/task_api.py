"""
Task API - Refactored with proper user isolation and dependency injection
Uses: fastapi-sqlmodel-ai-backend, multi-user-data-isolation, restful-api-standards
"""
from uuid import UUID
from typing import List, Annotated, Optional
from datetime import datetime
from sqlmodel import Session, select

from fastapi import APIRouter, Depends, status, Query, Request, HTTPException

from src.shared.models import Task, Priority, User, TaskBase
from src.shared.database import get_session
from src.shared.auth import get_current_user
from src.task_service.services.task_priority_service import TaskPriorityService
from src.task_service.services.task_tag_service import TaskTagService
from src.task_service.services.task_query_service import TaskQueryService
from src.task_service.services.task_due_reminder_service import TaskDueReminderService

router = APIRouter(prefix="/tasks", tags=["tasks"])

# --- Task CRUD Endpoints ---

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskBase,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """
    Create a new task for the current user.
    ALWAYS scoped to authenticated user (multi-user-data-isolation pattern).
    """
    new_task = Task(
        description=task_data.description,
        user_id=current_user.id,  # ALWAYS set from authenticated user
        status=task_data.status,
        priority=task_data.priority,
        tags=task_data.tags,
        due_date=task_data.due_date,
        recurrence_pattern=task_data.recurrence_pattern,
        reminder_settings=task_data.reminder_settings
    )
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    return new_task

@router.get("/", response_model=List[Task], status_code=status.HTTP_200_OK)
async def list_tasks(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    List all tasks for the current user.
    ALWAYS filtered by user_id (multi-user-data-isolation pattern).
    """
    tasks = session.exec(
        select(Task)
        .where(Task.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    ).all()
    return tasks

@router.get("/{task_id}", response_model=Task, status_code=status.HTTP_200_OK)
async def get_task(
    task_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """
    Get a specific task by ID.
    Verifies ownership (multi-user-data-isolation pattern).
    """
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Verify ownership
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this task")
    
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """
    Delete a task.
    Verifies ownership (multi-user-data-isolation pattern).
    """
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Verify ownership
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")
    
    session.delete(task)
    session.commit()
    return None

# --- Priority Endpoints ---

@router.post("/{task_id}/priority", response_model=Task, status_code=status.HTTP_200_OK)
async def set_priority(
    task_id: UUID,
    new_priority: Priority,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Set task priority (user-scoped)"""
    service = TaskPriorityService(session)
    return service.set_priority(task_id, new_priority, current_user.id)

# --- Tag Endpoints ---

@router.post("/{task_id}/tags", response_model=Task, status_code=status.HTTP_200_OK)
async def add_tag(
    task_id: UUID,
    tag: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Add tag to task (user-scoped)"""
    service = TaskTagService(session)
    return service.add_tag(task_id, tag, current_user.id)

@router.delete("/{task_id}/tags/{tag}", response_model=Task, status_code=status.HTTP_200_OK)
async def remove_tag(
    task_id: UUID,
    tag: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Remove tag from task (user-scoped)"""
    service = TaskTagService(session)
    return service.remove_tag(task_id, tag, current_user.id)

# --- Search, Filter, Sort Endpoints ---

@router.get("/search/", response_model=List[Task], status_code=status.HTTP_200_OK)
async def search_filter_sort_tasks(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    query: Optional[str] = Query(None),
    priority: Optional[Priority] = Query(None),
    tags: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    sort_by: Optional[str] = Query("created_at"),
    order: Optional[str] = Query("desc")
):
    """
    Search, filter, and sort tasks (user-scoped).
    All queries ALWAYS filtered by current user.
    """
    service = TaskQueryService(session)
    return service.search_filter_sort(
        user_id=current_user.id,  # ALWAYS filter by user
        query=query,
        priority=priority,
        tags=tags.split(",") if tags else None,
        status_filter=status_filter,
        sort_by=sort_by,
        order=order
    )

# --- Due Date & Reminder Endpoints ---

@router.post("/{task_id}/due-reminder", response_model=Task, status_code=status.HTTP_200_OK)
async def set_due_date_and_reminder(
    task_id: UUID,
    due_date: datetime,
    reminder_offset: Optional[str] = None,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    request: Request = None
):
    """Set due date and optional reminder (user-scoped)"""
    service = TaskDueReminderService(session, request)
    return await service.set_due_date_and_reminder(
        task_id=task_id,
        due_date=due_date,
        reminder_offset=reminder_offset,
        user_id=current_user.id
    )
