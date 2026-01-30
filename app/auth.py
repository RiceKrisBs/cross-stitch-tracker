"""
Authentication utilities for password hashing and session management
"""

from datetime import datetime, timedelta, UTC
from typing import Annotated

import bcrypt
from fastapi import Cookie, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import User

# Session storage (in-memory for simplicity)
# In production, consider using Redis or database-backed sessions
sessions: dict[str, dict] = {}

# Session expiry time (7 days)
SESSION_EXPIRY = timedelta(days=7)


def hash_password(password: str) -> str:
    """Hash a plain text password"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_session(user_id: int) -> str:
    """Create a new session for a user and return the session ID"""
    import secrets

    session_id = secrets.token_urlsafe(32)
    now = datetime.now(UTC)
    sessions[session_id] = {
        "user_id": user_id,
        "created_at": now,
        "expires_at": now + SESSION_EXPIRY,
    }
    return session_id


def get_session_user(session_id: str | None) -> int | None:
    """Get user ID from session ID, return None if invalid or expired"""
    if not session_id or session_id not in sessions:
        return None

    session_data = sessions[session_id]
    if datetime.now(UTC) > session_data["expires_at"]:
        # Session expired, remove it
        del sessions[session_id]
        return None

    return session_data["user_id"]


def delete_session(session_id: str) -> None:
    """Delete a session (for logout)"""
    if session_id in sessions:
        del sessions[session_id]


def authenticate_user(username: str, password: str, session: Session) -> User | None:
    """Authenticate a user by username and password"""
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()

    # SECURITY: Always verify password even if user doesn't exist
    # This prevents timing attacks that could enumerate valid usernames
    if not user:
        # Perform a dummy password check to match timing of real check
        verify_password(password, "$2b$12$1zs8Pl0YLpwA/Egb4Vdd6ujks3j9Y2eSWjiL9jq2Uc5zuk.9Mr5aS")
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


async def get_current_user(
    session_id: Annotated[str | None, Cookie()] = None,
    session: Session = Depends(get_session),
) -> User:
    """
    Dependency to get the current authenticated user from session.
    Raises 401 if not authenticated.
    """
    user_id = get_session_user(session_id)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


async def get_current_user_optional(
    session_id: Annotated[str | None, Cookie()] = None,
    session: Session = Depends(get_session),
) -> User | None:
    """
    Dependency to get the current authenticated user from session.
    Returns None if not authenticated (doesn't raise exception).
    """
    user_id = get_session_user(session_id)

    if not user_id:
        return None

    user = session.get(User, user_id)
    return user
