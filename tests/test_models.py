"""
Tests for database models
"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.models import FlossColor, User


def test_create_user(session: Session):
    """Test creating a user"""
    user = User(
        username="testuser", email="test@example.com", hashed_password="hashed_password_here"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.created_at is not None
    assert user.updated_at is not None


def test_create_floss_color(session: Session):
    """Test creating a floss color"""
    floss = FlossColor(brand="DMC", color_number="310", color_name="Black", hex_color="#000000")
    session.add(floss)
    session.commit()
    session.refresh(floss)

    assert floss.id is not None
    assert floss.brand == "DMC"
    assert floss.color_number == "310"
    assert floss.color_name == "Black"
    assert floss.hex_color == "#000000"


def test_floss_color_unique_constraint(session: Session):
    """Test that brand+color_number must be unique"""
    floss1 = FlossColor(brand="DMC", color_number="310", color_name="Black")
    session.add(floss1)
    session.commit()

    # Try to add duplicate
    floss2 = FlossColor(brand="DMC", color_number="310", color_name="Also Black")
    session.add(floss2)

    with pytest.raises(IntegrityError):
        session.commit()


def test_user_unique_username(session: Session):
    """Test that username must be unique"""
    user1 = User(username="testuser", email="test1@example.com", hashed_password="hash1")
    session.add(user1)
    session.commit()

    # Try to add duplicate username
    user2 = User(username="testuser", email="test2@example.com", hashed_password="hash2")
    session.add(user2)

    with pytest.raises(IntegrityError):
        session.commit()
