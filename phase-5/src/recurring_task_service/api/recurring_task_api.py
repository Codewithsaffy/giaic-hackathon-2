from fastapi import APIRouter, Depends, status, Request, HTTPException
from sqlmodel import Session, select
from dapr.clients import DaprClient
from typing import List, Optional, Annotated, Any
from uuid import UUID

from src.shared.models import RecurringTask, User
from src.shared.exceptions import NotFoundException, ConflictException
from src.recurring_task_service.services.scheduler import RecurringTaskScheduler
from src.shared.dapr_utils import DaprServiceInvoker

router = APIRouter(prefix="/recurring-tasks", tags=["recurring-tasks"])


# Dependency for database session
def get_session():
    # This will be overridden by dependency injection in the main FastAPI app
    with Session() as session:
        yield session


# Dependency for Dapr client
def get_dapr_client():
    with DaprClient() as client:
        yield client


# Dependency for current user
def get_current_user(request: Request) -> User:
    user_id_str = request.headers.get("X-User-ID")
    if not user_id_str:
        return User(id=UUID("00000000-0000-0000-0000-000000000001"), username="testuser", email="test@example.com")
    
    try:
        return User(id=UUID(user_id_str), username="authenticated_user", email="")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid User ID format")


# --- Recurring Task Endpoints ---

@router.post("/", response_model=RecurringTask, status_code=status.HTTP_201_CREATED)
async def create_recurring_task(
    task_data: RecurringTask,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    dapr_client: Annotated[DaprClient, Depends(get_dapr_client)]
):
    """
    Creates a new recurring task and schedules it via Dapr.
    """
    task_data.user_id = current_user.id
    session.add(task_data)
    session.commit()
    session.refresh(task_data)

    # Schedule via Dapr Jobs API
    scheduler = RecurringTaskScheduler(DaprServiceInvoker(dapr_client))
    await scheduler.schedule_recurring_task(task_data)

    return task_data

@router.get("/{task_id}", response_model=RecurringTask, status_code=status.HTTP_200_OK)
async def get_recurring_task(
    task_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """
    Retrieves a recurring task template by its ID.
    """
    task = session.exec(
        select(RecurringTask).where(RecurringTask.id == task_id, RecurringTask.user_id == current_user.id)
    ).first()
    if not task:
        raise NotFoundException(detail=f"Recurring task with id {task_id} not found.")
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recurring_task(
    task_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    dapr_client: Annotated[DaprClient, Depends(get_dapr_client)]
):
    """
    Deletes a recurring task and unschedules it.
    """
    task = session.exec(
        select(RecurringTask).where(RecurringTask.id == task_id, RecurringTask.user_id == current_user.id)
    ).first()
    if not task:
        raise NotFoundException(detail=f"Recurring task with id {task_id} not found.")

    # Unschedule via Dapr
    scheduler = RecurringTaskScheduler(DaprServiceInvoker(dapr_client))
    await scheduler.unschedule_recurring_task(task_id)

    session.delete(task)
    session.commit()
    return {"message": "Recurring task deleted successfully."}
