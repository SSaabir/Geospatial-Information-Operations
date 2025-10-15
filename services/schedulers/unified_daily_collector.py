#!/usr/bin/env python3
"""
Unified Daily Data Collection System
====================================
Automatically runs existing collector functions at scheduled times:
- Weather data (using collector.py functions)
- Air quality data (using collector.py functions)
- Climate news articles (using news_collector.py)

Author: GIS Team
Created: October 2025
"""

import os
import sys
import time
import schedule
import logging
from datetime import datetime, date
from dotenv import load_dotenv
import json
from typing import Dict, Any
from sqlalchemy.orm import sessionmaker

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from agents.collector import (
        initialize_db,
        fetch_current_weather_batch,
        upload_air_quality_to_postgres
    )
    from agents.news_collector import NewsCollectorAgent
    from db_config import DatabaseConfig
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("Make sure collector.py and news_collector.py are available.")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('unified_daily_collector.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class UnifiedDailyCollector:
    """Unified system for daily weather, air quality, and news collection using existing functions."""
    
    def __init__(self):
        self.locations = [
            "Colombo",
            "Kandy", 
            "Galle",
            "Jaffna",
            "Trincomalee",
            "Negombo"
        ]
        
        # Database setup
        self.db_config = DatabaseConfig()
        self.engine = self.db_config.get_engine()
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Initialize database connection for collector
        initialize_db(self.engine)
        
        logger.info("✅ Unified Daily Collector initialized with existing database connection")
        
    def check_database_connection(self) -> bool:
        """Check if database connection is working."""
        try:
            with self.engine.connect() as conn:
                from sqlalchemy import text
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            logger.info("✅ Database connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {str(e)}")
            return False
    
    def fetch_weather_batch(self) -> Dict[str, Any]:
        """Fetch weather data for all locations using existing collector function."""
        logger.info("🌤️ Fetching weather data using collector.fetch_current_weather_batch()")
        try:
            results = fetch_current_weather_batch(locations=self.locations, date_param="today")
            return {"status": "success", "data": results}
        except Exception as e:
            logger.error(f"❌ Weather batch collection failed: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def fetch_air_quality_batch(self) -> Dict[str, Any]:
        """Fetch air quality data for all locations using existing collector function."""
        logger.info("🌬️ Fetching air quality data using collector.upload_air_quality_to_postgres()")
        
        results = {"successful": 0, "failed": 0, "details": []}
        
        for location in self.locations:
            try:
                result_json = upload_air_quality_to_postgres.invoke(location)
                result_data = json.loads(result_json)
                
                if result_data.get("success"):
                    results["successful"] += 1
                    results["details"].append({
                        "location": location,
                        "status": "success"
                    })
                    logger.info(f"✅ Air quality collected for {location}")
                else:
                    results["failed"] += 1
                    results["details"].append({
                        "location": location,
                        "status": "error",
                        "error": result_data.get("error", "Unknown")
                    })
                    logger.error(f"❌ Air quality failed for {location}")
                    
            except Exception as e:
                results["failed"] += 1
                results["details"].append({
                    "location": location,
                    "status": "error",
                    "error": str(e)
                })
                logger.error(f"❌ Air quality error for {location}: {str(e)}")
            
            time.sleep(2)  # Rate limiting
        
        return {"status": "success", "data": results}
    
    def fetch_climate_news(self) -> Dict[str, Any]:
        """Fetch latest climate and weather news."""
        try:
            logger.info("📰 Fetching climate news articles")
            
            # Create database session
            db_session = self.SessionLocal()
            
            try:
                # Use NewsCollectorAgent
                news_agent = NewsCollectorAgent(db_session)
                result = news_agent.collect_news(days_back=1, max_articles=20)
                
                logger.info(f"✅ News collection complete: {result.get('total_collected', 0)} articles")
                return {
                    "status": "success",
                    "data": result,
                    "timestamp": datetime.now().isoformat()
                }
                
            finally:
                db_session.close()
                
        except Exception as e:
            logger.error(f"❌ Failed to fetch climate news: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def fetch_climate_news(self) -> Dict[str, Any]:
        """Fetch climate news using existing NewsCollectorAgent."""
        logger.info("📰 Fetching climate news using NewsCollectorAgent.collect_news()")
        
        db_session = self.SessionLocal()
        try:
            news_agent = NewsCollectorAgent(db_session)
            result = news_agent.collect_news(days_back=1, max_articles=20)
            
            logger.info(f"✅ News collection completed: {result.get('total_collected', 0)} articles")
            
            return {
                "status": "success",
                "data": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch climate news: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        finally:
            db_session.close()
    
    def run_daily_collection(self):
        """Main function to run all daily data collection tasks."""
        logger.info("=" * 70)
        logger.info("🚀 STARTING UNIFIED DAILY DATA COLLECTION")
        logger.info(f"📅 Date: {date.today()}")
        logger.info(f"🕐 Time: {datetime.now().strftime('%H:%M:%S')}")
        logger.info("=" * 70)
        
        # Check database connection
        if not self.check_database_connection():
            logger.error("❌ Cannot proceed - database connection failed")
            return
        
        # 1. COLLECT WEATHER DATA FOR ALL LOCATIONS
        logger.info("\n📊 PHASE 1: WEATHER DATA COLLECTION")
        logger.info("-" * 70)
        weather_results = self.fetch_weather_batch()
        
        # 2. COLLECT AIR QUALITY DATA FOR ALL LOCATIONS
        logger.info("\n📊 PHASE 2: AIR QUALITY DATA COLLECTION")
        logger.info("-" * 70)
        air_quality_results = self.fetch_air_quality_batch()
        
        # 3. COLLECT CLIMATE NEWS
        logger.info("\n📊 PHASE 3: CLIMATE NEWS COLLECTION")
        logger.info("-" * 70)
        news_result = self.fetch_climate_news()
        
        # Generate summary report
        self.generate_daily_report(
            weather_results.get("data"),
            air_quality_results.get("data"),
            news_result
        )
        
        logger.info("\n" + "=" * 70)
        logger.info("✅ UNIFIED DAILY DATA COLLECTION COMPLETED!")
        logger.info("=" * 70)
    
    def generate_daily_report(self, weather_results: Dict, 
                            air_quality_results: Dict,
                            news_result: Dict):
        """Generate a comprehensive daily collection report."""
        today = date.today().isoformat()
        
        # Parse weather results
        weather_data = weather_results if weather_results else {}
        weather_success = weather_data.get("success", 0)
        weather_failed = weather_data.get("failed", 0)
        weather_total = weather_success + weather_failed
        
        # Parse air quality results
        air_data = air_quality_results if air_quality_results else {}
        air_success = air_data.get("successful", 0)
        air_failed = air_data.get("failed", 0)
        air_total = air_success + air_failed
        
        # Parse news results
        news_success = 1 if news_result.get("status") == "success" else 0
        news_count = news_result.get("data", {}).get("total_collected", 0) if news_success else 0
        
        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║           UNIFIED DAILY DATA COLLECTION REPORT                   ║
║                        {today}                              ║
╚══════════════════════════════════════════════════════════════════╝

🌤️  WEATHER DATA COLLECTION:
    ✅ Success: {weather_success}/{weather_total} locations
    ❌ Failed:  {weather_failed}/{weather_total} locations
    
🌬️  AIR QUALITY DATA COLLECTION:
    ✅ Success: {air_success}/{air_total} locations
    ❌ Failed:  {air_failed}/{air_total} locations

📰 CLIMATE NEWS COLLECTION:
    ✅ Status:  {"Success" if news_success else "Failed"}
    📄 Articles: {news_count} new articles collected
    
📍 LOCATIONS PROCESSED:
    {', '.join(self.locations)}

⏰ COLLECTION TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💾 DATABASE STATUS: Connected ✅

╚══════════════════════════════════════════════════════════════════╝
        """
        
        logger.info(report)
        
        # Save detailed report to file
        report_file = f"daily_collection_report_{today}.json"
        detailed_report = {
            "date": today,
            "collection_time": datetime.now().isoformat(),
            "summary": {
                "weather": {
                    "success": weather_success,
                    "failed": weather_failed,
                    "total": weather_total
                },
                "air_quality": {
                    "success": air_success,
                    "failed": air_failed,
                    "total": air_total
                },
                "news": {
                    "success": news_success,
                    "articles_collected": news_count
                },
                "locations": self.locations
            },
            "details": {
                "weather_results": weather_results,
                "air_quality_results": air_quality_results,
                "news_result": news_result
            }
        }
        
        try:
            with open(report_file, 'w') as f:
                json.dump(detailed_report, f, indent=2, default=str)
            logger.info(f"📝 Detailed report saved to: {report_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save report file: {str(e)}")


def setup_scheduler(collection_time: str = "06:00"):
    """Setup the daily scheduling."""
    collector = UnifiedDailyCollector()
    
    # Schedule daily collection at specified time (default 6:00 AM)
    schedule.every().day.at(collection_time).do(collector.run_daily_collection)
    
    # Allow manual trigger for testing
    if len(sys.argv) > 1 and sys.argv[1] == "--run-now":
        logger.info("🧪 Running manual collection (--run-now mode)")
        collector.run_daily_collection()
        return
    
    logger.info("⏰ Unified Daily Collector started")
    logger.info(f"📅 Scheduled to run every day at {collection_time}")
    logger.info("🔄 Press Ctrl+C to stop the scheduler")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("\n👋 Scheduler stopped by user")


if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║         UNIFIED DAILY DATA COLLECTION SYSTEM                     ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print("")
    print("📊 Automatically collects:")
    print("   • Weather data (temperature, humidity, pressure, wind, etc.)")
    print("   • Air quality data (PM2.5, PM10, AQI, etc.)")
    print("   • Climate news articles")
    print("")
    print("🌍 Locations: Colombo, Kandy, Galle, Jaffna, Trincomalee")
    print("💾 Stores all data in PostgreSQL database")
    print("📊 Generates daily collection reports")
    print("")
    print("⚙️  Configuration:")
    print("   - Default collection time: 6:00 AM")
    print("   - Requires: OPENWEATHERMAP_API_KEY in .env")
    print("   - Requires: NEWS_API_KEY in .env")
    print("")
    print("Usage:")
    print("  python unified_daily_collector.py           # Start scheduler")
    print("  python unified_daily_collector.py --run-now # Run immediately")
    print("")
    
    # Check for required environment variables
    if not os.getenv("OPENWEATHERMAP_API_KEY"):
        print("⚠️  WARNING: OPENWEATHERMAP_API_KEY not found in .env")
    if not os.getenv("NEWS_API_KEY"):
        print("⚠️  WARNING: NEWS_API_KEY not found in .env")
    print("")
    
    setup_scheduler(collection_time="06:00")
