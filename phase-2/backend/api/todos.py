from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
import uuid # Remove if unused, but might be needed for other things? No.

from models import Task, TaskCreate, TaskUpdate, TaskPublic
from database import get_session
from auth import get_current_user
import crud

router = APIRouter(tags=["Todos"])

@router.get("/api/{user_id}/tasks", response_model=List[TaskPublic])
async def get_user_tasks(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    offset: int = 0,
    limit: int = 100
) -> List[TaskPublic]:
    token_user_id = current_user.get("sub")
    if token_user_id != user_id:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own tasks"
        )
    # Corrected function call: get_tasks_by_user
    tasks = await crud.get_tasks_by_user(session, user_id, offset=offset, limit=limit)
    return tasks

@router.post("/api/{user_id}/tasks", response_model=TaskPublic, status_code=status.HTTP_201_CREATED)
async def create_user_task(
    user_id: str,
    task: TaskCreate,
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
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> TaskPublic:
    token_user_id = current_user.get("sub")
    if token_user_id != user_id:
         raise HTTPException(status_code=403, detail="Access denied")
    
    updated_task = await crud.update_task(session, task_id, task_update, user_id)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
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