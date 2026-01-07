import asyncio
from sqlmodel import select
from backend.database import get_session_context
from backend.models import Session, User

async def dump_db():
    async with get_session_context() as session:
        print("\n--- USERS ---")
        users = await session.exec(select(User))
        for user in users.all():
            print(f"User: {user.id} | {user.email} | {user.name}")

        print("\n--- SESSIONS ---")
        sessions = await session.exec(select(Session))
        for s in sessions.all():
            print(f"Session: {s.token[:20]}... | User: {s.userId} | Expires: {s.expiresAt}")

if __name__ == "__main__":
    asyncio.run(dump_db())
