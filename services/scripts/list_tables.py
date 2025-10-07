"""Utility: list tables in the configured database.

Usage:
    python scripts/list_tables.py

This uses the project's `db_config` to get the engine and list tables.
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from db_config import DatabaseConfig
from sqlalchemy import inspect


def main():
    cfg = DatabaseConfig()
    try:
        engine = cfg.get_engine()
    except Exception as e:
        print("Failed to create DB engine:", e)
        sys.exit(1)

    insp = inspect(engine)
    tables = insp.get_table_names()
    if not tables:
        print("No tables found in database.")
        return

    print("Tables in database:")
    for t in tables:
        print(" -", t)


if __name__ == '__main__':
    main()
