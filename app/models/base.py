"""
Base model classes and mixins
"""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


def utc_now():
    """Return current UTC time"""
    return datetime.now(UTC)


class TimestampMixin(SQLModel):
    """Mixin to add created_at and updated_at timestamps to models"""

    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=utc_now, nullable=False)
