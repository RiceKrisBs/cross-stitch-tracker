"""
Database configuration and session management
"""

from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

# SQLite database URL
DATABASE_URL = "sqlite:///./data/cross_stitch_tracker.db"

# Create engine with echo for development (shows SQL queries)
engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False},  # Needed for SQLite
)


def create_db_and_tables():
    """Create all database tables"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session]:
    """
    Dependency for getting database sessions.
    Use with FastAPI's Depends().
    """
    with Session(engine) as session:
        yield session
