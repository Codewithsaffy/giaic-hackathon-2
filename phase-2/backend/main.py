import os
from dotenv import load_dotenv

# Load .env from the backend directory
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)


from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from contextlib import asynccontextmanager
import logging
import uuid

from .database import get_session, engine, init_db
from .models import Task, TaskCreate, TaskUpdate, TaskPublic
from . import crud
from .api import auth, todos

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