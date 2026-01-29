"""
Reset database: drop all tables, recreate, and reseed with data
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.append(str(Path(__file__).parent.parent))

from seed_dev_data import seed_all as seed_dev_data

# Import seed scripts
from seed_floss_colors import seed_dmc_colors
from sqlmodel import SQLModel

from app.database import engine


def reset_database():
    """Drop all tables, recreate them, and reseed with data"""
    print("\n=== Resetting Database ===\n")

    # Drop all tables
    print("Dropping all tables...")
    SQLModel.metadata.drop_all(engine)
    print("✓ Tables dropped")

    # Create all tables
    print("Creating all tables...")
    SQLModel.metadata.create_all(engine)
    print("✓ Tables created")

    # Seed reference data
    print("\nSeeding reference data...")
    seed_dmc_colors()

    # Seed development data
    print("\nSeeding development data...")
    seed_dev_data()

    print("\n=== Database Reset Complete ===\n")


if __name__ == "__main__":
    import sys

    # Ask for confirmation
    if "--force" not in sys.argv:
        response = input("This will DELETE ALL DATA. Are you sure? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            sys.exit(0)

    reset_database()
