---
name: mcp-python-sdk-expert
description: "Expert knowledge of Model Context Protocol (MCP) Python SDK (v1.25.0+, spec 2025-11-25). Use for: building MCP servers that expose tools/resources/prompts, FastMCP quickstart servers, tool schema definition with JSON Schema 2020-12, structured outputs, integration with OpenAI Agents SDK, SSE/Streamable HTTP transports. Covers server creation, tool registration, context handling, validation, and production deployment patterns."
author: "AI Todo Chatbot Project"
version: "1.0"
date: "2025-01-11"
---

## Overview

The Model Context Protocol (MCP) is an open protocol for connecting LLMs to external tools and data. Think of it as a standardized API specifically designed for LLM interactions.

**Current Version**: v1.25.0 (Python SDK)
**Spec Version**: 2025-11-25
**Maintainer**: Anthropic, PBC

**What MCP Servers Can Do**:
- **Tools**: Functions the LLM can call (like POST endpoints)
- **Resources**: Data the LLM can read (like GET endpoints)  
- **Prompts**: Reusable templates for LLM interactions

## Installation

```bash
# Latest version
pip install mcp

# Specific version
pip install mcp==1.25.0

# With FastMCP (recommended for quick starts)
pip install "mcp[fastmcp]"

# For development
pip install "mcp[dev]"
```

## Two Approaches to Building MCP Servers

### 1. FastMCP (Recommended - Quick Start)

**Best for**: Simple servers, rapid prototyping, minimal boilerplate

```python
from mcp.server.fastmcp import FastMCP

# Create server
mcp = FastMCP("My MCP Server")

# Register a tool - that's it!
@mcp.tool()
def add_task(user_id: str, title: str, description: str = "") -> dict:
    """
    Add a new task to the user's todo list.
    
    Args:
        user_id: User's unique identifier
        title: Task title
        description: Optional description
    
    Returns:
        Dictionary with task_id, status, and title
    """
    # Your logic here
    task_id = save_to_database(user_id, title, description)
    return {
        "task_id": task_id,
        "status": "created",
        "title": title
    }

# Auto-generates JSON schema from type hints + docstring!
```

### 2. Low-Level SDK (Full Control)

**Best for**: Complex servers, custom transports, advanced features

```python
from mcp.server.lowlevel import Server
import mcp.types as types

server = Server("my-server")

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="add_task",
            description="Add a new task",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["user_id", "title"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "add_task":
        result = add_task(**arguments)
        return [types.TextContent(
            type="text",
            text=str(result)
        )]
```

## FastMCP Deep Dive (YOUR PROJECT)

### Basic Server Setup

```python
from mcp.server.fastmcp import FastMCP, Context
from sqlmodel import Session, select
from database import engine, Task
from datetime import datetime

# Create server
mcp = FastMCP("Todo MCP Server")

# Optional: Add dependencies
mcp = FastMCP(
    "Todo MCP Server",
    dependencies=["sqlmodel", "psycopg2-binary"]
)
```

### Tool Registration Patterns

**Pattern 1: Simple Tool**

```python
@mcp.tool()
def add_task(user_id: str, title: str, description: str = "") -> dict:
    """Add a new task"""
    with Session(engine) as session:
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            completed=False,
            created_at=datetime.utcnow()
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        
        return {
            "task_id": task.id,
            "status": "created",
            "title": task.title
        }
```

**Pattern 2: Tool with Context**

```python
from dataclasses import dataclass

@dataclass
class AppContext:
    database: any
    config: dict

@mcp.tool()
def delete_task(
    user_id: str,
    task_id: int,
    context: Context[AppContext]  # Auto-injected!
) -> dict:
    """Delete a task"""
    db = context.database
    config = context.config
    
    # Use context...
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id
    ).first()
    
    if not task:
        return {
            "task_id": task_id,
            "status": "error",
            "error": "Task not found"
        }
    
    db.delete(task)
    db.commit()
    
    return {
        "task_id": task_id,
        "status": "deleted",
        "title": task.title
    }
```

