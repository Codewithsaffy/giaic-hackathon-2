import os
import asyncio
import asyncpg
from dotenv import load_dotenv

async def inspect():
    load_dotenv('f:/hackathon-phase-2/backend/.env')
    db_url = os.getenv('DATABASE_URL')
    
    if not db_url:
        print("DATABASE_URL not found")
        return

    try:
        conn = await asyncpg.connect(db_url)
        rows = await conn.fetch("SELECT column_name FROM information_schema.columns WHERE table_name = 'session';")
        print([row['column_name'] for row in rows])
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(inspect())
