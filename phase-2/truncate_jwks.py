import os
import asyncio
import asyncpg
from dotenv import load_dotenv

async def truncate():
    # Load env variables
    load_dotenv('f:/hackathon-phase-2/backend/.env')
    db_url = os.getenv('DATABASE_URL')

    if not db_url:
        print("DATABASE_URL not found")
        return

    # asyncpg expects postgres:// or postgresql://
    try:
        conn = await asyncpg.connect(db_url)
        await conn.execute('TRUNCATE TABLE jwks;')
        await conn.close()
        print("JWKS table truncated successfully")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(truncate())
