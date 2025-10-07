"""Utility: export database schema to SQL CREATE TABLE statements.

Usage:
    python scripts/export_schema.py

This uses the project's `db_config` to get the engine and export schemas.
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from db_config import DatabaseConfig
from sqlalchemy import inspect, MetaData, Table, Column
from sqlalchemy.sql.sqltypes import *
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_sql_type(col_type):
    """Convert SQLAlchemy column type to SQL string."""
    if isinstance(col_type, Integer):
        return "INTEGER"
    elif isinstance(col_type, String):
        return f"VARCHAR({col_type.length})" if col_type.length else "TEXT"
    elif isinstance(col_type, Text):
        return "TEXT"
    elif isinstance(col_type, Float):
        return "FLOAT"
    elif isinstance(col_type, Boolean):
        return "BOOLEAN"
    elif isinstance(col_type, DateTime):
        return "TIMESTAMP"
    elif isinstance(col_type, Date):
        return "DATE"
    elif isinstance(col_type, Time):
        return "TIME"
    else:
        return str(col_type)

def export_schema():
    cfg = DatabaseConfig()
    try:
        engine = cfg.get_engine()
    except Exception as e:
        print("Failed to create DB engine:", e)
        sys.exit(1)

    insp = inspect(engine)
    tables = insp.get_table_names()

    with open('data/PstDB.sql', 'w') as f:
        for table_name in sorted(tables):
            columns = insp.get_columns(table_name)
            pks = insp.get_pk_constraint(table_name)['constrained_columns']

            f.write(f"CREATE TABLE {table_name} (\n")
            col_defs = []
            for col in columns:
                col_type = get_sql_type(col['type'])
                nullable = "" if col['nullable'] else " NOT NULL"
                pk = " PRIMARY KEY" if col['name'] in pks else ""
                col_defs.append(f"    {col['name']} {col_type}{nullable}{pk}")
            f.write(",\n".join(col_defs))
            f.write("\n);\n\n")

    print("Schema exported to data/PstDB.sql")

if __name__ == '__main__':
    export_schema()