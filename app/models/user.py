"""
User model
"""

from sqlmodel import Field

from .base import TimestampMixin


class User(TimestampMixin, table=True):
    """User model for authentication and data ownership"""

    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, max_length=50)
    email: str = Field(unique=True, index=True, max_length=100)
    hashed_password: str = Field(max_length=255)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"
