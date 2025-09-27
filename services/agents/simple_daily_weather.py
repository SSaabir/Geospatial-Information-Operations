#!/usr/bin/env python3
"""
Simple Daily Weather Collection
===============================
A lightweight script to collect daily weather data without external dependencies.

This script can be:
- Run manually for immediate collection
- Scheduled using Windows Task Scheduler
- Called from other scripts or automation tools

Usage:
    python simple_daily_weather.py           # Run collection now
    python simple_daily_weather.py --test    # Test database connection only
    python simple_daily_weather.py --help    # Show help

Author: AI Assistant  
Created: 2025-09-27
"""

import os
import sys
import json
from datetime import datetime, date
from dotenv import load_dotenv

# Add current directory to path to import collector functions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def print_banner():
    """Print the application banner."""
    print("=" * 60)
    print("🌤️  DAILY WEATHER DATA COLLECTION")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def test_imports():
    """Test if required imports are available."""
    try:
        from collector import setup_daily_weather_collection, fetch_current_weather_batch
        print("✅ Collector functions imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import collector functions: {str(e)}")
        print("Make sure you're running this from the correct directory.")
        return False

def test_database():
    """Test database connection."""
    try:
        import psycopg2
        load_dotenv()
        
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "GISDb"), 
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD")
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM weather_data")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        print(f"✅ Database connection successful")
        print(f"📊 Current weather records in database: {count}")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print("Please check your database configuration and .env file")
        return False

def run_daily_collection():
    """Run the main daily weather collection process."""
    try:
        from collector import setup_daily_weather_collection
        
        print("🚀 Starting daily weather data collection...")
        print()
        
        # Run the collection
        results = setup_daily_weather_collection()
        
        # Save results to file
        today = date.today().isoformat()
        results_file = f"weather_collection_results_{today}.json"
        
        try:
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"📝 Results saved to: {results_file}")
        except Exception as e:
            print(f"⚠️ Could not save results file: {str(e)}")
        
        # Print final status
        if "error" in results:
            print(f"\n❌ Collection failed: {results['error']}")
            return False
        else:
            weather_success = results.get("weather_results", {}).get("successful", 0)
            weather_total = results.get("weather_results", {}).get("total_locations", 0)
            air_success = results.get("air_quality_results", {}).get("successful", 0)
            
            print(f"\n🎉 Collection completed successfully!")
            print(f"🌤️ Weather data: {weather_success}/{weather_total} locations")
            print(f"🌬️ Air quality data: {air_success} cities")
            return True
            
    except Exception as e:
        print(f"❌ Collection process failed: {str(e)}")
        return False

def show_help():
    """Show help information."""
    help_text = """
🌤️ SIMPLE DAILY WEATHER COLLECTION
==================================

This script collects current weather and air quality data for Sri Lankan cities
and stores it in your PostgreSQL database.

USAGE:
------
python simple_daily_weather.py           # Run collection now
python simple_daily_weather.py --test    # Test database connection only  
python simple_daily_weather.py --help    # Show this help

LOCATIONS COVERED:
------------------
Weather: Colombo, Kandy, Galle, Jaffna, Trincomalee, Negombo
Air Quality: Colombo, Kandy, Galle

AUTOMATION OPTIONS:
-------------------
1. Windows Task Scheduler (recommended):
   schtasks /create /tn "Daily Weather" /tr "python {script_path}" /sc daily /st 06:00

2. Manual scheduling:
   Run this script daily at your preferred time

3. Integration with other scripts:
   from simple_daily_weather import run_daily_collection
   result = run_daily_collection()

REQUIREMENTS:
-------------
- PostgreSQL database configured 
- .env file with database credentials
- Internet connection for weather API
- Python packages: psycopg2, python-dotenv, requests

FILES GENERATED:
----------------
- weather_collection_results_YYYY-MM-DD.json (daily results)
- daily_weather_scheduler.log (if using scheduler)

TROUBLESHOOTING:
----------------
If you encounter issues:
1. Check database connection with --test
2. Verify .env file contains correct database credentials
3. Ensure you have internet connectivity
4. Check that required Python packages are installed
"""
    print(help_text)

def main():
    """Main function."""
    # Parse command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['--help', '-h', 'help']:
            show_help()
            return
        elif arg in ['--test', '-t', 'test']:
            print_banner()
            test_success = test_imports() and test_database()
            if test_success:
                print("\n✅ All tests passed! Ready for daily collection.")
            else:
                print("\n❌ Tests failed. Please fix issues before running collection.")
            return
    
    # Run normal collection
    print_banner()
    
    # Test prerequisites
    if not test_imports():
        sys.exit(1)
    
    if not test_database():
        sys.exit(1)
    
    print()
    
    # Run collection
    success = run_daily_collection()
    
    print()
    print("=" * 60)
    if success:
        print("✅ Daily weather collection completed successfully!")
    else:
        print("❌ Daily weather collection failed!")
        sys.exit(1)
    
    print(f"⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()