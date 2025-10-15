"""
Daily Data Collection API
Provides endpoints to:
- Manually trigger daily data collection
- View collection status and history
- Get latest collected data
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, List
from sqlalchemy import text
from datetime import datetime, date, timedelta
import logging
import sys
import os

# Add schedulers directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'schedulers'))

from security.auth_middleware import get_current_user
from db_config import DatabaseConfig
from models.user import UserDB

# Import collector
try:
    from schedulers.unified_daily_collector import UnifiedDailyCollector
except ImportError:
    UnifiedDailyCollector = None

logger = logging.getLogger(__name__)

daily_data_router = APIRouter(prefix="/api/daily-data", tags=["Daily Data Collection"])

def get_db():
    """Get database connection"""
    db_config = DatabaseConfig()
    return db_config.get_engine()


@daily_data_router.get("/status")
async def get_collection_status(db=Depends(get_db)):
    """Get the status of daily data collection"""
    try:
        with db.connect() as conn:
            # Get latest weather collection
            weather_result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_records,
                    MAX(timestamp) as last_collected,
                    COUNT(DISTINCT city) as locations_count
                FROM weather_data
                WHERE date = CURRENT_DATE
            """)).fetchone()
            
            # Get latest air quality collection
            air_result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_records,
                    MAX(timestamp) as last_collected,
                    COUNT(DISTINCT location) as locations_count
                FROM air_quality_data
                WHERE DATE(timestamp) = CURRENT_DATE
            """)).fetchone()
            
            # Get latest news collection
            news_result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_articles,
                    MAX(published_at) as latest_article,
                    COUNT(DISTINCT source) as sources_count
                FROM news_articles
                WHERE published_at > CURRENT_DATE
            """)).fetchone()
            
            return {
                "success": True,
                "date": date.today().isoformat(),
                "collection_status": {
                    "weather": {
                        "records_today": weather_result[0] if weather_result else 0,
                        "last_collected": weather_result[1].isoformat() if weather_result and weather_result[1] else None,
                        "locations": weather_result[2] if weather_result else 0
                    },
                    "air_quality": {
                        "records_today": air_result[0] if air_result else 0,
                        "last_collected": air_result[1].isoformat() if air_result and air_result[1] else None,
                        "locations": air_result[2] if air_result else 0
                    },
                    "news": {
                        "articles_today": news_result[0] if news_result else 0,
                        "latest_article": news_result[1].isoformat() if news_result and news_result[1] else None,
                        "sources": news_result[2] if news_result else 0
                    }
                }
            }
    except Exception as e:
        logger.error(f"Error getting collection status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@daily_data_router.get("/latest-weather")
async def get_latest_weather(location: str = "Colombo", db=Depends(get_db)):
    """Get latest weather data for a location"""
    try:
        with db.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    city, date, temperature, temp_min, temp_max,
                    humidity, pressure, wind_speed, cloudcover,
                    conditions, description,
                    timestamp
                FROM weather_data
                WHERE city = :location
                ORDER BY date DESC, timestamp DESC
                LIMIT 1
            """), {"location": location}).fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail=f"No weather data found for {location}")
            
            return {
                "success": True,
                "location": result[0],
                "date": result[1].isoformat(),
                "data": {
                    "temperature": result[2],
                    "temp_min": result[3],
                    "temp_max": result[4],
                    "humidity": result[5],
                    "pressure": result[6],
                    "wind_speed": result[7],
                    "cloudiness": result[8],
                    "condition": result[9],
                    "description": result[10]
                },
                "collected_at": result[11].isoformat()
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting latest weather: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@daily_data_router.get("/latest-air-quality")
async def get_latest_air_quality(location: str = "Colombo", db=Depends(get_db)):
    """Get latest air quality data for a location"""
    try:
        with db.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    location, timestamp, pm10, pm2_5,
                    carbon_monoxide, ozone, timestamp
                FROM air_quality_data
                WHERE location = :location
                ORDER BY timestamp DESC
                LIMIT 1
            """), {"location": location}).fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail=f"No air quality data found for {location}")
            
            return {
                "success": True,
                "location": result[0],
                "timestamp": result[1].isoformat(),
                "data": {
                    "pm10": result[2],
                    "pm2_5": result[3],
                    "co": result[4],
                    "ozone": result[5]
                },
                "collected_at": result[6].isoformat()
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting latest air quality: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@daily_data_router.get("/weather-history")
async def get_weather_history(
    location: str = "Colombo",
    days: int = 7,
    db=Depends(get_db)
):
    """Get weather history for a location"""
    try:
        with db.connect() as conn:
            results = conn.execute(text("""
                SELECT 
                    date, temperature, temp_min, temp_max,
                    humidity, pressure, conditions
                FROM weather_data
                WHERE city = :location
                  AND date >= CURRENT_DATE - :days::integer
                ORDER BY date DESC
            """), {"location": location, "days": days}).fetchall()
            
            return {
                "success": True,
                "location": location,
                "days": days,
                "data": [
                    {
                        "date": row[0].isoformat(),
                        "temperature": row[1],
                        "temp_min": row[2],
                        "temp_max": row[3],
                        "humidity": row[4],
                        "pressure": row[5],
                        "condition": row[6]
                    }
                    for row in results
                ]
            }
    except Exception as e:
        logger.error(f"Error getting weather history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@daily_data_router.post("/trigger-collection")
async def trigger_manual_collection(
    background_tasks: BackgroundTasks,
    current_user: UserDB = Depends(get_current_user)
):
    """Manually trigger daily data collection (Admin only)"""
    try:
        # Check admin privileges
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        if UnifiedDailyCollector is None:
            raise HTTPException(status_code=500, detail="Collector module not available")
        
        # Run collection in background
        def run_collection():
            try:
                collector = UnifiedDailyCollector()
                collector.run_daily_collection()
                logger.info(f"Manual collection triggered by {current_user.username}")
            except Exception as e:
                logger.error(f"Background collection failed: {e}")
        
        background_tasks.add_task(run_collection)
        
        return {
            "success": True,
            "message": "Data collection started in background",
            "triggered_by": current_user.username,
            "triggered_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@daily_data_router.get("/all-locations-summary")
async def get_all_locations_summary(db=Depends(get_db)):
    """Get summary of latest data for all locations"""
    try:
        with db.connect() as conn:
            # Get latest weather for all locations
            weather_results = conn.execute(text("""
                SELECT DISTINCT ON (city)
                    city, temperature, humidity, conditions, timestamp
                FROM weather_data
                WHERE date = CURRENT_DATE
                ORDER BY city, timestamp DESC
            """)).fetchall()
            
            # Get latest air quality for all locations
            air_results = conn.execute(text("""
                SELECT DISTINCT ON (location)
                    location, pm10, pm2_5, timestamp
                FROM air_quality_data
                WHERE DATE(timestamp) = CURRENT_DATE
                ORDER BY location, timestamp DESC
            """)).fetchall()
            
            # Combine data by location
            locations_data = {}
            
            for row in weather_results:
                locations_data[row[0]] = {
                    "location": row[0],
                    "weather": {
                        "temperature": row[1],
                        "humidity": row[2],
                        "condition": row[3],
                        "collected_at": row[4].isoformat() if row[4] else None
                    }
                }
            
            for row in air_results:
                if row[0] in locations_data:
                    locations_data[row[0]]["air_quality"] = {
                        "pm10": row[1],
                        "pm2_5": row[2],
                        "collected_at": row[3].isoformat() if row[3] else None
                    }
            
            return {
                "success": True,
                "date": date.today().isoformat(),
                "locations": list(locations_data.values())
            }
            
    except Exception as e:
        logger.error(f"Error getting locations summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@daily_data_router.get("/collection-stats")
async def get_collection_stats(days: int = 30, db=Depends(get_db)):
    """Get collection statistics for the past N days"""
    try:
        with db.connect() as conn:
            stats = conn.execute(text("""
                SELECT 
                    COUNT(DISTINCT date) as days_collected,
                    COUNT(*) as total_weather_records,
                    AVG(temperature) as avg_temperature,
                    MAX(temperature) as max_temperature,
                    MIN(temperature) as min_temperature
                FROM weather_data
                WHERE date >= CURRENT_DATE - :days::integer
            """), {"days": days}).fetchone()
            
            air_stats = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_air_records,
                    AVG(pm10) as avg_pm10,
                    AVG(pm2_5) as avg_pm2_5
                FROM air_quality_data
                WHERE DATE(timestamp) >= CURRENT_DATE - :days::integer
            """), {"days": days}).fetchone()
            
            news_stats = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_articles,
                    COUNT(DISTINCT source) as unique_sources
                FROM news_articles
                WHERE published_at >= CURRENT_DATE - :days::integer
            """), {"days": days}).fetchone()
            
            return {
                "success": True,
                "period_days": days,
                "statistics": {
                    "weather": {
                        "days_collected": stats[0] if stats else 0,
                        "total_records": stats[1] if stats else 0,
                        "avg_temperature": round(stats[2], 2) if stats and stats[2] else None,
                        "max_temperature": stats[3] if stats else None,
                        "min_temperature": stats[4] if stats else None
                    },
                    "air_quality": {
                        "total_records": air_stats[0] if air_stats else 0,
                        "avg_pm10": round(air_stats[1], 2) if air_stats and air_stats[1] else None,
                        "avg_pm2_5": round(air_stats[2], 2) if air_stats and air_stats[2] else None
                    },
                    "news": {
                        "total_articles": news_stats[0] if news_stats else 0,
                        "unique_sources": news_stats[1] if news_stats else 0
                    }
                }
            }
            
    except Exception as e:
        logger.error(f"Error getting collection stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
