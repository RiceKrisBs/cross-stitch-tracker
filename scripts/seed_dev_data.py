"""
Seed database with development/example data
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.append(str(Path(__file__).parent.parent))

import bcrypt
from sqlmodel import Session, select

from app.database import engine
from app.models import User


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def seed_users():
    """Create example users"""
    with Session(engine) as session:
        # Check if users already exist
        existing_count = len(session.exec(select(User)).all())

        if existing_count > 0:
            print(f"Users already seeded ({existing_count} users found). Skipping...")
            return

        print("Seeding example users...")

        # Create test users
        users = [
            User(
                username="alice",
                email="alice@example.com",
                hashed_password=hash_password("password123"),
            ),
            User(
                username="bob",
                email="bob@example.com",
                hashed_password=hash_password("password123"),
            ),
        ]

        for user in users:
            session.add(user)

        session.commit()
        print(f"✓ Successfully seeded {len(users)} users!")
        print("  - Username: alice, Password: password123")
        print("  - Username: bob, Password: password123")


def seed_all():
    """Seed all development data"""
    print("\n=== Seeding Development Data ===\n")
    seed_users()
    print("\n=== Seeding Complete ===\n")


if __name__ == "__main__":
    seed_all()