**Pattern 3: Tool with Structured Output**

```python
from pydantic import BaseModel

class TaskResponse(BaseModel):
    task_id: int
    status: str
    title: str
    error: str | None = None

@mcp.tool()
def complete_task(user_id: str, task_id: int) -> TaskResponse:
    """Mark task as complete"""
    with Session(engine) as session:
        task = session.get(Task, task_id)
        
        if not task or task.user_id != user_id:
            return TaskResponse(
                task_id=task_id,
                status="error",
                title="",
                error="Task not found"
            )
        
        task.completed = True
        task.updated_at = datetime.utcnow()
        session.commit()
        
        return TaskResponse(
            task_id=task.id,
            status="completed",
            title=task.title
        )
```

### Tool Return Types

MCP tools can return data in multiple formats:

```python
# 1. Text content only (simple)
@mcp.tool()
def simple_tool() -> str:
    return "Task created successfully"

# 2. Structured data (JSON) - NEW in spec 2025-06-18
@mcp.tool()
def structured_tool() -> dict:
    return {"task_id": 5, "status": "created"}

# 3. Both text + structured (backwards compatible)
@mcp.tool()
def hybrid_tool() -> tuple[str, dict]:
    text = "Task created"
    data = {"task_id": 5}
    return (text, data)

# 4. Full control with CallToolResult
from mcp.types import CallToolResult, TextContent

@mcp.tool()
def advanced_tool() -> CallToolResult:
    return CallToolResult(
        content=[
            TextContent(type="text", text="Task created")
        ],
        isError=False,
        _meta={"timestamp": "2025-01-11T10:00:00Z"}
    )
```

**For Your Project**: Use **structured data (dict)** for all tools - clean and simple!

### Output Schemas (Validation)

**NEW FEATURE**: Define expected output schema - SDK validates automatically!

```python
@mcp.tool(
    outputSchema={
        "type": "object",
        "properties": {
            "task_id": {"type": "number"},
            "status": {"type": "string", "enum": ["created", "error"]},
            "title": {"type": "string"}
        },
        "required": ["task_id", "status", "title"]
    }
)
def add_task_validated(user_id: str, title: str) -> dict:
    """Tool with output validation"""
    return {
        "task_id": 5,
        "status": "created",  # Must be "created" or "error"
        "title": title
    }
    # If output doesn't match schema -> automatic error!
```

### Complete Tool Examples for Your Project

