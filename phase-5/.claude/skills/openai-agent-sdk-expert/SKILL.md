---
name: openai-agents-sdk-expert
description: "Expert knowledge of OpenAI Agents SDK for Python (latest 2025 version 0.6.5+). Use for: building agentic workflows, creating agents with tools/handoffs/guardrails, MCP server integration, session management, tracing, and stateless multi-agent architectures. Covers Agent creation, Runner execution, function tools, MCP integration (MCPServerStdio, MCPServerSse, MCPServerStreamableHttp), context handling, and best practices for production FastAPI apps."
author: "AI Todo Chatbot Project"
version: "1.0"
date: "2025-01-11"
---

## Overview

OpenAI Agents SDK is a lightweight framework for building multi-agent workflows in Python. Released in 2025, it's the production-ready successor to Swarm. The SDK is **provider-agnostic** and supports OpenAI's Responses API, Chat Completions API, and 100+ other LLMs.

**Current Version**: 0.6.5 (January 2025)

**Key Features**:
- Agents: LLMs with instructions, tools, guardrails, and handoffs
- Handoffs: Delegate tasks between specialized agents
- Guardrails: Input/output validation and safety checks
- Sessions: Automatic conversation history management
- Tracing: Built-in debugging and monitoring
- MCP Integration: Native support for Model Context Protocol servers

## Installation

```bash
# Basic installation
pip install openai-agents

# With specific version
pip install openai-agents==0.6.5

# Required dependencies (auto-installed)
# - openai
# - pydantic
```

## Core Primitives

### 1. Agent

The fundamental building block - an LLM configured with instructions, tools, and capabilities.

```python
from agents import Agent

agent = Agent(
    name="Todo Assistant",  # Agent identifier
    instructions="You are a helpful todo list assistant",  # System prompt
    model="gpt-4",  # or "gpt-4o", "gpt-3.5-turbo", etc.
)
```

**Agent Parameters**:
- `name` (str): Agent identifier
- `instructions` (str | callable): System prompt or dynamic instruction function
- `model` (str): Model identifier (default: "gpt-4o")
- `tools` (list): Function tools or sub-agents exposed as tools
- `handoffs` (list): Sub-agents for delegation
- `guardrails` (list): Input/output validation rules
- `mcp_servers` (list): MCP servers providing tools
- `output_type` (type): Structured output type (Pydantic, dataclass, etc.)
- `model_settings` (ModelSettings): Advanced model configuration

### 2. Runner

Executes agent workflows and manages the conversation loop.

```python
from agents import Runner

# Synchronous execution
result = Runner.run_sync(
    agent,
    "Add a task to buy groceries"
)
print(result.final_output)

# Asynchronous execution
result = await Runner.run(
    agent,
    "Show me all my tasks"
)
```

**Runner Methods**:
- `Runner.run(agent, input, context=None)` - Async execution
- `Runner.run_sync(agent, input, context=None)` - Sync execution
- `Runner.run_streamed(agent, input, context=None)` - Streaming results

### 3. Function Tools

Turn any Python function into a tool with automatic schema generation.

```python
from agents import Agent

def add_task(user_id: str, title: str, description: str = "") -> dict:
    """
    Add a new task to the user's todo list.
    
    Args:
        user_id: The user's unique identifier
        title: Task title
        description: Optional task description
    
    Returns:
        Dictionary with task_id, status, and title
    """
    # Your database logic here
    task_id = save_to_database(user_id, title, description)
    return {
        "task_id": task_id,
        "status": "created",
        "title": title
    }

# Agent automatically generates schema from function signature
agent = Agent(
    name="Todo Agent",
    instructions="Help users manage tasks",
    tools=[add_task]  # Just pass the function!
)
```

**Tool Best Practices**:
1. Use type hints - SDK generates JSON schema automatically
2. Write detailed docstrings - becomes tool description
3. Use Pydantic models for complex inputs
4. Return structured data (dict, Pydantic model, dataclass)
5. Handle errors gracefully - return error status in response

### 4. MCP Server Integration

**CRITICAL FOR YOUR PROJECT**: The SDK has native MCP support.

```python
from agents import Agent
from agents.mcp import MCPServerStreamableHttp

async def create_agent_with_mcp():
    # Connect to your MCP server
    mcp_server = MCPServerStreamableHttp(
        name="Todo MCP Server",
        params={
            "url": "http://localhost:8001/mcp",
            "timeout": 10
        },
        cache_tools_list=True  # Cache tool definitions
    )
    
    agent = Agent(
        name="Todo Assistant",
        instructions="""
        You are a helpful todo list assistant.
        Use the available MCP tools to manage tasks.
        Always confirm actions with friendly responses.
        """,
        mcp_servers=[mcp_server]  # Tools loaded automatically
    )
    
    return agent
```

