---
name: fastapi-sqlmodel-ai-backend
description: "Expert knowledge of FastAPI (latest 2025) with SQLModel ORM for building AI chatbot backends. Use for: REST API design, database models, async operations, CORS configuration, dependency injection, session management with Neon PostgreSQL, stateless architecture patterns, JWT auth integration, streaming responses. Covers FastAPI 0.100+, SQLModel latest, Pydantic v2, async PostgreSQL with asyncpg."
author: "AI Todo Chatbot Project"
version: "1.0"
date: "2025-01-11"
---

## Overview

FastAPI + SQLModel is the perfect stack for AI chatbot backends:
- **FastAPI**: Modern, fast web framework with automatic API docs
- **SQLModel**: Combines SQLAlchemy ORM + Pydantic validation in one model

**Why This Stack**:
- Type safety everywhere (editor autocomplete)
- Async support (handle many concurrent users)
- Single model definition for DB + API validation
- Automatic OpenAPI documentation
- Perfect for AI/ML integration

**Versions**:
- FastAPI: 0.100+ (latest features)
- SQLModel: Latest (built on SQLAlchemy 2.x + Pydantic v2)
- Python: 3.11+ recommended

## Installation

```bash
# Core dependencies
pip install fastapi uvicorn sqlmodel psycopg2-binary

# For async PostgreSQL (recommended)
pip install asyncpg

# Full stack
pip install fastapi[all] sqlmodel asyncpg python-multipart

# For auth
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

## Project Structure

```
/backend/
  /app/
    main.py              # FastAPI app
    /api/
      /endpoints/
        chat.py          # Chat endpoint
        auth.py          # Auth endpoints
      deps.py            # Dependency injection
    /models/
      task.py            # Task model
      conversation.py    # Conversation model
      message.py         # Message model
      user.py            # User model (if using auth)
    /core/
      config.py          # Configuration
      database.py        # Database connection
      security.py        # Auth utilities
  .env                   # Environment variables
  requirements.txt
```

## Database Models with SQLModel

### Basic Model Pattern

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    """Todo task model - used for BOTH database AND API"""
    
    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Required fields
    user_id: str = Field(index=True)  # Index for fast queries
    title: str = Field(max_length=500)
    
    # Optional fields
    description: Optional[str] = None
    completed: bool = Field(default=False)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False
            }
        }
```

### Your Project Models

```python
# models/task.py
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str
    description: Optional[str] = None
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# models/conversation.py
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# models/message.py
class Message(SQLModel, table=True):
    __tablename__ = "messages"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(index=True)
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

## Database Connection (Neon PostgreSQL)

```python
# core/database.py
from sqlmodel import create_engine, Session, SQLModel
from typing import Generator
import os

# Neon PostgreSQL connection string
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@neon-host.com/dbname"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log SQL (disable in production)
    pool_pre_ping=True,  # Verify connections
    pool_size=10,  # Connection pool size
    max_overflow=20
)

def init_db():
    """Create all tables"""
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """Dependency for getting DB session"""
    with Session(engine) as session:
        yield session
```

## FastAPI Application Setup

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import init_db
from api.endpoints import chat, auth

# Create app
app = FastAPI(
    title="AI Todo Chatbot API",
    description="Conversational todo list with OpenAI Agents SDK",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev
        "https://your-app.vercel.app"  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event
@app.on_event("startup")
def on_startup():
    init_db()  # Create tables
    print("Database initialized")

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Chat Endpoint (Stateless)

```python
# api/endpoints/chat.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional, List
from core.database import get_session
from models import Task, Conversation, Message
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp

router = APIRouter()

# Request/Response models
class ChatRequest(BaseModel):
    user_id: str
    conversation_id: Optional[int] = None
    message: str

class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: List[dict] = []

# Create agent (once at startup)
agent = None

async def get_agent():
    global agent
    if agent is None:
        mcp_server = MCPServerStreamableHttp(
            name="Todo MCP",
            params={"url": "http://localhost:8001/mcp"},
            cache_tools_list=True
        )
        agent = Agent(
            name="Todo Assistant",
            instructions="""
            You are a helpful todo list assistant.
            Use available tools to manage tasks.
            Always confirm actions with friendly responses.
            """,
            mcp_servers=[mcp_server]
        )
    return agent

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    session: Session = Depends(get_session)
):
    """
    Main chat endpoint - STATELESS
    
    Flow:
    1. Get or create conversation
    2. Load message history from DB
    3. Save user message
    4. Run agent with MCP tools
    5. Save assistant response
    6. Return response
    """
    
    # 1. Get or create conversation
    if request.conversation_id:
        conversation = session.get(Conversation, request.conversation_id)
        if not conversation:
            raise HTTPException(404, "Conversation not found")
    else:
        conversation = Conversation(user_id=request.user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
    
    # 2. Load message history (for context)
    messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
    ).all()
    
    # 3. Save user message
    user_message = Message(
        conversation_id=conversation.id,
        user_id=request.user_id,
        role="user",
        content=request.message
    )
    session.add(user_message)
    session.commit()
    
    # 4. Run agent
    agent_instance = await get_agent()
    
    from dataclasses import dataclass
    
    @dataclass
    class Context:
        user_id: str
        conversation_id: int
    
    context = Context(
        user_id=request.user_id,
        conversation_id=conversation.id
    )
    
    result = await Runner.run(
        agent_instance,
        input=request.message,
        context=context
    )
    
    # 5. Save assistant response
    assistant_message = Message(
        conversation_id=conversation.id,
        user_id=request.user_id,
        role="assistant",
        content=result.final_output
    )
    session.add(assistant_message)
    session.commit()
    
    # 6. Return response
    return ChatResponse(
        conversation_id=conversation.id,
        response=result.final_output,
        tool_calls=[
            {
                "tool": call.name,
                "input": call.arguments,
                "output": call.result
            }
            for call in result.tool_calls
        ]
    )
