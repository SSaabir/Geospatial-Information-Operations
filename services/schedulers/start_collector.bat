@echo off
REM ====================================================================
REM   Unified Daily Data Collector - Windows Startup Script
REM ====================================================================
REM   Starts the automated daily data collection system
REM   Collects: Weather, Air Quality, and Climate News
REM ====================================================================

echo.
echo ========================================================
echo   UNIFIED DAILY DATA COLLECTION SYSTEM
echo ========================================================
echo.
echo Starting the automated data collector...
echo This will run continuously and collect data at 6:00 AM daily
echo.
echo Press Ctrl+C to stop
echo.

cd /d "%~dp0"

REM Check if .env file exists
if not exist "..\.env" (
    echo [WARNING] .env file not found!
    echo Please create a .env file in the services directory with:
    echo   OPENWEATHERMAP_API_KEY=your_key_here
    echo   NEWS_API_KEY=your_key_here
    echo.
    pause
)

REM Activate virtual environment if it exists
if exist "..\venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call ..\venv\Scripts\activate.bat
)

REM Run the collector
python unified_daily_collector.py

pause