**MCP Server Types**:

1. **MCPServerStreamableHttp** (Recommended for production)
```python
from agents.mcp import MCPServerStreamableHttp

server = MCPServerStreamableHttp(
    name="My MCP Server",
    params={
        "url": "https://api.example.com/mcp",
        "headers": {"Authorization": "Bearer token"}
    },
    cache_tools_list=True
)
```

2. **MCPServerSse** (Server-Sent Events)
```python
from agents.mcp import MCPServerSse

async with MCPServerSse(
    name="SSE Server",
    params={
        "url": "http://localhost:8000/sse",
        "headers": {"X-Workspace": "workspace-123"}
    }
) as server:
    agent = Agent(mcp_servers=[server])
```

3. **MCPServerStdio** (Local subprocess)
```python
from agents.mcp import MCPServerStdio

async with MCPServerStdio(
    name="Local Server",
    params={
        "command": "python",
        "args": ["mcp_server.py"]
    }
) as server:
    agent = Agent(mcp_servers=[server])
```

### 5. Sessions

**Automatic conversation memory** - eliminates manual state management.

```python
from agents import Agent, Runner, Session

agent = Agent(name="Assistant")

# Create a session
session = Session()

# First turn
result = await Runner.run(agent, "Hello!", session=session)
# Session automatically stores: user message + assistant response

# Second turn - agent has context from first turn
result = await Runner.run(agent, "What did I just say?", session=session)
# Agent can reference previous conversation
```

**IMPORTANT**: For your stateless FastAPI architecture, DON'T use SDK Sessions. Instead:
1. Load conversation history from database
2. Build messages array manually
3. Pass to Runner without session parameter
4. Save response to database

```python
# Stateless pattern for FastAPI
async def chat_endpoint(user_message: str, conversation_id: int):
    # 1. Load history from DB
    messages = load_from_database(conversation_id)
    
    # 2. Add new message
    messages.append({"role": "user", "content": user_message})
    
    # 3. Run agent (no session)
    result = await Runner.run(
        agent,
        input=user_message,
        # Pass history via context or messages parameter
    )
    
    # 4. Save to DB
    save_to_database(conversation_id, result.final_output)
    
    return result.final_output
```

### 6. Context (Dependency Injection)

Pass state and dependencies to agents and tools.

```python
from dataclasses import dataclass
from agents import Agent, Runner

@dataclass
class AppContext:
    user_id: str
    database_session: any
    config: dict

# Tools can access context
def add_task(title: str, context: AppContext) -> dict:
    # Access user_id and database from context
    user_id = context.user_id
    db = context.database_session
    # ... save task
    return {"status": "created"}

agent = Agent[AppContext](
    name="Todo Agent",
    tools=[add_task]
)

# Run with context
context = AppContext(
    user_id="user_123",
    database_session=db_session,
    config={"max_tasks": 100}
)

result = await Runner.run(agent, "Add a task", context=context)
```

## Agent Patterns

### Pattern 1: Single Agent with Tools

```python
from agents import Agent

def add_task(user_id: str, title: str) -> dict:
    return {"task_id": 1, "status": "created"}

def list_tasks(user_id: str) -> list:
    return [{"id": 1, "title": "Buy groceries"}]

agent = Agent(
    name="Todo Agent",
    instructions="Manage user tasks",
    tools=[add_task, list_tasks]
)
```

### Pattern 2: Agent with Handoffs (Delegation)

```python
from agents import Agent

# Specialized agents
booking_agent = Agent(
    name="Booking Agent",
    instructions="Handle all booking requests"
)

refund_agent = Agent(
    name="Refund Agent",
    instructions="Handle all refund requests"
)

# Triage agent delegates to specialists
triage_agent = Agent(
    name="Customer Service",
    instructions="""
    Help customers with their requests.
    - For bookings, hand off to booking agent
    - For refunds, hand off to refund agent
    """,
    handoffs=[booking_agent, refund_agent]
)

# When user asks about refund, triage agent automatically
# hands off to refund_agent
```

### Pattern 3: Agent as Tool (Sub-agents)

```python
from agents import Agent

# Create specialized sub-agents
booking_agent = Agent(...)
refund_agent = Agent(...)

# Expose them as tools to main agent
main_agent = Agent(
    name="Customer Service",
    instructions="Call specialized tools for specific tasks",
    tools=[
        booking_agent.as_tool(
            tool_name="booking_expert",
            tool_description="Handles booking questions"
        ),
        refund_agent.as_tool(
            tool_name="refund_expert",
            tool_description="Handles refund questions"
        )
    ]
)
```

**Handoffs vs Tools**:
- **Handoffs**: Agent delegates and conversation transfers to new agent
- **Tools**: Agent invokes sub-agent but maintains control

### Pattern 4: Dynamic Instructions