```

## Dependency Injection Pattern

```python
# api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from core.database import get_session
from core.security import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
):
    """Get current authenticated user"""
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    return user_id

# Use in endpoints
@router.get("/me")
async def get_me(user_id: str = Depends(get_current_user)):
    return {"user_id": user_id}
```

## Environment Configuration

```python
# core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # MCP Server
    MCP_SERVER_URL: str = "http://localhost:8001/mcp"
    
    # OpenAI
    OPENAI_API_KEY: str
    
    # Auth (if using)
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "https://your-app.vercel.app"
    ]
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## Common Patterns

### 1. Query Patterns

```python
from sqlmodel import select

# Get one
task = session.get(Task, task_id)

# Query with filter
task = session.exec(
    select(Task).where(Task.id == task_id)
).first()

# Query multiple
tasks = session.exec(
    select(Task).where(Task.user_id == user_id)
).all()

# With ordering
tasks = session.exec(
    select(Task)
    .where(Task.user_id == user_id)
    .order_by(Task.created_at.desc())
).all()

# With limit
tasks = session.exec(
    select(Task)
    .where(Task.completed == False)
    .limit(10)
).all()

# Count
count = session.exec(
    select(Task).where(Task.completed == True)
).count()
```

### 2. CRUD Operations

```python
# Create
new_task = Task(user_id="user123", title="Buy milk")
session.add(new_task)
session.commit()
session.refresh(new_task)  # Get ID and defaults

# Read
task = session.get(Task, task_id)

# Update
task.title = "Buy milk and eggs"
task.updated_at = datetime.utcnow()
session.add(task)
session.commit()

# Delete
session.delete(task)
session.commit()

# Bulk operations
tasks = [Task(...) for _ in range(100)]
session.add_all(tasks)
session.commit()
```

### 3. Error Handling

```python
from sqlalchemy.exc import IntegrityError

@router.post("/tasks")
async def create_task(
    task: Task,
    session: Session = Depends(get_session)
):
    try:
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(400, "Task already exists")
    except Exception as e:
        session.rollback()
        raise HTTPException(500, "Database error")
```

### 4. Streaming Responses

```python
from fastapi.responses import StreamingResponse

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    async def generate():
        result = Runner.run_streamed(agent, request.message)
        async for event in result.stream_events():
            if event.type == "run_item_stream_event":
                yield f"data: {event.item}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

## Best Practices

### 1. Always Use Type Hints

```python
# Good
def get_task(task_id: int, session: Session) -> Task:
    return session.get(Task, task_id)

# Bad
def get_task(task_id, session):
    return session.get(Task, task_id)
```

### 2. Use Pydantic Models for API

```python
# Separate API models from DB models
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    completed: bool
    created_at: datetime

@router.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    db_task = Task(**task.dict(), user_id="user123")
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task
```

### 3. Use Context Managers

```python
# Good
with Session(engine) as session:
    task = session.get(Task, 1)

# Bad (must manually close)
session = Session(engine)
task = session.get(Task, 1)
session.close()
```

### 4. Index Critical Columns

```python
class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)  # INDEXED
    user_id: str = Field(index=True)  # INDEXED
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)  # INDEXED
```

### 5. Handle Null Values

```python
# Use Optional for nullable fields
title: Optional[str] = None  # Can be None
user_id: str  # Cannot be None (required)
```

## Testing

```python
# test_chat.py
from fastapi.testclient import TestClient
from main import app
from core.database import get_session, engine
from sqlmodel import Session, SQLModel

client = TestClient(app)

def test_create_conversation():
    # Override session
    SQLModel.metadata.create_all(engine)
    
    response = client.post("/api/chat", json={
        "user_id": "test_user",
        "message": "Add a task to buy groceries"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert "response" in data
```

## Performance Optimization

```python
# 1. Use connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True
)

# 2. Batch database calls
tasks = session.exec(
    select(Task).where(Task.user_id == user_id)
).all()  # One query, not N queries

# 3. Use select loading for relationships
# (if you add relationships later)

# 4. Add database indexes
# See model examples above

# 5. Use async if needed
from sqlmodel.ext.asyncio.session import AsyncSession
```

## Deployment Checklist

- [ ] Set DATABASE_URL environment variable
- [ ] Configure CORS for production domain
- [ ] Set up connection pooling
- [ ] Add logging (Sentry, etc.)
- [ ] Enable HTTPS
- [ ] Add rate limiting
- [ ] Configure database backups
- [ ] Set up monitoring
- [ ] Test with production data
- [ ] Create database migrations (Alembic)

## Key Takeaways

1. **SQLModel = One model for DB + API** - no duplication
2. **FastAPI = Automatic docs** - free Swagger UI
3. **Type hints everywhere** - editor support
4. **Use dependency injection** - clean code
5. **Stateless chat endpoint** - scalable architecture
6. **Connection pooling** - handle concurrent requests
7. **Index critical columns** - fast queries
8. **Separate API models** - flexibility
9. **Use async patterns** - better performance
10. **Test everything** - prevent bugs in production