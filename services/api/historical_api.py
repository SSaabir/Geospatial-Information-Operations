"""
Historical Weather Data API
Provides tier-based access to historical weather data from the weather_data table.

Access Limits by Tier:
- Free: Last 30 days
- Researcher: Last 1 year (365 days)
- Professional: Full archive (28 years from 1997-2025)
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date, datetime, timedelta
from typing import Optional, List
import logging

from security.auth_middleware import get_current_user
from models.user import UserDB
from utils.tier import enforce_historical_access, get_historical_days_for_tier
from db_config import DatabaseConfig

logger = logging.getLogger(__name__)

historical_router = APIRouter(prefix="/historical", tags=["historical"])
db_config = DatabaseConfig()

def get_db():
    """FastAPI dependency for database session"""
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()


@historical_router.get("/weather")
async def get_historical_weather(
    city: str = Query(..., description="City name (e.g., Colombo, Jaffna, Kandy, Matara, Trincomalee)"),
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get historical weather data for a specific city and date range.
    
    Access is tier-based:
    - **Free**: Last 30 days only
    - **Researcher**: Last 1 year (365 days)
    - **Professional**: Full archive (28 years from 1997)
    
    Returns detailed weather data including temperature, humidity, precipitation,
    wind speed, pressure, and weather conditions.
    """
    
    # Validate date range
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be before or equal to end_date"
        )
    
    # Check if date range is too large (prevent abuse)
    days_requested = (end_date - start_date).days + 1
    if days_requested > 3650:  # 10 years max in single query
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Date range too large. Maximum 10 years (3650 days) per query."
        )
    
    # Enforce tier-based historical data access limits
    try:
        enforce_historical_access(start_date, current_user.tier)
    except HTTPException as e:
        # Re-raise with additional context
        logger.warning(f"User {current_user.email} (tier={current_user.tier}) attempted to access historical data beyond limits: {start_date}")
        raise e
    
    # Query weather_data table
    try:
        query = text("""
            SELECT 
                city,
                date,
                tempmax,
                tempmin,
                temperature,
                humidity,
                precipsum,
                rain,
                snow,
                snowdepth,
                windgust,
                wind_speed,
                winddir,
                pressure,
                cloudcover,
                visibility,
                solarradiation,
                solarenergy,
                uvindex,
                sunrise,
                sunset,
                moonphase,
                conditions,
                description,
                icon,
                country
            FROM weather_data
            WHERE LOWER(city) = LOWER(:city)
              AND date BETWEEN :start_date AND :end_date
            ORDER BY date DESC
        """)
        
        result = db.execute(query, {
            "city": city,
            "start_date": start_date,
            "end_date": end_date
        })
        
        # Convert rows to dictionaries
        columns = result.keys()
        data = [dict(zip(columns, row)) for row in result.fetchall()]
        
        # Convert date/time objects to ISO format
        for record in data:
            if isinstance(record.get('date'), date):
                record['date'] = record['date'].isoformat()
            if record.get('sunrise'):
                record['sunrise'] = str(record['sunrise'])
            if record.get('sunset'):
                record['sunset'] = str(record['sunset'])
        
        logger.info(f"Historical data query: user={current_user.email}, tier={current_user.tier}, city={city}, range={start_date} to {end_date}, records={len(data)}")
        
        return {
            "success": True,
            "city": city,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "record_count": len(data),
            "tier": current_user.tier,
            "data": data
        }
        
    except Exception as e:
        logger.error(f"Error querying historical weather data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve historical weather data: {str(e)}"
        )


@historical_router.get("/cities")
async def get_available_cities(
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of cities with available historical weather data.
    
    Returns city names and the count of records available for each city.
    """
    try:
        query = text("""
            SELECT 
                city,
                COUNT(*) as record_count,
                MIN(date) as earliest_date,
                MAX(date) as latest_date
            FROM weather_data
            GROUP BY city
            ORDER BY city
        """)
        
        result = db.execute(query)
        columns = result.keys()
        cities = [dict(zip(columns, row)) for row in result.fetchall()]
        
        # Convert dates to ISO format
        for city_info in cities:
            if isinstance(city_info.get('earliest_date'), date):
                city_info['earliest_date'] = city_info['earliest_date'].isoformat()
            if isinstance(city_info.get('latest_date'), date):
                city_info['latest_date'] = city_info['latest_date'].isoformat()
        
        return {
            "success": True,
            "cities": cities,
            "total_cities": len(cities)
        }
        
    except Exception as e:
        logger.error(f"Error querying available cities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve city list: {str(e)}"
        )


@historical_router.get("/access-limits")
async def get_access_limits(
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get historical data access limits for the current user's tier.
    
    Returns the oldest date accessible and the number of days of historical data available.
    """
    max_days = get_historical_days_for_tier(current_user.tier)
    
    if max_days == float('inf'):
        oldest_accessible = date(1997, 1, 1)  # Earliest data in database
        days_description = "unlimited"
    else:
        oldest_accessible = date.today() - timedelta(days=int(max_days))
        days_description = f"{int(max_days)} days"
    
    return {
        "success": True,
        "tier": current_user.tier,
        "historical_data_access": {
            "days": days_description,
            "days_numeric": max_days if max_days != float('inf') else None,
            "oldest_accessible_date": oldest_accessible.isoformat(),
            "today": date.today().isoformat()
        },
        "upgrade_info": {
            "free": "30 days",
            "researcher": "1 year (365 days)",
            "professional": "Full archive (28 years from 1997)"
        }
    }


@historical_router.get("/summary")
async def get_historical_summary(
    city: str = Query(..., description="City name"),
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get statistical summary of historical weather data for a date range.
    
    Returns averages, min/max values, and aggregated statistics.
    Access is tier-based like the main historical data endpoint.
    """
    
    # Validate and enforce access
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be before or equal to end_date"
        )
    
    enforce_historical_access(start_date, current_user.tier)
    
    try:
        query = text("""
            SELECT 
                city,
                COUNT(*) as total_days,
                AVG(temperature) as avg_temperature,
                MIN(tempmin) as lowest_temperature,
                MAX(tempmax) as highest_temperature,
                AVG(humidity) as avg_humidity,
                SUM(precipsum) as total_precipitation,
                AVG(wind_speed) as avg_wind_speed,
                MAX(windgust) as max_wind_gust,
                AVG(pressure) as avg_pressure,
                AVG(cloudcover) as avg_cloud_cover,
                COUNT(CASE WHEN rain = true THEN 1 END) as rainy_days,
                COUNT(CASE WHEN snow = true THEN 1 END) as snowy_days
            FROM weather_data
            WHERE LOWER(city) = LOWER(:city)
              AND date BETWEEN :start_date AND :end_date
            GROUP BY city
        """)
        
        result = db.execute(query, {
            "city": city,
            "start_date": start_date,
            "end_date": end_date
        })
        
        row = result.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data found for city '{city}' in the specified date range"
            )
        
        columns = result.keys()
        summary = dict(zip(columns, row))
        
        # Round numeric values for readability
        for key, value in summary.items():
            if isinstance(value, float):
                summary[key] = round(value, 2)
        
        logger.info(f"Historical summary: user={current_user.email}, city={city}, range={start_date} to {end_date}")
        
        return {
            "success": True,
            "city": city,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "summary": summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating historical summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate historical summary: {str(e)}"
        )
