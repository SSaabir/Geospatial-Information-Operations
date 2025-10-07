"""Dump recent events from audit/usage tables for quick verification"""
from db_config import DatabaseConfig
import json
import logging

logger = logging.getLogger(__name__)


def dump(table, limit=10):
    # Whitelist allowed table names to avoid SQL injection risks
    allowed = {
        'api_access_log',
        'auth_events',
        'usage_metrics',
        'payments',
        'checkout_sessions'
    }
    if table not in allowed:
        raise ValueError(f"Table '{table}' is not allowed for dumping")

    db_config = DatabaseConfig()
    engine = db_config.get_engine()
    with engine.connect() as conn:
        try:
            # Use parameterized limit where possible; build query using safe table name
            q = f"SELECT * FROM {table} ORDER BY created_at DESC NULLS LAST LIMIT :limit"
            res = conn.execute(q, {"limit": int(limit)})
            rows = [dict(r) for r in res]
            print(f"--- {table} (last {limit}) ---")
            print(json.dumps(rows, default=str, indent=2))
        except Exception as e:
            logger.exception("Failed to query table %s: %s", table, e)
            print(f"Failed to dump {table}: {e}")


if __name__ == '__main__':
    tables = [
        'api_access_log',
        'auth_events',
        'usage_metrics',
        'payments',
        'checkout_sessions'
    ]
    for t in tables:
        try:
            dump(t, limit=10)
        except Exception as e:
            print(f"Failed to dump {t}: {e}")
