"""Notification manager utility

Provides a small, reusable NotificationManager that supports sending
notifications via email, webhook, and storing notification records to
the database (if a SQLAlchemy engine is provided).

Usage:
    from services.utils.notification_manager import get_notification_manager
    nm = get_notification_manager()
    nm.notify(subject='Test', message='Hello', level='info', extra={})

Environment variables used (optional):
  - SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD
  - DEFAULT_NOTIFICATION_EMAIL
  - GLOBAL_WEBHOOK_URL
"""

import os
import json
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from datetime import datetime

import requests

logger = logging.getLogger(__name__)


class NotificationManager:
    """Simple notification manager supporting email, webhook and DB storage."""

    def __init__(self, engine=None):
        # DB engine (optional) for storing notifications
        self.engine = engine

        # Email configuration
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587)) if os.getenv('SMTP_PORT') else None
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.default_email = os.getenv('DEFAULT_NOTIFICATION_EMAIL', 'alerts@localhost')

        # Webhook
        self.webhook_url = os.getenv('GLOBAL_WEBHOOK_URL')

    def notify(self, subject: str, message: str, level: str = 'info', to_email: Optional[str] = None, webhook_url: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None, user_id: Optional[int] = None):
        """Send a notification through available channels.

        Channels tried (in order): email (if configured), webhook (if configured), DB store (if engine provided).
        """
        metadata = metadata or {}
        timestamp = datetime.utcnow().isoformat()

        # Try email
        if self.smtp_server and self.smtp_username and self.smtp_password:
            try:
                self._send_email(subject, message, to_email or self.default_email)
            except Exception as e:
                logger.error(f"Failed to send notification email: {e}")

        # Try webhook
        url = webhook_url or self.webhook_url
        if url:
            try:
                self._send_webhook(url, subject, message, level, metadata)
            except Exception as e:
                logger.error(f"Failed to send notification webhook: {e}")

        # Try DB store
        if self.engine:
            try:
                self._store_notification(subject, message, level, metadata, timestamp, user_id)
            except Exception as e:
                logger.error(f"Failed to store notification to DB: {e}")

    def _send_email(self, subject: str, body: str, to_email: str):
        msg = MIMEMultipart()
        msg['From'] = self.smtp_username
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(self.smtp_server, self.smtp_port or 587) as server:
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)

        logger.info(f"Notification email sent to {to_email}: {subject}")

    def _send_webhook(self, url: str, subject: str, message: str, level: str, metadata: Dict[str, Any]):
        payload = {
            'type': 'notification',
            'level': level,
            'subject': subject,
            'message': message,
            'metadata': metadata,
            'timestamp': datetime.utcnow().isoformat()
        }

        resp = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=10)
        if resp.status_code >= 200 and resp.status_code < 300:
            logger.info(f"Notification webhook sent to {url}: {subject}")
        else:
            logger.error(f"Webhook returned status {resp.status_code}: {resp.text}")

    def _store_notification(self, subject: str, message: str, level: str, metadata: Dict[str, Any], timestamp: str, user_id: Optional[int] = None):
        # Attempt to insert into a notifications table. If table doesn't exist, create a lightweight one.
        try:
            from sqlalchemy import text
            with self.engine.connect() as conn:
                # Create table if missing (simple portable SQL for Postgres)
                create_table_sql = text("""
                    CREATE TABLE IF NOT EXISTS notifications (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP,
                        level VARCHAR(20),
                        subject VARCHAR(255),
                        message TEXT,
                        metadata JSONB,
                        read BOOLEAN DEFAULT false,
                        user_id INTEGER REFERENCES users(id)
                    )
                """)
                conn.execute(create_table_sql)
                
                insert_sql = text("""
                    INSERT INTO notifications (timestamp, level, subject, message, metadata, user_id)
                    VALUES (:timestamp, :level, :subject, :message, :metadata, :user_id)
                """)
                conn.execute(insert_sql, {
                    'timestamp': timestamp,
                    'level': level,
                    'subject': subject,
                    'message': message,
                    'metadata': json.dumps(metadata),
                    'user_id': user_id
                })
                conn.commit()

            logger.info(f"Notification stored in DB: {subject}")
        except Exception as e:
            # If DB operations fail, log and move on
            logger.error(f"DB notification store failed: {e}")


# Singleton accessor
_notification_manager_instance: Optional[NotificationManager] = None


def get_notification_manager(engine=None) -> NotificationManager:
    global _notification_manager_instance
    if _notification_manager_instance is None:
        _notification_manager_instance = NotificationManager(engine=engine)
    elif engine is not None and _notification_manager_instance.engine is None:
        # Update engine if one is provided and instance doesn't have one
        _notification_manager_instance.engine = engine
    return _notification_manager_instance


def notify(subject: str, message: str, level: str = 'info', to_email: Optional[str] = None, webhook_url: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None, engine=None, user_id: Optional[int] = None):
    # Auto-fetch engine from db_config if not provided
    if engine is None:
        try:
            from db_config import DatabaseConfig
            db_config = DatabaseConfig()
            engine = db_config.get_engine()
        except Exception as e:
            logger.debug(f"Could not auto-fetch database engine: {e}")
            engine = None
    
    nm = get_notification_manager(engine=engine)
    nm.notify(subject=subject, message=message, level=level, to_email=to_email, webhook_url=webhook_url, metadata=metadata, user_id=user_id)
