import sys
import os

# Add the current directory to sys.path to support both local and Vercel execution
# This ensures that 'import database', etc. work regardless of where the command is run
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from dotenv import load_dotenv

# Load environment variables
# 1. Try default loading (CWD - good for Vercel/Local-in-folder)
load_dotenv()
# 2. Try absolute path relative to script (Good for Local-from-parent)
env_path = os.path.join(current_dir, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path, override=True)

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
from api import auth, todos

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables on startup."""
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized.")
    yield
    # Cleanup on shutdown
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

@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"message": "Todo App API is running!"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}