```python
from mcp.server.fastmcp import FastMCP
from sqlmodel import Session, select
from database import engine, Task
from datetime import datetime

mcp = FastMCP("Todo MCP Server")

# Tool 1: add_task
@mcp.tool()
def add_task(user_id: str, title: str, description: str = "") -> dict:
    """
    Create a new task in the todo list.
    
    Args:
        user_id: The user's unique identifier
        title: Task title (required)
        description: Optional task description
    
    Returns:
        Dictionary with task_id, status, and title
    
    Example:
        >>> add_task("user123", "Buy groceries", "Milk, eggs, bread")
        {"task_id": 5, "status": "created", "title": "Buy groceries"}
    """
    with Session(engine) as session:
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            completed=False
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        
        return {
            "task_id": task.id,
            "status": "created",
            "title": task.title
        }

# Tool 2: list_tasks
@mcp.tool()
def list_tasks(
    user_id: str,
    status: str = "all"  # "all", "pending", "completed"
) -> dict:
    """
    Retrieve tasks from the user's todo list.
    
    Args:
        user_id: The user's unique identifier
        status: Filter by status - "all", "pending", or "completed"
    
    Returns:
        Dictionary with tasks array and count
    
    Example:
        >>> list_tasks("user123", "pending")
        {
            "tasks": [
                {"id": 1, "title": "Buy groceries", "completed": false},
                {"id": 2, "title": "Call mom", "completed": false}
            ],
            "count": 2,
            "status_filter": "pending"
        }
    """
    with Session(engine) as session:
        query = select(Task).where(Task.user_id == user_id)
        
        if status == "pending":
            query = query.where(Task.completed == False)
        elif status == "completed":
            query = query.where(Task.completed == True)
        
        tasks = session.exec(query).all()
        
        return {
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat()
                }
                for task in tasks
            ],
            "count": len(tasks),
            "status_filter": status
        }

# Tool 3: complete_task
@mcp.tool()
def complete_task(user_id: str, task_id: int) -> dict:
    """
    Mark a task as complete.
    
    Args:
        user_id: The user's unique identifier
        task_id: ID of the task to complete
    
    Returns:
        Dictionary with task_id, status, and title
    """
    with Session(engine) as session:
        task = session.exec(
            select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
        ).first()
        
        if not task:
            return {
                "task_id": task_id,
                "status": "error",
                "error": "Task not found",
                "title": ""
            }
        
        task.completed = True
        task.updated_at = datetime.utcnow()
        session.commit()
        
        return {
            "task_id": task.id,
            "status": "completed",
            "title": task.title
        }

# Tool 4: delete_task
@mcp.tool()
def delete_task(user_id: str, task_id: int) -> dict:
    """
    Remove a task from the todo list.
    
    Args:
        user_id: The user's unique identifier
        task_id: ID of the task to delete
    
    Returns:
        Dictionary with task_id, status, and title
    """
    with Session(engine) as session:
        task = session.exec(
            select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
        ).first()
        
        if not task:
            return {
                "task_id": task_id,
                "status": "error",
                "error": "Task not found",
                "title": ""
            }
        
        title = task.title
        session.delete(task)
        session.commit()
        
        return {
            "task_id": task_id,
            "status": "deleted",
            "title": title
        }

# Tool 5: update_task
@mcp.tool()
def update_task(
    user_id: str,
    task_id: int,
    title: str | None = None,
    description: str | None = None
) -> dict:
    """
    Modify a task's title or description.
    
    Args:
        user_id: The user's unique identifier
        task_id: ID of the task to update
        title: New title (optional)
        description: New description (optional)
    
    Returns:
        Dictionary with task_id, status, and updated title
    """
    with Session(engine) as session:
        task = session.exec(
            select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
        ).first()
        
        if not task:
            return {
                "task_id": task_id,
                "status": "error",
                "error": "Task not found",
                "title": ""
            }
        
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        
        task.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(task)
        
        return {
            "task_id": task.id,
            "status": "updated",
            "title": task.title
        }
```

## Running the MCP Server

### Development (Local)

```python
# mcp_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Todo MCP Server")

# ... register tools ...

if __name__ == "__main__":
    # Stdio transport (for testing)
    mcp.run()
    
    # Or HTTP transport
    import uvicorn
    uvicorn.run(mcp.get_asgi_app(), host="0.0.0.0", port=8001)
```

Run it:
```bash
# Stdio mode
python mcp_server.py

# HTTP mode
python mcp_server.py --transport http --port 8001
```

### Production (FastAPI Integration)

```python
# main.py
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
import uvicorn

app = FastAPI()
mcp = FastMCP("Todo MCP Server")

# Register your tools
@mcp.tool()
def add_task(...): ...

# Mount MCP server on /mcp endpoint
app.mount("/mcp", mcp.get_asgi_app())

# Your other FastAPI routes
@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

**IMPORTANT**: MCP server runs on port **8001**, main FastAPI on port **8000**.

## Transports

MCP supports multiple transport protocols:

### 1. Streamable HTTP (Recommended for Production)

```python
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

app = FastAPI()
mcp = FastMCP("My Server")

app.mount("/mcp", mcp.get_asgi_app())

# Client connects to: http://localhost:8001/mcp
```

### 2. Server-Sent Events (SSE)

```python
from mcp.server.sse import SseServerTransport

