"""
Tests for authentication system
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.auth import (
    authenticate_user,
    create_session,
    delete_session,
    get_session_user,
    hash_password,
    sessions,
    verify_password,
)
from app.models import User


# Password hashing tests


def test_hash_password():
    """Test password hashing"""
    password = "testpassword123"
    hashed = hash_password(password)

    # Hash should be different from original
    assert hashed != password
    # Hash should have reasonable length
    assert len(hashed) > 20


def test_verify_password():
    """Test password verification"""
    password = "testpassword123"
    hashed = hash_password(password)

    # Correct password should verify
    assert verify_password(password, hashed) is True

    # Wrong password should not verify
    assert verify_password("wrongpassword", hashed) is False


def test_hash_password_different_each_time():
    """Test that hashing same password produces different hashes (salt)"""
    password = "testpassword123"
    hash1 = hash_password(password)
    hash2 = hash_password(password)

    # Hashes should be different (salted)
    assert hash1 != hash2

    # But both should verify
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True


# Session management tests


def test_create_session():
    """Test session creation"""
    user_id = 1
    session_id = create_session(user_id)

    # Session ID should be returned
    assert session_id is not None
    assert len(session_id) > 0

    # Session should be stored
    assert session_id in sessions
    assert sessions[session_id]["user_id"] == user_id


def test_get_session_user():
    """Test getting user from session"""
    user_id = 42
    session_id = create_session(user_id)

    # Should return correct user ID
    retrieved_user_id = get_session_user(session_id)
    assert retrieved_user_id == user_id


def test_get_session_user_invalid():
    """Test getting user from invalid session"""
    # Non-existent session should return None
    assert get_session_user("invalid_session_id") is None
    assert get_session_user(None) is None


def test_delete_session():
    """Test session deletion"""
    user_id = 1
    session_id = create_session(user_id)

    # Session should exist
    assert session_id in sessions

    # Delete session
    delete_session(session_id)

    # Session should be gone
    assert session_id not in sessions
    assert get_session_user(session_id) is None


# User authentication tests


def test_authenticate_user_success(session: Session):
    """Test successful user authentication"""
    # Create a user
    password = "testpassword123"
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password(password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Authenticate with correct credentials
    authenticated_user = authenticate_user("testuser", password, session)

    assert authenticated_user is not None
    assert authenticated_user.username == "testuser"
    assert authenticated_user.id == user.id


def test_authenticate_user_wrong_password(session: Session):
    """Test authentication with wrong password"""
    # Create a user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("correctpassword"),
    )
    session.add(user)
    session.commit()

    # Authenticate with wrong password
    authenticated_user = authenticate_user("testuser", "wrongpassword", session)

    assert authenticated_user is None


def test_authenticate_user_nonexistent(session: Session):
    """Test authentication with non-existent username"""
    authenticated_user = authenticate_user("nonexistent", "password", session)
    assert authenticated_user is None


# Registration endpoint tests


def test_register_user_success(client: TestClient, session: Session):
    """Test successful user registration"""
    response = client.post(
        "/auth/register",
        data={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
        },
        follow_redirects=False,
    )

    # Should redirect to home
    assert response.status_code == 302
    assert response.headers["location"] == "/"

    # Should set session cookie
    assert "session_id" in response.cookies

    # User should be created in database
    from sqlmodel import select

    statement = select(User).where(User.username == "newuser")
    user = session.exec(statement).first()

    assert user is not None
    assert user.username == "newuser"
    assert user.email == "newuser@example.com"
    # Password should be hashed, not stored as plain text
    assert user.hashed_password != "password123"


def test_register_user_duplicate_username(client: TestClient, session: Session):
    """Test registration with duplicate username"""
    # Create existing user
    user = User(
        username="existing",
        email="existing@example.com",
        hashed_password=hash_password("password"),
    )
    session.add(user)
    session.commit()

    # Try to register with same username
    response = client.post(
        "/auth/register",
        data={
            "username": "existing",
            "email": "newemail@example.com",
            "password": "password123",
        },
    )

    # Should fail with HTML response
    assert response.status_code == 400
    assert "already exists" in response.text.lower()


def test_register_user_short_username(client: TestClient):
    """Test registration with too short username"""
    response = client.post(
        "/auth/register",
        data={
            "username": "ab",  # Too short
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 400
    assert "username" in response.text.lower()


def test_register_user_short_password(client: TestClient):
    """Test registration with too short password"""
    response = client.post(
        "/auth/register",
        data={
            "username": "testuser",
            "email": "test@example.com",
            "password": "pass",  # Too short
        },
    )

    assert response.status_code == 400
    assert "password" in response.text.lower()


def test_register_user_invalid_email(client: TestClient):
    """Test registration with invalid email"""
    response = client.post(
        "/auth/register",
        data={
            "username": "testuser",
            "email": "notanemail",  # Invalid
            "password": "password123",
        },
    )

    assert response.status_code == 400
    assert "email" in response.text.lower()


# Login endpoint tests


def test_login_user_success(client: TestClient, session: Session):
    """Test successful user login"""
    # Create a user
    password = "testpassword123"
    user = User(
        username="loginuser",
        email="login@example.com",
        hashed_password=hash_password(password),
    )
    session.add(user)
    session.commit()

    # Login
    response = client.post(
        "/auth/login",
        data={
            "username": "loginuser",
            "password": password,
        },
        follow_redirects=False,
    )

    # Should redirect to home
    assert response.status_code == 302
    assert response.headers["location"] == "/"

    # Should set session cookie
    assert "session_id" in response.cookies


def test_login_user_wrong_password(client: TestClient, session: Session):
    """Test login with wrong password"""
    # Create a user
    user = User(
        username="loginuser",
        email="login@example.com",
        hashed_password=hash_password("correctpassword"),
    )
    session.add(user)
    session.commit()

    # Try to login with wrong password
    response = client.post(
        "/auth/login",
        data={
            "username": "loginuser",
            "password": "wrongpassword",
        },
    )

    # Should fail with HTML response
    assert response.status_code == 401
    assert "invalid" in response.text.lower()


def test_login_user_nonexistent(client: TestClient):
    """Test login with non-existent username"""
    response = client.post(
        "/auth/login",
        data={
            "username": "nonexistent",
            "password": "password123",
        },
    )

    # Should fail with HTML response
    assert response.status_code == 401
    assert "invalid" in response.text.lower()


# Logout endpoint tests


def test_logout_user(client: TestClient, session: Session):
    """Test user logout"""
    # Create a user and session
    user = User(
        username="logoutuser",
        email="logout@example.com",
        hashed_password=hash_password("password"),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    session_id = create_session(user.id)

    # Logout - session_id now read from cookie, not form data (security fix)
    response = client.post(
        "/auth/logout",
        cookies={"session_id": session_id},
        follow_redirects=False,
    )

    # Should redirect to login page
    assert response.status_code == 302
    assert response.headers["location"] == "/auth/login"

    # Session should be deleted
    assert get_session_user(session_id) is None


# Protected route tests (middleware/dependency)


def test_get_current_user_authenticated(session: Session):
    """Test getting current user when authenticated"""
    # Create a user and session
    user = User(
        username="authuser",
        email="auth@example.com",
        hashed_password=hash_password("password"),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    session_id = create_session(user.id)

    # Make a request with session cookie
    # We'll need to add a protected endpoint first in the app
    # For now, just test the auth functions directly
    user_id = get_session_user(session_id)
    assert user_id == user.id


def test_get_current_user_not_authenticated():
    """Test getting current user when not authenticated"""
    # No session cookie
    user_id = get_session_user(None)
    assert user_id is None


# Registration and login page tests


def test_register_page(client: TestClient):
    """Test registration page loads"""
    response = client.get("/auth/register")
    assert response.status_code == 200
    assert "register" in response.text.lower()


def test_login_page(client: TestClient):
    """Test login page loads"""
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert "login" in response.text.lower()


def test_register_page_redirect_if_logged_in(client: TestClient, session: Session):
    """Test that registration page redirects if already logged in"""
    # Create a user and session
    user = User(
        username="loggedinuser",
        email="loggedin@example.com",
        hashed_password=hash_password("password"),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    session_id = create_session(user.id)

    # Try to access register page with session cookie
    response = client.get(
        "/auth/register",
        cookies={"session_id": session_id},
        follow_redirects=False,
    )

    # Should redirect to home
    assert response.status_code == 302
    assert response.headers["location"] == "/"


def test_login_page_redirect_if_logged_in(client: TestClient, session: Session):
    """Test that login page redirects if already logged in"""
    # Create a user and session
    user = User(
        username="loggedinuser",
        email="loggedin@example.com",
        hashed_password=hash_password("password"),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    session_id = create_session(user.id)

    # Try to access login page with session cookie
    response = client.get(
        "/auth/login",
        cookies={"session_id": session_id},
        follow_redirects=False,
    )

    # Should redirect to home
    assert response.status_code == 302
    assert response.headers["location"] == "/"
