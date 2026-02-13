"""
Centralized database configuration and session management.
Uses neon-sqlmodel-patterns and fastapi-sqlmodel-ai-backend skills.
"""
from sqlmodel import create_engine, Session, SQLModel
from typing import Generator
import os

# Neon PostgreSQL connection string
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@host:port/database"
)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries
    pool_pre_ping=True,  # Verify connections before use
    pool_size=10,  # Connection pool size
    max_overflow=20  # Max overflow connections
)

def init_db():
    """Create all database tables"""
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.
    Use with FastAPI Depends for automatic session management.
    """
    with Session(engine) as session:
        yield session
