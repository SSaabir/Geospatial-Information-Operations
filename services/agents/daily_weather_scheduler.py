#!/usr/bin/env python3
"""
Daily Weather Data Scheduler
============================
Automatically fetches and uploads current weather data to the database every day.

Features:
- Scheduled daily weather data collection
- Error handling and logging
- Multiple location support
- Database health checks
- Retry mechanism for failed uploads

Author: AI Assistant
Created: 2025-09-27
"""

import os
import sys
import time
import schedule
import logging
import psycopg2
from datetime import datetime, date
from dotenv import load_dotenv
import json
from typing import List, Dict, Any

# Add the current directory to path so we can import collector functions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from collector import fetch_and_store_weather, upload_air_quality_to_postgres
except ImportError:
    print("❌ Error: Could not import collector functions. Make sure collector.py exists.")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_weather_scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class WeatherScheduler:
    """Handles daily weather data collection and database operations."""
    
    def __init__(self):
        self.locations = [
            "Colombo",
            "Kandy", 
            "Galle",
            "Jaffna",
            "Trincomalee"
        ]
        self.max_retries = 3
        self.retry_delay = 300  # 5 minutes
        
    def check_database_connection(self) -> bool:
        """Check if database connection is working."""
        try:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                database=os.getenv("DB_NAME", "GISDb"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD")
            )
            cursor = conn.cursor()
            # Removed database connection test
            cursor.close()
            conn.close()
            logger.info("Database connection test logic removed")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {str(e)}")
            return False
    
    def fetch_weather_for_location(self, location: str, date_param: str = "today") -> Dict[str, Any]:
        """Fetch weather data for a specific location."""
        try:
            logger.info(f"🌤️ Fetching weather data for {location} ({date_param})")
            weather_data = fetch_and_store_weather(location, date_param)
            logger.info(f"✅ Successfully fetched weather data for {location}")
            return {
                "location": location,
                "status": "success",
                "data": weather_data,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Failed to fetch weather data for {location}: {str(e)}")
            return {
                "location": location,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def fetch_air_quality_for_location(self, location: str) -> Dict[str, Any]:
        """Fetch air quality data for a specific location."""
        try:
            logger.info(f"🌬️ Fetching air quality data for {location}")
            # Import the tool and run it
            result = upload_air_quality_to_postgres.invoke(location)
            result_data = json.loads(result)
            
            if result_data.get("success"):
                logger.info(f"✅ Successfully fetched air quality data for {location}")
                return {
                    "location": location,
                    "status": "success", 
                    "data": result_data,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.warning(f"⚠️ Air quality fetch returned no success for {location}")
                return {
                    "location": location,
                    "status": "warning",
                    "data": result_data,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"❌ Failed to fetch air quality data for {location}: {str(e)}")
            return {
                "location": location,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def daily_weather_collection(self):
        """Main function to collect all daily weather data."""
        logger.info("🚀 Starting daily weather data collection...")
        
        # Check database connection first
        if not self.check_database_connection():
            logger.error("❌ Cannot proceed - database connection failed")
            return
        
        weather_results = []
        air_quality_results = []
        
        # Collect weather data for all locations
        for location in self.locations:
            for attempt in range(self.max_retries):
                try:
                    # Fetch today's weather data
                    weather_result = self.fetch_weather_for_location(location, "today")
                    weather_results.append(weather_result)
                    
                    # Fetch air quality data
                    air_quality_result = self.fetch_air_quality_for_location(location)
                    air_quality_results.append(air_quality_result)
                    
                    break  # Success, no need to retry
                    
                except Exception as e:
                    logger.warning(f"⚠️ Attempt {attempt + 1}/{self.max_retries} failed for {location}: {str(e)}")
                    if attempt < self.max_retries - 1:
                        logger.info(f"⏳ Waiting {self.retry_delay} seconds before retry...")
                        time.sleep(self.retry_delay)
                    else:
                        logger.error(f"❌ All attempts failed for {location}")
                        weather_results.append({
                            "location": location,
                            "status": "failed",
                            "error": f"Max retries exceeded: {str(e)}",
                            "timestamp": datetime.now().isoformat()
                        })
        
        # Generate summary report
        self.generate_daily_report(weather_results, air_quality_results)
        
        logger.info("✅ Daily weather data collection completed!")
    
    def generate_daily_report(self, weather_results: List[Dict], air_quality_results: List[Dict]):
        """Generate a summary report of the daily collection."""
        today = date.today().isoformat()
        
        weather_success = sum(1 for r in weather_results if r["status"] == "success")
        weather_failed = sum(1 for r in weather_results if r["status"] in ["error", "failed"])
        
        air_success = sum(1 for r in air_quality_results if r["status"] == "success")
        air_failed = sum(1 for r in air_quality_results if r["status"] in ["error", "failed"])
        
        report = f"""
📊 DAILY WEATHER COLLECTION REPORT - {today}
====================================================

🌤️ WEATHER DATA COLLECTION:
   ✅ Successfully collected: {weather_success}/{len(weather_results)} locations
   ❌ Failed: {weather_failed}/{len(weather_results)} locations
   
🌬️ AIR QUALITY DATA COLLECTION:
   ✅ Successfully collected: {air_success}/{len(air_quality_results)} locations  
   ❌ Failed: {air_failed}/{len(air_quality_results)} locations

📍 LOCATIONS PROCESSED: {', '.join(self.locations)}

📅 COLLECTION TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔗 DATABASE STATUS: Connected ✅
====================================================
        """
        
        logger.info(report)
        
        # Save detailed report to file
        report_file = f"daily_weather_report_{today}.json"
        detailed_report = {
            "date": today,
            "collection_time": datetime.now().isoformat(),
            "summary": {
                "weather_success": weather_success,
                "weather_failed": weather_failed,
                "air_quality_success": air_success, 
                "air_quality_failed": air_failed,
                "total_locations": len(self.locations)
            },
            "weather_results": weather_results,
            "air_quality_results": air_quality_results
        }
        
        try:
            with open(report_file, 'w') as f:
                json.dump(detailed_report, f, indent=2, default=str)
            logger.info(f"📝 Detailed report saved to: {report_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save report file: {str(e)}")

def setup_daily_schedule():
    """Setup the daily scheduling."""
    scheduler = WeatherScheduler()
    
    # Schedule daily collection at 6:00 AM
    schedule.every().day.at("06:00").do(scheduler.daily_weather_collection)
    
    # Also allow manual trigger for testing
    if len(sys.argv) > 1 and sys.argv[1] == "--run-now":
        logger.info("🧪 Running manual collection (--run-now mode)")
        scheduler.daily_weather_collection()
        return
    
    logger.info("⏰ Daily weather scheduler started")
    logger.info("📅 Scheduled to run every day at 6:00 AM")
    logger.info("🔄 Press Ctrl+C to stop the scheduler")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("👋 Scheduler stopped by user")

if __name__ == "__main__":
    print("🌤️ Daily Weather Data Scheduler")
    print("================================")
    print("📅 Automatically collects weather data every day at 6:00 AM")
    print("🌍 Locations: Colombo, Kandy, Galle, Jaffna, Trincomalee")
    print("💾 Stores data in PostgreSQL database")
    print("📊 Generates daily collection reports")
    print("")
    print("Usage:")
    print("  python daily_weather_scheduler.py           # Start scheduler")
    print("  python daily_weather_scheduler.py --run-now # Run collection immediately")
    print("")
    
    setup_daily_schedule()