```python
from agents import Agent, RunContextWrapper

def dynamic_instructions(
    context: RunContextWrapper[AppContext],
    agent: Agent
) -> str:
    user_id = context.context.user_id
    task_count = get_task_count(user_id)
    
    return f"""
    You are helping user {user_id}.
    They currently have {task_count} tasks.
    Be helpful and friendly.
    """

agent = Agent(
    name="Todo Agent",
    instructions=dynamic_instructions  # Function, not string!
)
```

## MCP Integration Best Practices

### 1. Tool Filtering

```python
from agents.mcp import MCPServerStreamableHttp

def filter_tools(tools, filter_context):
    """Only expose tools relevant to current user"""
    user_role = filter_context.context.user_role
    
    if user_role == "admin":
        return tools  # All tools
    else:
        # Filter out admin tools
        return [t for t in tools if not t.name.startswith("admin_")]

server = MCPServerStreamableHttp(
    name="Todo MCP",
    params={"url": "http://localhost:8001/mcp"},
    tool_config={
        "filter": filter_tools
    }
)
```

### 2. Tool Caching

```python
# Cache tool definitions (recommended if tools don't change)
server = MCPServerStreamableHttp(
    name="Todo MCP",
    params={"url": "http://localhost:8001/mcp"},
    cache_tools_list=True  # Only calls list_tools() once
)
```

### 3. Approval Required

```python
async def approval_callback(tool_name, tool_input):
    """Require approval for destructive operations"""
    if tool_name == "delete_task":
        # Show confirmation to user
        return await ask_user_confirmation(
            f"Delete task {tool_input['task_id']}?"
        )
    return True  # Auto-approve other tools

server = MCPServerStreamableHttp(
    name="Todo MCP",
    params={"url": "http://localhost:8001/mcp"},
    tool_config={
        "require_approval": {
            "delete_task": "always",  # Always require approval
            "add_task": "never"       # Never require approval
        },
        "on_approval_request": approval_callback
    }
)
```

## Structured Outputs

Force agent to return specific data format.

```python
from pydantic import BaseModel
from agents import Agent

class TaskList(BaseModel):
    tasks: list[dict]
    total_count: int
    has_pending: bool

agent = Agent(
    name="Task Analyzer",
    instructions="Analyze user's tasks and return structured data",
    output_type=TaskList  # Force this output format
)

result = await Runner.run(agent, "Analyze my tasks")
# result.final_output is a TaskList instance
print(result.final_output.total_count)
```

## Tracing & Debugging

Built-in tracing for debugging and monitoring.

```python
from agents import Agent, Runner
from agents.tracing import trace

# Basic tracing
with trace("todo_workflow"):
    result = await Runner.run(agent, "Add task")

# Custom spans
with trace("database_operation"):
    save_to_database(task)

# Tracing is automatic - shows:
# - Agent invocations
# - Tool calls
# - MCP server requests
# - Token usage
# - Timing information
```

## Error Handling

```python
from agents import Agent, Runner
from agents.exceptions import ToolExecutionError

async def risky_tool(task_id: int) -> dict:
    """Tool that might fail"""
    try:
        result = delete_task(task_id)
        return {"status": "deleted", "task_id": task_id}
    except Exception as e:
        # Return error in structured format
        # Agent will see this and handle gracefully
        return {
            "status": "error",
            "error": str(e),
            "task_id": task_id
        }

agent = Agent(
    name="Todo Agent",
    instructions="""
    When tools return errors, inform the user politely.
    Don't expose technical error details.
    """,
    tools=[risky_tool]
)
```

## FastAPI Integration Pattern

**YOUR PROJECT ARCHITECTURE**:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp
from sqlmodel import Session, select
from database import engine, Conversation, Message

app = FastAPI()

# Create agent once at startup
async def create_agent():
    mcp_server = MCPServerStreamableHttp(
        name="Todo MCP Server",
        params={"url": "http://localhost:8001/mcp"},
        cache_tools_list=True
    )
    
    return Agent(
        name="Todo Assistant",
        instructions="""
        You are a helpful todo list assistant.
        Help users manage tasks through natural language.
        Always confirm actions with friendly responses.
        """,
        mcp_servers=[mcp_server]
    )

# Initialize at startup
agent = None

@app.on_event("startup")
async def startup():
    global agent
    agent = await create_agent()

# Chat endpoint (STATELESS)
class ChatRequest(BaseModel):
    user_id: str
    conversation_id: int | None = None
    message: str

class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: list

