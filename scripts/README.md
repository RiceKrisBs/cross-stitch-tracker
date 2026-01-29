# Database Scripts

This directory contains scripts for managing the database.

## Scripts

### seed_floss_colors.py
Seeds the FlossColor table with all DMC colors (~449 colors).

```bash
python scripts/seed_floss_colors.py
```

### seed_dev_data.py
Seeds the database with development/example data:
- 2 test users (alice and bob, both with password "password123")

```bash
python scripts/seed_dev_data.py
```

### reset_db.py
**Warning: Destructive operation!**

Drops all tables, recreates them, and reseeds with both reference data and development data.

```bash
# Interactive (asks for confirmation)
python scripts/reset_db.py

# Force without confirmation
python scripts/reset_db.py --force
```

## Usage

### Initial Setup
After creating the virtual environment and installing dependencies:

1. Create tables and seed with DMC colors:
   ```bash
   python scripts/seed_floss_colors.py
   ```

2. Seed development data:
   ```bash
   python scripts/seed_dev_data.py
   ```

### During Development
If you need to reset the database:

```bash
python scripts/reset_db.py
```

This will drop all data and reseed with fresh data.