# Server setup
transport = SseServerTransport("/sse")
# Client connects to: http://localhost:8001/sse
```

### 3. Stdio (Development/Testing)

```python
from mcp.server.stdio import stdio_server

# Runs as subprocess
# Good for local testing, not production
await stdio_server(server)
```

**For Your Project**: Use **Streamable HTTP** (FastAPI mount).

## Lifecycle Management

```python
from contextlib import asynccontextmanager
from mcp.server.fastmcp import FastMCP, Context

@dataclass
class AppContext:
    db: Database

@asynccontextmanager
async def app_lifespan(server: FastMCP):
    """Startup and shutdown logic"""
    # Startup
    db = await Database.connect()
    print("Database connected")
    
    try:
        yield AppContext(db=db)
    finally:
        # Shutdown
        await db.disconnect()
        print("Database disconnected")

# Use lifespan
mcp = FastMCP("My Server", lifespan=app_lifespan)

@mcp.tool()
def my_tool(context: Context[AppContext]) -> dict:
    # Access lifecycle context
    db = context.db
    return {"status": "ok"}
```

## Context Capabilities

The `Context` object provides several capabilities:

```python
from mcp.server.fastmcp import Context

@mcp.tool()
async def advanced_tool(user_id: str, context: Context) -> dict:
    # 1. Logging
    await context.info(f"Processing for user {user_id}")
    await context.warning("Slow operation")
    await context.error("Something failed")
    
    # 2. Progress reporting
    total = 100
    for i in range(total):
        await context.report_progress(i, total)
        # ... do work ...
    
    # 3. Request metadata
    request_id = context.request_id
    
    return {"status": "ok"}
```

## Error Handling

```python
@mcp.tool()
def risky_tool(task_id: int) -> dict:
    """Tool that might fail"""
    try:
        result = perform_operation(task_id)
        return {
            "task_id": task_id,
            "status": "success",
            "result": result
        }
    except ValueError as e:
        # Return structured error
        return {
            "task_id": task_id,
            "status": "error",
            "error": "Invalid task ID",
            "details": str(e)
        }
    except Exception as e:
        # Log but don't expose internals
        logger.error(f"Tool error: {e}")
        return {
            "task_id": task_id,
            "status": "error",
            "error": "Internal server error"
        }
```

## Testing MCP Tools

### Unit Testing

```python
import pytest
from your_mcp_server import add_task

def test_add_task():
    result = add_task(
        user_id="test_user",
        title="Test Task",
        description="Test Description"
    )
    
    assert result["status"] == "created"
    assert result["title"] == "Test Task"
    assert "task_id" in result

def test_add_task_error():
    result = add_task(
        user_id="",  # Invalid
        title="Task"
    )
    
    assert result["status"] == "error"
```

### Integration Testing with MCP Inspector

```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Start your MCP server
python mcp_server.py

# Open inspector
mcp-inspector http://localhost:8001/mcp
```

## Complete Server Example for Your Project

```python
# mcp_server.py
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from sqlmodel import Session, create_engine, select
from contextlib import asynccontextmanager
from dataclasses import dataclass
import uvicorn

# Database models
from database import Task

# Database connection
DATABASE_URL = "postgresql://user:pass@neon-host/db"
engine = create_engine(DATABASE_URL)

# Create FastAPI app
app = FastAPI(title="Todo MCP Server")

# Create MCP server
mcp = FastMCP("Todo MCP Server")

# All 5 tools
@mcp.tool()
def add_task(user_id: str, title: str, description: str = "") -> dict:
    """Create a new task"""
    with Session(engine) as session:
        task = Task(user_id=user_id, title=title, description=description)
        session.add(task)
        session.commit()
        session.refresh(task)
        return {
            "task_id": task.id,
            "status": "created",
            "title": task.title
        }