@app.post("/api/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    with Session(engine) as session:
        # 1. Get or create conversation
        if request.conversation_id:
            conversation = session.get(Conversation, request.conversation_id)
        else:
            conversation = Conversation(user_id=request.user_id)
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
        
        # 2. Load history from database
        messages = session.exec(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at)
        ).all()
        
        # 3. Save user message
        user_msg = Message(
            conversation_id=conversation.id,
            user_id=request.user_id,
            role="user",
            content=request.message
        )
        session.add(user_msg)
        session.commit()
        
        # 4. Run agent with context
        from dataclasses import dataclass
        
        @dataclass
        class UserContext:
            user_id: str
            conversation_id: int
        
        context = UserContext(
            user_id=request.user_id,
            conversation_id=conversation.id
        )
        
        # Execute agent (STATELESS - no session)
        result = await Runner.run(
            agent,
            input=request.message,
            context=context
        )
        
        # 5. Save assistant response
        assistant_msg = Message(
            conversation_id=conversation.id,
            user_id=request.user_id,
            role="assistant",
            content=result.final_output
        )
        session.add(assistant_msg)
        session.commit()
        
        # 6. Return response
        return ChatResponse(
            conversation_id=conversation.id,
            response=result.final_output,
            tool_calls=[
                {
                    "tool": call.name,
                    "input": call.arguments,
                    "result": call.result
                }
                for call in result.tool_calls
            ]
        )
```

## Common Patterns for Your Project

### 1. User Context Injection

```python
@dataclass
class TodoContext:
    user_id: str
    database: Session
    
def add_task(title: str, description: str, context: TodoContext) -> dict:
    """MCP tool gets context automatically"""
    task = Task(
        user_id=context.user_id,
        title=title,
        description=description
    )
    context.database.add(task)
    context.database.commit()
    return {"task_id": task.id, "status": "created"}
```

### 2. Streaming Responses

```python
@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    result = Runner.run_streamed(
        agent,
        input=request.message,
        stream=True
    )
    
    async def generate():
        async for event in result.stream_events():
            if event.type == "run_item_stream_event":
                yield f"data: {event.item}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
```

### 3. Multi-Step Workflows

```python
# Agent automatically chains tools
result = await Runner.run(
    agent,
    "Delete the task about groceries"
)

# Agent will:
# 1. Call list_tasks to find grocery task
# 2. Call delete_task with the task_id
# 3. Return confirmation

# All automatic - no manual orchestration!
```

## Performance Tips

1. **Cache MCP Tool Lists**: Set `cache_tools_list=True` on MCP servers
2. **Reuse Agent Instance**: Create once, use many times (thread-safe)
3. **Use Async**: `Runner.run()` is faster than `Runner.run_sync()`
4. **Batch Operations**: Design tools that handle multiple items
5. **Connection Pooling**: Use connection pools for MCP HTTP servers

## Security Best Practices

1. **Validate Tool Inputs**: Use Pydantic models
2. **Sanitize Outputs**: Never expose internal errors to users
3. **Use Guardrails**: Add input/output validation
4. **Approval for Dangerous Operations**: Require approval for deletes
5. **Rate Limiting**: Implement at FastAPI layer
6. **Context Isolation**: Don't share context between users

## Debugging Checklist

- [ ] Is agent getting the right instructions?
- [ ] Are tools registered correctly? (check with `agent.tools`)
- [ ] Is MCP server URL correct and reachable?
- [ ] Are tool schemas valid? (check tool docstrings)
- [ ] Is context being passed correctly?
- [ ] Check tracing output for tool calls
- [ ] Verify database connections in tools
- [ ] Test tools independently before adding to agent

## Common Errors

**Error**: "Tool not found"
- **Fix**: Check MCP server is running and URL is correct

**Error**: "Invalid tool schema"
- **Fix**: Add type hints and docstring to tool function

**Error**: "Context not found"
- **Fix**: Add `context: ContextType` parameter to tool

**Error**: "Agent not calling tools"
- **Fix**: Make instructions clearer about when to use tools

## Version Compatibility

- **Python**: 3.9+ (3.11+ recommended)
- **OpenAI SDK**: Compatible with latest
- **MCP Python SDK**: v1.7.1+
- **Pydantic**: v2.x (v1 not supported)
- **FastAPI**: 0.100+

## Additional Resources

- GitHub: https://github.com/openai/openai-agents-python
- Docs: https://openai.github.io/openai-agents-python/
- Examples: https://github.com/openai/openai-agents-python/tree/main/examples
- MCP Integration: https://openai.github.io/openai-agents-python/mcp/

## Key Takeaways for Your Project

1. **Use MCPServerStreamableHttp** to connect to your MCP server on port 8001
2. **Don't use SDK Sessions** - you're managing state in PostgreSQL
3. **Create agent once at FastAPI startup** - reuse for all requests
4. **Pass user_id via Context** - tools can access it
5. **Let agent handle tool chaining** - it's automatic
6. **Agent instructions are critical** - be specific about behavior
7. **Return structured errors** from tools - agent will handle gracefully
8. **Tracing is built-in** - use it for debugging