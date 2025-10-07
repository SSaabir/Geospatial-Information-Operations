"""No-op weather_api placeholder.

This file exists to avoid import errors after removing the weather endpoints.
It intentionally does not register any FastAPI router.
"""

# Intentionally empty. If you want the weather endpoints restored, replace this
# file with an APIRouter implementation and include it in main.py.

__all__ = []
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from ..db_config import get_database_session
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

weather_router = APIRouter(prefix="/weather", tags=["Weather"])


def row_to_latest(row: dict) -> Dict[str, Any]:
    return {
        "time": str(row.get("datetime")),
        "temp": row.get("temp"),
        "humidity": row.get("humidity"),
        "wind": row.get("windspeed"),
    }


@weather_router.get("/latest")
def get_latest_weather():
    """Return the most recent weather record for dashboard."""
    try:
        session = get_database_session()
        # Attempt to read a recent record from weather_data if table exists
        try:
            res = session.execute("SELECT * FROM weather_data ORDER BY datetime DESC LIMIT 24")
            rows = [dict(r) for r in res.fetchall()]
            session.close()
            if rows:
                # map to simple array expected by frontend
                return [row_to_latest(r) for r in rows]
        except Exception as e:
            logger.debug(f"weather table query failed: {e}")
            session.close()

    except Exception as e:
        logger.error(f"DB access error in get_latest_weather: {e}")

    # Fallback demo data
    now = datetime.utcnow()
    fallback = []
    for i in range(24):
        t = now - timedelta(hours=23 - i)
        fallback.append({"time": t.isoformat(), "temp": 28 + (i % 5), "humidity": 65, "wind": 10})
    return fallback


@weather_router.get("/weekly")
def get_weekly():
    """Return a weekly summary (7 days)"""
    try:
        session = get_database_session()
        try:
            res = session.execute("SELECT date(datetime) as day, avg(temp) as temp, avg(windspeed) as wind, sum(rainsum) as rainfall FROM weather_data GROUP BY date(datetime) ORDER BY day DESC LIMIT 7")
            rows = [dict(r) for r in res.fetchall()]
            session.close()
            if rows:
                return list(reversed([{"day": str(r["day"]), "temp": float(r.get("temp") or 0), "wind": float(r.get("wind") or 0), "rainfall": float(r.get("rainfall") or 0)} for r in rows]))
        except Exception as e:
            logger.debug(f"weekly query failed: {e}")
            session.close()
    except Exception as e:
        logger.error(f"DB access error in get_weekly: {e}")

    # Fallback weekly
    fallback = []
    for d in range(7):
        day = (datetime.utcnow() - timedelta(days=6 - d)).date().isoformat()
        fallback.append({"day": day, "temp": 28 + d % 3, "wind": 8 + d % 2, "rainfall": 0.0})
    return fallback


@weather_router.get("/regions")
def get_regions():
    """Return simple regional distribution for pie chart"""
    try:
        session = get_database_session()
        try:
            res = session.execute("SELECT statedistrict as name, count(*) as cnt FROM weather_data GROUP BY statedistrict ORDER BY cnt DESC LIMIT 10")
            rows = [dict(r) for r in res.fetchall()]
            session.close()
            if rows:
                total = sum([r.get('cnt', 0) for r in rows]) or 1
                colors = ["#8B5CF6", "#06B6D4", "#F59E0B", "#EF4444", "#10B981", "#6366F1", "#A78BFA", "#F472B6", "#60A5FA", "#F97316"]
                out = []
                for i, r in enumerate(rows):
                    val = round((r.get('cnt', 0) / total) * 100, 1)
                    out.append({"name": r.get('name') or 'Unknown', "value": val, "color": colors[i % len(colors)]})
                return out
        except Exception as e:
            logger.debug(f"regions query failed: {e}")
            session.close()
    except Exception as e:
        logger.error(f"DB access error in get_regions: {e}")

    # Fallback regions
    return [
        {"name": "Colombo", "value": 45.0, "color": "#8B5CF6"},
        {"name": "Kandy", "value": 20.0, "color": "#06B6D4"},
        {"name": "Galle", "value": 12.0, "color": "#F59E0B"},
        {"name": "Jaffna", "value": 8.0, "color": "#EF4444"},
        {"name": "Other", "value": 15.0, "color": "#10B981"},
    ]


@weather_router.get("/alerts")
def get_alerts():
    """Return recent alerts (mocked)"""
    try:
        # For now, attempt to read from a possible alerts table
        session = get_database_session()
        try:
            res = session.execute("SELECT id, message, type, created_at FROM weather_alerts ORDER BY created_at DESC LIMIT 10")
            rows = [dict(r) for r in res.fetchall()]
            session.close()
            if rows:
                out = []
                for r in rows:
                    out.append({"id": r.get('id'), "message": r.get('message'), "type": r.get('type') or 'info', "time": str(r.get('created_at'))})
                return out
        except Exception:
            session.close()
    except Exception as e:
        logger.error(f"DB access error in get_alerts: {e}")

    # fallback alerts
    return [
        {"id": 1, "message": "Light showers expected tomorrow in Colombo.", "type": "info", "time": datetime.utcnow().isoformat()},
        {"id": 2, "message": "High UV index today - take care.", "type": "warning", "time": datetime.utcnow().isoformat()},
    ]
