import sys
import os

# Add the current directory to sys.path to support both local and Vercel execution
# This ensures that 'import database', etc. work regardless of where the command is run
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from dotenv import load_dotenv
import logging

# Load environment variables
# In production/K8s, we rely on the environment variables set by the cluster.
# We only load .env if we're not in a containerized environment or for local development.
if not os.getenv("KUBERNETES_SERVICE_HOST"):
    load_dotenv()
    env_path = os.path.join(current_dir, ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path) # No override=True here

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FORCE SET OPENAI_API_KEY for openai-agents library compatibility
# This ensures it's available before any client initialization
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key:
    # Check if OPENAI_API_KEY is missing or identical
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = gemini_key
        logger.info("Set OPENAI_API_KEY from GEMINI_API_KEY")

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from contextlib import asynccontextmanager
import logging
import uuid

from database import get_session, engine, init_db
from models import Task, TaskCreate, TaskUpdate, TaskPublic
import crud
from api import auth, todos, chat_simple

# Dapr and MCP imports
from dapr.clients import DaprClient
from agents.mcp import MCPServerStdio
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables and persistent resources on startup."""
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized.")
    
    # Initialize Dapr Client (resiliently for local dev)
    try:
        if os.getenv("DAPR_HTTP_PORT") or os.getenv("DAPR_GRPC_PORT"):
            logger.info("Dapr ports detected, initializing Dapr client...")
            app.state.dapr_client = DaprClient()
            logger.info("Dapr client initialized.")
        else:
            app.state.dapr_client = None
    except Exception as e:
        logger.error(f"Failed to initialize Dapr client: {e}")
        app.state.dapr_client = None

    # [NEW] Initialize Persistent MCP Server
    try:
        mcp_server_path = os.path.join(current_dir, "mcp_server_tasks.py")
        logger.info(f"Initializing persistent TaskManager MCP server: {mcp_server_path}")
        
        # We use the context manager manually to make it persistent
        mcp_stdio = MCPServerStdio(
            name="TaskManager",
            params={
                "command": sys.executable,
                "args": ["-u", mcp_server_path],
                "env": os.environ.copy()
            },
            client_session_timeout_seconds=300 # Increased for persistence
        )
        
        # Start the MCP server process
        app.state.mcp_server = await mcp_stdio.__aenter__()
        logger.info("✅ Persistent TaskManager MCP server started.")
        
    except Exception as e:
        logger.error(f"Failed to start persistent MCP server: {e}")
        app.state.mcp_server = None
    
    yield
    
    # Cleanup on shutdown
    if hasattr(app.state, "mcp_server") and app.state.mcp_server:
        logger.info("Stopping persistent MCP server...")
        try:
            # We need to call __aexit__ on the original context manager
            # but since we stored the session, we'll try to find the mcp_stdio
            # For simplicity, we'll just log and let the process end if clean exit is tricky,
            # but let's try to be professional.
            await mcp_stdio.__aexit__(None, None, None)
            logger.info("Persistent MCP server stopped.")
        except:
             pass

    if app.state.dapr_client:
        app.state.dapr_client.close()
    await engine.dispose()
    logger.info("Database disposed.")

app = FastAPI(
    title="Todo App API",
    description="REST API for the Todo application with JWT authentication",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth.router)

# Include todo routes
app.include_router(todos.router)

# Include simple chat router
app.include_router(chat_simple.router)

@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"message": "Todo App API is running!"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}