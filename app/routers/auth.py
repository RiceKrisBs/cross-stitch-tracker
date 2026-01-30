"""
Authentication routes: registration, login, logout
"""

from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Form, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.auth import authenticate_user, create_session, delete_session, get_current_user_optional, hash_password
from app.config import settings
from app.database import get_session
from app.models import User

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")


class UserRegister(BaseModel):
    """User registration request"""

    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """User login request"""

    username: str
    password: str


@router.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
    user: User | None = Depends(get_current_user_optional),
):
    """Registration page"""
    # If already logged in, redirect to home
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(request, "auth/register.html")


@router.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    username: Annotated[str, Form()],
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    session: Session = Depends(get_session),
):
    """Register a new user"""
    error = None

    # Validate input
    if not username or len(username) < 3:
        error = "Username must be at least 3 characters"
    elif not email or "@" not in email:
        error = "Invalid email address"
    elif not password or len(password) < 8:
        error = "Password must be at least 8 characters"
    else:
        # Hash password
        hashed_password = hash_password(password)

        # Create user
        user = User(username=username, email=email, hashed_password=hashed_password)

        try:
            session.add(user)
            session.commit()
            session.refresh(user)

            # Create session and set cookie
            session_id = create_session(user.id)
            response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
            response.set_cookie(
                key="session_id",
                value=session_id,
                httponly=True,
                secure=settings.cookie_secure,  # SECURITY: True in production (HTTPS)
                max_age=60 * 60 * 24 * 7,  # 7 days
                samesite="lax",
            )
            return response
        except IntegrityError:
            session.rollback()
            error = "Username or email already exists"

    # If we got here, there was an error - re-render form with error
    return templates.TemplateResponse(
        request,
        "auth/register.html",
        {"error": error, "username": username, "email": email},
        status_code=400,
    )


@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    user: User | None = Depends(get_current_user_optional),
):
    """Login page"""
    # If already logged in, redirect to home
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(request, "auth/login.html")


@router.post("/login", response_class=HTMLResponse)
async def login_user(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    session: Session = Depends(get_session),
):
    """Login a user"""
    user = authenticate_user(username, password, session)

    if not user:
        # Re-render login form with error message
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {"error": "Invalid username or password", "username": username},
            status_code=401,
        )

    # Create session and set cookie
    session_id = create_session(user.id)
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=settings.cookie_secure,  # SECURITY: True in production (HTTPS)
        max_age=60 * 60 * 24 * 7,  # 7 days
        samesite="lax",
    )

    return response


@router.post("/logout")
async def logout_user(
    session_id: Annotated[str | None, Cookie()] = None,
):
    """Logout a user"""
    # SECURITY: Read session_id from cookie, not form data
    # This prevents attackers from logging out other users
    if session_id:
        delete_session(session_id)

    response = RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="session_id")

    return response
