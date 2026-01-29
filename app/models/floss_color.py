"""
FlossColor model - reference table for all available floss colors
"""

from sqlmodel import Field, UniqueConstraint

from .base import TimestampMixin


class FlossColor(TimestampMixin, table=True):
    """
    Reference table for all available floss colors.
    Pre-populated with DMC colors, can be extended with other brands.
    """

    __tablename__ = "floss_colors"
    __table_args__ = (UniqueConstraint("brand", "color_number", name="unique_brand_color"),)

    id: int | None = Field(default=None, primary_key=True)
    brand: str = Field(index=True, max_length=50)  # e.g., "DMC", "Anchor"
    color_number: str = Field(index=True, max_length=20)  # e.g., "310", "B5200"
    color_name: str | None = Field(default=None, max_length=100)  # e.g., "Black"
    hex_color: str | None = Field(default=None, max_length=7)  # e.g., "#000000"

    def __repr__(self):
        return f"<FlossColor(id={self.id}, brand='{self.brand}', number='{self.color_number}', name='{self.color_name}')>"
