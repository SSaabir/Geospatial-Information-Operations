@echo off
REM Daily Weather Data Collection Setup
REM ===================================
REM This script helps set up automated daily weather data collection

echo.
echo ========================================
echo   Daily Weather Data Collection Setup  
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python first
    pause
    exit /b 1
)

echo ✅ Python detected
echo.

REM Check if virtual environment exists
if not exist "..\.venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found at ..\.venv\
    echo Please create the virtual environment first
    pause
    exit /b 1
)

echo ✅ Virtual environment detected
echo.

REM Install required packages
echo 📦 Installing required packages...
..\.venv\Scripts\pip.exe install schedule
if errorlevel 1 (
    echo ⚠️  Failed to install schedule package
    echo Trying to continue anyway...
)

echo.
echo 🎯 DAILY WEATHER COLLECTION OPTIONS:
echo =====================================
echo.
echo 1. Run weather collection NOW (test)
echo 2. Setup Windows Task Scheduler (daily at 6 AM)  
echo 3. Run scheduler in background (manual mode)
echo 4. Test database connection
echo 5. Exit
echo.

choice /c 12345 /m "Select an option"

if errorlevel 5 goto :exit
if errorlevel 4 goto :test_db
if errorlevel 3 goto :run_scheduler
if errorlevel 2 goto :setup_task
if errorlevel 1 goto :run_now

:run_now
echo.
echo 🚀 Running weather collection immediately...
..\.venv\Scripts\python.exe -c "from collector import setup_daily_weather_collection; setup_daily_weather_collection()"
echo.
echo Collection completed! Check the output above for results.
pause
goto :exit

:test_db
echo.
echo 🔍 Testing database connection...
..\.venv\Scripts\python.exe -c "
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'GISDb'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD')
    )
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM weather_data')
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    print(f'✅ Database connection successful!')
    print(f'📊 Current weather records: {count}')
except Exception as e:
    print(f'❌ Database connection failed: {str(e)}')
"
pause
goto :exit

:setup_task
echo.
echo 🗓️ Setting up Windows Task Scheduler...
echo.
echo This will create a scheduled task to run weather collection daily at 6:00 AM
echo.

set SCRIPT_PATH=%~dp0daily_weather_scheduler.py
set PYTHON_PATH=%~dp0..\.venv\Scripts\python.exe

schtasks /create /tn "Daily Weather Data Collection" /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\" --run-now" /sc daily /st 06:00 /f

if errorlevel 1 (
    echo ❌ Failed to create scheduled task
    echo You may need to run this script as Administrator
) else (
    echo ✅ Scheduled task created successfully!
    echo 📅 Weather data will be collected daily at 6:00 AM
    echo.
    echo To manage the task:
    echo - View: schtasks /query /tn "Daily Weather Data Collection"  
    echo - Delete: schtasks /delete /tn "Daily Weather Data Collection"
)
pause
goto :exit

:run_scheduler
echo.
echo ⏰ Starting weather scheduler in background mode...
echo Press Ctrl+C to stop the scheduler
echo.
..\.venv\Scripts\python.exe daily_weather_scheduler.py
goto :exit

:exit
echo.
echo 👋 Goodbye!
exit /b 0