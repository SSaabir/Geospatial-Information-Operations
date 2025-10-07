"""Idempotent DB table creation and seeding for audit/usage and payments.

Call create_tables_and_seed(engine) on startup to ensure the tables exist and
that a few sample rows are present for smoke-testing / local dev.
"""
from sqlalchemy import text
import logging
from db_config import db_config

logger = logging.getLogger(__name__)


def create_tables_and_seed():
    engine = db_config.get_engine()
    with engine.begin() as conn:
        # Create tables if they don't exist (simple DDL compatible with PostgreSQL)
        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS api_access_log (
                id BIGSERIAL PRIMARY KEY,
                endpoint TEXT,
                method VARCHAR(10),
                user_id BIGINT,
                ip_address TEXT,
                user_agent TEXT,
                response_code INTEGER,
                response_time DOUBLE PRECISION,
                request_size INTEGER,
                response_size INTEGER,
                threat_score DOUBLE PRECISION,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            """
        ))

        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS auth_events (
                id BIGSERIAL PRIMARY KEY,
                event_type TEXT,
                user_id BIGINT,
                ip_address TEXT,
                success BOOLEAN,
                failure_reason TEXT,
                session_id TEXT,
                user_agent TEXT,
                geolocation JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            """
        ))

        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS usage_metrics (
                id BIGSERIAL PRIMARY KEY,
                user_id BIGINT UNIQUE,
                api_calls BIGINT DEFAULT 0,
                reports_generated BIGINT DEFAULT 0,
                data_downloads BIGINT DEFAULT 0,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            """
        ))

        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS payments (
                id BIGSERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
                amount NUMERIC(10,2),
                plan TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP WITH TIME ZONE,
                recurring BOOLEAN DEFAULT FALSE
            );
            """
        ))

        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS checkout_sessions (
                id UUID PRIMARY KEY,
                user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
                plan TEXT,
                amount NUMERIC(10,2),
                recurring BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                paid BOOLEAN DEFAULT FALSE,
                paid_at TIMESTAMP WITH TIME ZONE
            );
            """
        ))

        # Insert sample rows only if tables are empty
        try:
            r = conn.execute(text("SELECT COUNT(*) FROM api_access_log"))
            count = r.scalar() if r is not None else 0
        except Exception:
            count = 0

        if count == 0:
            logger.info("Seeding sample api_access_log rows")
            for i in range(1, 6):
                conn.execute(
                    text(
                        "INSERT INTO api_access_log (endpoint, method, user_id, ip_address, user_agent, response_code, response_time) VALUES (:endpoint, :method, :user_id, :ip_address, :user_agent, :response_code, :response_time)"
                    ),
                    {
                        "endpoint": f"/sample/endpoint/{i}",
                        "method": "GET",
                        "user_id": i,
                        "ip_address": "127.0.0.1",
                        "user_agent": "seed-script",
                        "response_code": 200,
                        "response_time": 0.01 * i,
                    },
                )

            logger.info("Seeding sample auth_events rows")
            for i in range(1, 6):
                conn.execute(
                    text(
                        "INSERT INTO auth_events (event_type, user_id, ip_address, success, failure_reason, session_id, user_agent) VALUES (:event_type, :user_id, :ip_address, :success, :failure_reason, :session_id, :user_agent)"
                    ),
                    {
                        "event_type": "register" if i % 2 == 1 else "login",
                        "user_id": i,
                        "ip_address": "127.0.0.1",
                        "success": True,
                        "failure_reason": None,
                        "session_id": None,
                        "user_agent": "seed-script",
                    },
                )

            logger.info("Seeding sample usage_metrics rows")
            for i in range(1, 6):
                conn.execute(
                    text(
                        "INSERT INTO usage_metrics (user_id, api_calls, reports_generated, data_downloads) VALUES (:user_id, :api_calls, :reports_generated, :data_downloads)"
                    ),
                    {
                        "user_id": i,
                        "api_calls": i * 3,
                        "reports_generated": i % 2,
                        "data_downloads": i,
                    },
                )

            logger.info("Seeding sample payments rows")
            for i in range(1, 6):
                conn.execute(
                    text(
                        "INSERT INTO payments (user_id, amount, plan, expires_at, recurring) VALUES (:user_id, :amount, :plan, CURRENT_TIMESTAMP + INTERVAL '30 days', :recurring)"
                    ),
                    {"user_id": i, "amount": 29.0 if i % 2 == 0 else 0.0, "plan": "researcher" if i % 2 == 0 else "free", "recurring": False},
                )

        logger.info("DB create_tables_and_seed completed")


if __name__ == "__main__":
    create_tables_and_seed()
