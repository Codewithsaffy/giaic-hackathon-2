---
name: multi-user-data-isolation
description: Implement user-scoped data access patterns. Use when filtering queries, protecting resources, or ensuring users only see their own data.
---

# Multi-User Data Isolation

## Overview

Implement user-scoped data access patterns to ensure users only see and interact with their own data. This skill provides patterns for backend implementation, database schema design, and API design to prevent cross-user data access.

## Backend Patterns

### 1. Extract User ID from JWT
```python
# middleware/auth.py
from fastapi import Request, HTTPException, Depends
from jose import JWTError, jwt
import os

def get_current_user_id(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = auth_header[7:]  # Remove "Bearer " prefix
    secret = os.getenv("JWT_SECRET")

    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: no user ID")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### 2. Add User ID Filter to All Queries
```python
# services/user_data_service.py
from sqlmodel import Session, select
from models import UserDocument
from typing import List

def get_user_documents(user_id: str, session: Session) -> List[UserDocument]:
    # Always filter by user_id
    documents = session.exec(
        select(UserDocument).where(UserDocument.user_id == user_id)
    ).all()
    return documents

def create_user_document(user_id: str, document_data: dict, session: Session) -> UserDocument:
    # Always associate with the authenticated user
    document = UserDocument(user_id=user_id, **document_data)
    session.add(document)
    session.commit()
    session.refresh(document)
    return document
```

### 3. Verify URL User ID Matches Token User ID
```python
# routers/documents.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

router = APIRouter(prefix="/api", tags=["documents"])

@router.get("/{user_id}/documents/{document_id}")
async def get_document(
    user_id: str,
    document_id: str,
    current_user_id: Annotated[str, Depends(get_current_user_id)]
):
    # Verify URL user_id matches token user_id
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")

    # Additional logic to fetch document
    # ...
```

### 4. Return 403 for Mismatches
```python
# middleware/authorization.py
def require_user_ownership(resource_user_id: str, current_user_id: str):
    if resource_user_id != current_user_id:
        raise HTTPException(status_code=403, detail="User not authorized to access this resource")
```

## Database Schema

### 1. Add User ID Column to User-Scoped Tables
```sql
-- Example: documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key constraint
    CONSTRAINT fk_documents_user_id
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
);

-- Index on user_id for performance
CREATE INDEX idx_documents_user_id ON documents(user_id);
```

### 2. SQLModel Example
```python
# models/document.py
from sqlmodel import SQLModel, Field, create_engine
from typing import Optional
import uuid

class UserDocumentBase(SQLModel):
    title: str
    content: Optional[str] = None

class UserDocument(UserDocumentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)  # Foreign key with index

    class Config:
        # Additional configuration if needed
        pass
```

### 3. Row Level Security (RLS) Policy Example (PostgreSQL)
```sql
-- Enable RLS on table
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Create policy that restricts access to user's own data
CREATE POLICY documents_user_isolation_policy ON documents
    FOR ALL
    USING (user_id = current_setting('app.current_user_id')::text);

-- Function to set current user in session
CREATE OR REPLACE FUNCTION set_current_user(user_id TEXT)
RETURNS void AS $$
BEGIN
    PERFORM set_config('app.current_user_id', user_id, true);
END;
$$ LANGUAGE plpgsql;
```

## API Design

### 1. URL Pattern: /api/{user_id}/resource
```python
# routers/documents.py
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/api", tags=["documents"])

@router.get("/{user_id}/documents")
async def list_user_documents(
    user_id: str,
    current_user_id: Annotated[str, Depends(get_current_user_id)]
):
    # Verify user is accessing their own data
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")

    # Fetch user's documents
    documents = get_user_documents(user_id, session)
    return {"documents": documents}

@router.get("/{user_id}/documents/{document_id}")
async def get_user_document(
    user_id: str,
    document_id: str,
    current_user_id: Annotated[str, Depends(get_current_user_id)]
):
    # Verify user is accessing their own data
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")

    # Fetch specific document
    # ...
```

### 2. Validate User ID Ownership on Every Request
```python
# decorators/ownership_check.py
from functools import wraps
from fastapi import HTTPException

def require_ownership(model_class, id_field="id", user_field="user_id"):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user_id from token and resource_id from URL
            current_user_id = kwargs.get('current_user_id')
            resource_id = kwargs.get(id_field)  # This would be the document_id, etc.

            # Fetch the resource to check ownership
            # This is pseudocode - implementation depends on your ORM
            resource = session.get(model_class, resource_id)
            if not resource or getattr(resource, user_field) != current_user_id:
                raise HTTPException(status_code=403, detail="Not authorized to access this resource")

            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### 3. Filter List Endpoints by User ID
```python
# routers/documents.py
@router.get("/{user_id}/documents")
async def list_user_documents(
    user_id: str,
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    skip: int = 0,
    limit: int = 100
):
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")

    # Always filter by user_id in the query
    documents = session.exec(
        select(UserDocument)
        .where(UserDocument.user_id == user_id)
        .offset(skip)
        .limit(limit)
    ).all()

    return {"documents": documents, "total": len(documents)}
```

## Implementation Checklist

Before implementation, ensure:

| Check | Requirement |
|-------|-------------|
| **JWT User ID Extraction** | Implement middleware to extract user_id from JWT tokens |
| **Query Filtering** | Add WHERE user_id = {current_user} to all user-scoped queries |
| **URL Validation** | Verify URL user_id matches token user_id on every request |
| **Database Schema** | Add user_id column with foreign key and index to all user-scoped tables |
| **403 Handling** | Return 403 Forbidden for unauthorized access attempts |
| **RLS Consideration** | Consider implementing Row Level Security for additional protection |

## Common Security Issues to Avoid

- ❌ Direct object references without user validation
- ❌ Missing user_id filters in queries
- ❌ Trusting URL parameters without token verification
- ❌ Allowing cross-user data access through list endpoints
- ❌ Not indexing user_id columns (performance issues)

## Testing Data Isolation

```python
# test_data_isolation.py
def test_user_data_isolation():
    # Create two users
    user1_id = create_test_user("user1@example.com")
    user2_id = create_test_user("user2@example.com")

    # Create documents for each user
    create_document_for_user(user1_id, "User 1 Document")
    create_document_for_user(user2_id, "User 2 Document")

    # Verify user 1 can only see their own documents
    user1_docs = get_user_documents(user1_id)
    assert len(user1_docs) == 1
    assert user1_docs[0].title == "User 1 Document"

    # Verify user 1 cannot access user 2's documents
    try:
        access_user_document(user1_id, user2_document_id)
        assert False, "Should not be able to access other user's document"
    except HTTPException as e:
        assert e.status_code == 403
```

This implementation ensures robust multi-user data isolation with proper validation at every level of your application.