from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker
from sqlalchemy.pool import NullPool
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Neon database URL format - asyncpg driver compatible
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@ep-xxx.region.aws.neon.tech:5432/dbname")

# Ensure we use the asyncpg driver
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Fix for asyncpg which doesn't support sslmode or channel_binding in URL
connect_args = {}
if "sslmode" in DATABASE_URL or "channel_binding" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("?sslmode=require", "").replace("&sslmode=require", "")
    DATABASE_URL = DATABASE_URL.replace("?sslmode=verify-full", "").replace("&sslmode=verify-full", "")
    DATABASE_URL = DATABASE_URL.replace("?sslmode=verify-ca", "").replace("&sslmode=verify-ca", "")
    DATABASE_URL = DATABASE_URL.replace("?sslmode=disable", "").replace("&sslmode=disable", "")
    DATABASE_URL = DATABASE_URL.replace("?channel_binding=require", "").replace("&channel_binding=require", "")
    connect_args["ssl"] = "require"

# Create async engine with Neon-specific settings
# Note: For asyncpg, we need to handle SSL differently than with psycopg2
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Neon works best with NullPool for serverless
    echo=False,  # Set to True for debugging
    isolation_level="REPEATABLE READ",  # Recommended for production with async
    connect_args=connect_args,
)



# Create async session maker
AsyncSessionFactory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to provide database session for FastAPI routes."""
    async with AsyncSessionFactory() as session:
        yield session

async def init_db():
    """Initialize the database tables."""
    from sqlmodel import SQLModel
    from .models import Task  # Import here to avoid circular imports

    logger.info("Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    logger.info("Database tables initialized.")