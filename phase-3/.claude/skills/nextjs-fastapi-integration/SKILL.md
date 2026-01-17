---
name: nextjs-fastapi-integration
description: Build Next.js 16 App Router with FastAPI backend. Use when creating API routes, server components, or connecting frontend to Python backend.
---

# Next.js 16 + FastAPI Integration

## Overview

Integrate Next.js 16 App Router with FastAPI backend for full-stack development. This skill provides patterns for server components, client components, server actions, and secure communication between frontend and backend.

## Next.js 16 App Router Patterns

### 1. Server Components by Default
```typescript
// app/dashboard/page.tsx
import { fetchUserData } from '@/lib/data';

export default async function DashboardPage({ params }: { params: { id: string } }) {
  const user = await fetchUserData(params.id);

  return (
    <div>
      <h1>Dashboard</h1>
      <UserProfile user={user} />
    </div>
  );
}
```

### 2. Client Components for Interactivity
```typescript
// components/InteractiveComponent.tsx
'use client';

import { useState } from 'react';

export default function InteractiveComponent() {
  const [count, setCount] = useState(0);

  return (
    <button onClick={() => setCount(count + 1)}>
      Count: {count}
    </button>
  );
}
```

### 3. Server Actions for Mutations
```typescript
// actions/user-actions.ts
'use server';

import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';

export async function updateUserProfile(formData: FormData) {
  const name = formData.get('name');
  const email = formData.get('email');

  // Call FastAPI endpoint
  const response = await fetch(`${process.env.API_BASE_URL}/api/users/me`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${await getCurrentUserToken()}`,
    },
    body: JSON.stringify({ name, email }),
  });

  if (!response.ok) {
    throw new Error('Failed to update profile');
  }

  revalidatePath('/dashboard');
  redirect('/dashboard');
}
```

### 4. API Routes at /app/api/
```typescript
// app/api/users/route.ts
import { NextRequest } from 'next/server';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const userId = searchParams.get('id');

  // Proxy to FastAPI backend
  const response = await fetch(`${process.env.FASTAPI_URL}/api/users/${userId}`, {
    headers: {
      'Authorization': `Bearer ${request.headers.get('authorization')?.replace('Bearer ', '')}`,
    },
  });

  return response.json();
}
```

## FastAPI Backend Structure

### 1. RESTful Endpoints with User Isolation
```python
# routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel import Session, select
from models.user import User, UserRead, UserUpdate
from dependencies import get_current_user, get_db_session

router = APIRouter(prefix="/api", tags=["users"])

@router.get("/users/{user_id}", response_model=UserRead)
async def get_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_db_session)
):
    if current_user.get("sub") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")

    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@router.put("/users/{user_id}", response_model=UserRead)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_db_session)
):
    if current_user.get("sub") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this resource")

    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)

    return user
```

### 2. SQLModel for ORM
```python
# models/user.py
from sqlmodel import SQLModel, Field, create_engine
from pydantic import BaseModel
from typing import Optional
import uuid

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    name: Optional[str] = None

class User(UserBase, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

class UserRead(UserBase):
    id: str
```

### 3. Pydantic Models for Validation
```python
# schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreateRequest(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
```

### 4. Neon PostgreSQL Connection
```python
# database.py
from sqlmodel import create_engine, Session
from typing import Generator
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=False)

def get_db_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
```

## Communication Patterns

### 1. JWT in Authorization Header
```typescript
// lib/auth.ts
export async function getCurrentUserToken(): Promise<string> {
  // Get token from cookies, session storage, or auth provider
  const token = document.cookie
    .split('; ')
    .find(row => row.startsWith('auth_token='))
    ?.split('=')[1];

  return token || '';
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await getCurrentUserToken();

  const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }

  return response.json();
}
```

### 2. Error Handling
```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],  # Configure based on your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=r"https://.*\.vercel\.app"  # For Vercel deployments
)

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )
```

### 3. CORS Configuration
```typescript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Credentials', value: 'true' },
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET,DELETE,PATCH,POST,PUT' },
          { key: 'Access-Control-Allow-Headers', value: 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version' },
        ]
      }
    ]
  }
}

module.exports = nextConfig
```

### 4. Type-Safe API Calls with TypeScript
```typescript
// types/api.ts
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
}

// hooks/useApi.ts
import { useState, useEffect } from 'react';

export function useApi<T>(url: string) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const token = await getCurrentUserToken();
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}${url}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [url]);

  return { data, loading, error };
}
```

## Integration Checklist

Before implementation, ensure:

| Check | Requirement |
|-------|-------------|
| **Server Components** | Use server components for data fetching and rendering by default |
| **Client Components** | Use client components only when interactivity is needed |
| **Server Actions** | Implement mutations using server actions for security |
| **SQLModel Setup** | Configure SQLModel with Neon PostgreSQL |
| **JWT Authentication** | Implement JWT-based authentication with proper token handling |
| **CORS Configuration** | Configure CORS to allow communication between Next.js and FastAPI |
| **Type Safety** | Ensure type safety between frontend and backend with shared types |

## Common Integration Patterns

### Pattern 1: Server Component Fetching Data from FastAPI
```typescript
// app/users/[id]/page.tsx
import { getUserById } from '@/lib/users';

export default async function UserPage({ params }: { params: { id: string } }) {
  const user = await getUserById(params.id);

  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  );
}
```

### Pattern 2: Client Component Calling Server Actions
```typescript
// components/UserForm.tsx
'use client';

import { updateUserProfile } from '@/actions/user-actions';

export default function UserForm({ userId }: { userId: string }) {
  async function handleSubmit(formData: FormData) {
    await updateUserProfile(formData);
  }

  return (
    <form action={handleSubmit}>
      <input name="name" type="text" placeholder="Name" />
      <input name="email" type="email" placeholder="Email" />
      <button type="submit">Update Profile</button>
    </form>
  );
}
```

This integration ensures secure, type-safe communication between your Next.js frontend and FastAPI backend with proper separation of concerns and optimal performance.