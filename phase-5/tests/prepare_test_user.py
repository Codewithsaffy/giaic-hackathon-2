import os
import uuid
import logging
from sqlalchemy import create_engine, text
from sqlmodel import Session, create_engine, SQLModel
from src.shared.models import User

DATABASE_URL = "postgresql://neondb_owner:npg_BK2sVMbcRFk0@ep-crimson-math-adtpm239-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"
TEST_USER_ID = "00000000-0000-0000-0000-000000000001"

engine = create_engine(DATABASE_URL)

def prepare_test_user():
    print(f"Creating test user {TEST_USER_ID}...")
    with Session(engine) as session:
        # Check if user exists
        existing_user = session.execute(text(f"SELECT id FROM users WHERE id = '{TEST_USER_ID}'")).first()
        if not existing_user:
            user = User(
                id=uuid.UUID(TEST_USER_ID),
                username="testuser",
                email="test@example.com"
            )
            session.add(user)
            session.commit()
            print("Test user created.")
        else:
            print("Test user already exists.")

if __name__ == "__main__":
    prepare_test_user()