@mcp.tool()
def list_tasks(user_id: str, status: str = "all") -> dict:
    """Retrieve tasks"""
    with Session(engine) as session:
        query = select(Task).where(Task.user_id == user_id)
        if status == "pending":
            query = query.where(Task.completed == False)
        elif status == "completed":
            query = query.where(Task.completed == True)
        tasks = session.exec(query).all()
        return {
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "completed": t.completed
                }
                for t in tasks
            ],
            "count": len(tasks)
        }

@mcp.tool()
def complete_task(user_id: str, task_id: int) -> dict:
    """Mark task as complete"""
    with Session(engine) as session:
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()
        if not task:
            return {"task_id": task_id, "status": "error", "error": "Not found"}
        task.completed = True
        session.commit()
        return {"task_id": task.id, "status": "completed", "title": task.title}

@mcp.tool()
def delete_task(user_id: str, task_id: int) -> dict:
    """Delete a task"""
    with Session(engine) as session:
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()
        if not task:
            return {"task_id": task_id, "status": "error", "error": "Not found"}
        title = task.title
        session.delete(task)
        session.commit()
        return {"task_id": task_id, "status": "deleted", "title": title}

@mcp.tool()
def update_task(
    user_id: str,
    task_id: int,
    title: str | None = None,
    description: str | None = None
) -> dict:
    """Update task"""
    with Session(engine) as session:
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()
        if not task:
            return {"task_id": task_id, "status": "error", "error": "Not found"}
        if title:
            task.title = title
        if description:
            task.description = description
        session.commit()
        return {"task_id": task.id, "status": "updated", "title": task.title}

# Mount MCP server
app.mount("/mcp", mcp.get_asgi_app())

# Health check
@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

## Deployment Checklist

- [ ] Set proper DATABASE_URL environment variable
- [ ] Use connection pooling for database
- [ ] Add error logging (Sentry, etc.)
- [ ] Set up health check endpoint
- [ ] Configure CORS if needed
- [ ] Use HTTPS in production
- [ ] Add rate limiting
- [ ] Monitor tool execution times
- [ ] Set up automated backups for database
- [ ] Test all tools individually
- [ ] Test with MCP Inspector
- [ ] Load test with expected traffic

## Common Issues

**Issue**: "Tool not registered"
- **Fix**: Ensure `@mcp.tool()` decorator is used and server is restarted

**Issue**: "Database connection failed"
- **Fix**: Check DATABASE_URL, ensure Neon is accessible

**Issue**: "Tool returns wrong format"
- **Fix**: Return dict, not string. Check examples above.

**Issue**: "Agent can't see tools"
- **Fix**: Verify MCP server URL is correct, check CORS settings

**Issue**: "Slow tool execution"
- **Fix**: Add database indexes, use connection pooling, optimize queries

## Best Practices

1. **Always return structured data** (dict) from tools
2. **Include error status** in responses, not exceptions
3. **Use type hints** - auto-generates schemas
4. **Write detailed docstrings** - becomes tool descriptions
5. **Validate inputs** in tool functions
6. **Use database sessions** correctly (with context manager)
7. **Log tool executions** for debugging
8. **Test tools independently** before MCP integration
9. **Version your tools** if making breaking changes
10. **Monitor performance** - slow tools = bad UX

## Key Takeaways for Your Project

1. **Use FastMCP** - simpler than low-level SDK
2. **Return dict from all tools** - clean structured output
3. **Mount on /mcp endpoint** via FastAPI
4. **Run on port 8001** (separate from main app on 8000)
5. **Each tool needs docstring** - becomes description
6. **Type hints are mandatory** - generates JSON schema
7. **Always handle errors** - return error status in dict
8. **Test with MCP Inspector** before agent integration
9. **Use SQLModel Session** properly (with statement)
10. **MCP is stateless** - no memory between calls

## Resources

- GitHub: https://github.com/modelcontextprotocol/python-sdk
- Docs: https://modelcontextprotocol.github.io/python-sdk/
- Spec: https://modelcontextprotocol.io/
- Examples: https://github.com/modelcontextprotocol/python-sdk/tree/main/examples
- Inspector: https://github.com/modelcontextprotocol/inspector