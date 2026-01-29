"""
Seed FlossColor table with DMC colors
"""

import json
import sys
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.append(str(Path(__file__).parent.parent))

from sqlmodel import Session, select

from app.database import engine
from app.models import FlossColor


def seed_dmc_colors():
    """Load DMC colors from JSON and insert into database"""

    # Load DMC colors from JSON file
    json_path = Path(__file__).parent.parent / "data" / "dmc_colors.json"
    with open(json_path) as f:
        dmc_colors = json.load(f)

    with Session(engine) as session:
        # Check if colors already exist
        statement = select(FlossColor).where(FlossColor.brand == "DMC")
        existing_count = len(session.exec(statement).all())

        if existing_count > 0:
            print(f"DMC colors already seeded ({existing_count} colors found). Skipping...")
            return

        # Insert all DMC colors
        print(f"Seeding {len(dmc_colors)} DMC colors...")

        for color_data in dmc_colors:
            floss = FlossColor(
                brand="DMC",
                color_number=color_data["color_number"],
                color_name=color_data["color_name"],
                hex_color=color_data["hex_color"],
            )
            session.add(floss)

        session.commit()
        print(f"✓ Successfully seeded {len(dmc_colors)} DMC colors!")


if __name__ == "__main__":
    seed_dmc_colors()
