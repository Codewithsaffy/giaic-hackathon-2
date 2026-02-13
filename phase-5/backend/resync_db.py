import asyncio
import os
from sqlalchemy import text
from database import engine, init_db
from models import Task

async def resync():
    print("Dropping 'task' table to resync schema...")
    async with engine.begin() as conn:
        # Wrap raw SQL in text() for SQLAlchemy execution
        await conn.execute(text("DROP TABLE IF EXISTS task CASCADE"))
    
    print("Recreating tables...")
    await init_db()
    print("Sync complete.")

if __name__ == "__main__":
    asyncio.run(resync())
