#!/bin/bash
# ====================================================================
#   Unified Daily Data Collector - Linux/Mac Startup Script
# ====================================================================
#   Starts the automated daily data collection system
#   Collects: Weather, Air Quality, and Climate News
# ====================================================================

echo ""
echo "========================================================"
echo "   UNIFIED DAILY DATA COLLECTION SYSTEM"
echo "========================================================"
echo ""
echo "Starting the automated data collector..."
echo "This will run continuously and collect data at 6:00 AM daily"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo "[WARNING] .env file not found!"
    echo "Please create a .env file in the services directory with:"
    echo "  OPENWEATHERMAP_API_KEY=your_key_here"
    echo "  NEWS_API_KEY=your_key_here"
    echo ""
    read -p "Press enter to continue anyway..."
fi

# Activate virtual environment if it exists
if [ -f "../venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source ../venv/bin/activate
fi

# Run the collector
python3 unified_daily_collector.py
