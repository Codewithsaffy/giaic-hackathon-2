---
name: restful-api-standards
description: Build consistent RESTful APIs with proper HTTP methods, status codes, and response formats. Use when creating new endpoints or refactoring APIs.
---

# RESTful API Standards

## Overview

Build consistent RESTful APIs with proper HTTP methods, status codes, and response formats. This skill provides standards for creating predictable, maintainable APIs that follow REST principles.

## Endpoint Structure

### Standard CRUD Operations
```
GET    /api/{user_id}/tasks          # List all resources for user
POST   /api/{user_id}/tasks          # Create new resource
GET    /api/{user_id}/tasks/{id}     # Get specific resource
PUT    /api/{user_id}/tasks/{id}     # Update entire resource
PATCH  /api/{user_id}/tasks/{id}     # Partial update
DELETE /api/{user_id}/tasks/{id}     # Delete resource
```

### Extended Operations
```
PATCH  /api/{user_id}/tasks/{id}/complete  # Partial update action
POST   /api/{user_id}/tasks/batch        # Batch operations
GET    /api/{user_id}/tasks/search       # Search/filter operations
```

### Implementation Example
```python
# routers/tasks.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlmodel import select
from models.task import Task, TaskCreate, TaskUpdate, TaskRead
from dependencies import get_current_user_id, get_session

router = APIRouter(prefix="/api/{user_id}", tags=["tasks"])

@router.get("/tasks", response_model=List[TaskRead])
async def list_tasks(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id),
    session=Depends(get_session)
):
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    tasks = session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()
    return tasks

@router.post("/tasks", response_model=TaskRead, status_code=201)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user_id: str = Depends(get_current_user_id),
    session=Depends(get_session)
):
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    task = Task(user_id=user_id, **task_data.dict())
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.get("/tasks/{task_id}", response_model=TaskRead)
async def get_task(
    user_id: str,
    task_id: str,
    current_user_id: str = Depends(get_current_user_id),
    session=Depends(get_session)
):
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    return task

@router.put("/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    user_id: str,
    task_id: str,
    task_data: TaskUpdate,
    current_user_id: str = Depends(get_current_user_id),
    session=Depends(get_session)
):
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    for key, value in task_data.dict(exclude_unset=True).items():
        setattr(task, key, value)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(
    user_id: str,
    task_id: str,
    current_user_id: str = Depends(get_current_user_id),
    session=Depends(get_session)
):
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()
    return

@router.patch("/tasks/{task_id}/complete", response_model=TaskRead)
async def complete_task(
    user_id: str,
    task_id: str,
    current_user_id: str = Depends(get_current_user_id),
    session=Depends(get_session)
):
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = True
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

## Response Format

### Standard Response Structure
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

### Success Response Example
```json
{
  "success": true,
  "data": {
    "id": "123",
    "title": "Complete project",
    "completed": false
  },
  "error": null
}
```

### Error Response Example
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Task with ID 123 not found",
    "details": "The requested task does not exist or you do not have permission to access it"
  }
}
```

### Implementation Helper
```python
# utils/responses.py
from typing import Any, Optional
from pydantic import BaseModel

class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[dict] = None

def success_response(data: Any = None) -> APIResponse:
    return APIResponse(success=True, data=data, error=None)

def error_response(message: str, code: str = "GENERAL_ERROR", details: str = None) -> APIResponse:
    error_info = {
        "code": code,
        "message": message
    }
    if details:
        error_info["details"] = details

    return APIResponse(success=False, data=None, error=error_info)
```

## HTTP Status Codes

### Standard Status Codes
- `200 OK`: Successful GET, PUT, PATCH requests
- `201 Created`: Successful POST request with resource creation
- `204 No Content`: Successful DELETE request
- `400 Bad Request`: Client sent invalid request
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Valid authentication but insufficient permissions
- `404 Not Found`: Resource does not exist
- `409 Conflict`: Resource already exists or conflict with current state
- `422 Unprocessable Entity`: Validation errors
- `500 Internal Server Error`: Server-side error

### Status Code Usage Examples
```python
# Error handling examples
from fastapi import HTTPException

# 400 Bad Request - Validation error
if not is_valid_email(email):
    raise HTTPException(
        status_code=400,
        detail="Invalid email format"
    )

# 401 Unauthorized - Missing authentication
if not token:
    raise HTTPException(
        status_code=401,
        detail="Authentication token required"
    )

# 403 Forbidden - Insufficient permissions
if user_id != resource_owner_id:
    raise HTTPException(
        status_code=403,
        detail="Insufficient permissions"
    )

# 404 Not Found - Resource doesn't exist
if not resource:
    raise HTTPException(
        status_code=404,
        detail="Resource not found"
    )

# 409 Conflict - Resource already exists
if email_exists:
    raise HTTPException(
        status_code=409,
        detail="User with this email already exists"
    )

# 422 Unprocessable Entity - Validation error
if age < 0:
    raise HTTPException(
        status_code=422,
        detail="Age cannot be negative"
    )
```

## API Design Best Practices

### 1. Consistent Naming Conventions
- Use plural nouns for resources (e.g., `/users`, `/tasks`)
- Use lowercase with hyphens for compound names (e.g., `/user-profiles`)
- Use camelCase for query parameters (e.g., `?sortBy=createdAt`)

### 2. Version Your APIs
```python
# Version in URL
router = APIRouter(prefix="/api/v1/{user_id}", tags=["tasks"])
```

### 3. Handle Query Parameters Consistently
```python
@router.get("/tasks")
async def list_tasks(
    user_id: str,
    limit: int = Query(100, le=1000),  # Default 100, max 1000
    offset: int = 0,
    sort_by: str = "created_at",
    order: str = Query("desc", regex="^(asc|desc)$")
):
    # Implementation
```

### 4. Use Standard Headers
```python
# Common headers
Content-Type: application/json
Authorization: Bearer <token>
X-Request-ID: <unique-id>
```

## Implementation Checklist

Before implementation, ensure:

| Check | Requirement |
|-------|-------------|
| **Endpoint Structure** | Follow standard CRUD patterns with consistent URL structure |
| **HTTP Methods** | Use correct HTTP methods for each operation |
| **Status Codes** | Return appropriate status codes for all scenarios |
| **Response Format** | Use consistent response structure across all endpoints |
| **Error Handling** | Implement proper error responses with meaningful messages |
| **Authentication** | Verify user access to resources in all endpoints |
| **Validation** | Validate input data and return appropriate error codes |
| **Documentation** | Document all endpoints with methods, parameters, and responses |

## Common API Design Issues to Avoid

- ❌ Inconsistent endpoint naming conventions
- ❌ Using GET requests for operations that modify data
- ❌ Returning 200 status for error responses
- ❌ Using non-standard HTTP status codes
- ❌ Missing authentication/authorization checks
- ❌ Inconsistent response formats across endpoints
- ❌ Not handling edge cases and error scenarios properly

This implementation ensures consistent, predictable RESTful APIs that follow industry best practices and are easy to maintain and consume.