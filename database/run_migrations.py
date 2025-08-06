#!/usr/bin/env python3
"""
Migration Runner Script
Applies or rolls back database migrations
"""

import os
import sys
from pathlib import Path

def run_migration(direction, migration_name=None):
    """Run a migration in the specified direction"""
    migrations_dir = Path(__file__).parent / "database" / "migrations"
    
    if direction == "up":
        # Apply all migrations
        up_dir = migrations_dir / "up"
        for migration_file in sorted(up_dir.glob("*.sql")):
            print(f"Applying {migration_file.name}...")
            # Here you would run the SQL against your database
            # For now, just print the file content
            with open(migration_file, 'r') as f:
                print(f.read())
    
    elif direction == "down":
        # Rollback migrations
        down_dir = migrations_dir / "down"
        if migration_name:
            down_file = down_dir / f"{migration_name}.sql"
            if down_file.exists():
                print(f"Rolling back {migration_name}...")
                with open(down_file, 'r') as f:
                    print(f.read())
        else:
            # Rollback all migrations in reverse order
            for migration_file in sorted(down_dir.glob("*.sql"), reverse=True):
                print(f"Rolling back {migration_file.name}...")
                with open(migration_file, 'r') as f:
                    print(f.read())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_migrations.py [up|down] [migration_name]")
        sys.exit(1)
    
    direction = sys.argv[1]
    migration_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    run_migration(direction, migration_name)
