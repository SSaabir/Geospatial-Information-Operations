# Schedulers Directory

This directory contains automated scheduled tasks and background jobs for data collection.

## 📁 Directory Structure

```
schedulers/
├── unified_daily_collector.py    # Main daily data collection system
├── start_collector.bat           # Windows startup script
├── start_collector.sh            # Linux/Mac startup script
└── README.md                      # This file
```

## 🚀 Unified Daily Collector

Automatically collects and stores:
- **Weather Data**: Temperature, humidity, pressure, wind speed, etc.
- **Air Quality Data**: PM2.5, PM10, AQI, CO, NO2, O3, SO2
- **Climate News**: Latest climate and weather-related news articles

### Locations Covered
- Colombo
- Kandy
- Galle
- Jaffna
- Trincomalee

### Collection Schedule
- **Default Time**: 6:00 AM daily
- **Rate Limiting**: 2-second delay between API calls
- **Auto-retry**: Up to 3 attempts with 5-minute delays

## ⚙️ Configuration

### Required Environment Variables

Add these to your `.env` file in the `services` directory:

```env
# OpenWeatherMap API (for weather and air quality data)
OPENWEATHERMAP_API_KEY=your_openweathermap_api_key_here

# NewsAPI.org (for climate news collection)
NEWS_API_KEY=your_news_api_key_here

# Database configuration (if not already set)
DB_HOST=localhost
DB_NAME=GISDb
DB_USER=postgres
DB_PASSWORD=your_password
```

### Getting API Keys

1. **OpenWeatherMap**: 
   - Sign up at https://openweathermap.org/api
   - Free tier: 1,000 calls/day (more than enough for 5 locations × 2 data types)

2. **NewsAPI.org**:
   - Sign up at https://newsapi.org/
   - Free tier: 100 requests/day

## 🏃 Running the Collector

### Option 1: Start Scheduler (runs continuously)

**Windows:**
```cmd
cd services\schedulers
start_collector.bat
```

**Linux/Mac:**
```bash
cd services/schedulers
chmod +x start_collector.sh
./start_collector.sh
```

The scheduler will:
- Start immediately
- Run in the background
- Trigger data collection every day at 6:00 AM
- Continue running until you stop it (Ctrl+C)

### Option 2: Manual One-Time Collection

**Run immediately without scheduling:**
```bash
python unified_daily_collector.py --run-now
```

This will:
- Collect all data immediately
- Generate a report
- Exit when complete

## 📊 Database Tables

The collector creates and populates these tables:

### `daily_weather_data`
```sql
- id (SERIAL PRIMARY KEY)
- location (VARCHAR)
- date (DATE)
- temperature, temp_min, temp_max (FLOAT)
- humidity, pressure (FLOAT)
- wind_speed, wind_direction (FLOAT, INTEGER)
- cloudiness, visibility (INTEGER)
- weather_condition, weather_description (VARCHAR, TEXT)
- sunrise, sunset (TIMESTAMP)
- collected_at (TIMESTAMP)
- UNIQUE(location, date)
```

### `daily_air_quality`
```sql
- id (SERIAL PRIMARY KEY)
- location (VARCHAR)
- date (DATE)
- aqi (INTEGER) - Air Quality Index (1-5 scale)
- pm2_5, pm10 (FLOAT) - Particulate matter
- co, no2, o3, so2 (FLOAT) - Gas concentrations
- latitude, longitude (FLOAT)
- collected_at (TIMESTAMP)
- UNIQUE(location, date)
```

### `news_articles` (uses existing table)
- Stores climate and weather-related news articles
- See `models/news.py` for full schema

## 📝 Reports

### Daily Collection Report

After each collection run, a JSON report is generated:

**Filename**: `daily_collection_report_YYYY-MM-DD.json`

**Contents**:
```json
{
  "date": "2025-10-16",
  "collection_time": "2025-10-16T06:00:00",
  "summary": {
    "weather": { "success": 5, "failed": 0, "total": 5 },
    "air_quality": { "success": 5, "failed": 0, "total": 5 },
    "news": { "success": 1, "articles_collected": 20 }
  },
  "details": { ... }
}
```

### Log File

**Filename**: `unified_daily_collector.log`

Contains detailed execution logs with timestamps.

## 🔍 Monitoring

### Check Collection Status

Use the API endpoint:
```bash
GET /api/daily-data/status
```

Returns:
- Records collected today
- Last collection timestamp
- Number of locations processed

### View Latest Data

**Weather:**
```bash
GET /api/daily-data/latest-weather?location=Colombo
```

**Air Quality:**
```bash
GET /api/daily-data/latest-air-quality?location=Colombo
```

### Manual Trigger (Admin only)

```bash
POST /api/daily-data/trigger-collection
Authorization: Bearer <admin_jwt_token>
```

## 🐛 Troubleshooting

### Issue: "API key not found"
**Solution**: Add `OPENWEATHERMAP_API_KEY` and `NEWS_API_KEY` to `.env`

### Issue: "Database connection failed"
**Solution**: 
1. Check database is running: `pg_ctl status`
2. Verify credentials in `.env`
3. Test connection: `psql -U postgres -d GISDb`

### Issue: "Location not found"
**Solution**: Ensure location names are spelled correctly (Colombo, Kandy, etc.)

### Issue: Rate limit exceeded
**Solution**: 
- Free OpenWeatherMap: 1,000 calls/day
- Adjust `time.sleep(2)` in code if needed
- Consider upgrading API plan

## 🔄 Production Deployment

### Run as System Service (Linux)

Create `/etc/systemd/system/data-collector.service`:

```ini
[Unit]
Description=GIS Daily Data Collector
After=network.target postgresql.service

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/services/schedulers
ExecStart=/usr/bin/python3 unified_daily_collector.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable data-collector
sudo systemctl start data-collector
sudo systemctl status data-collector
```

### Run as Windows Service

Use `nssm` (Non-Sucking Service Manager):

```cmd
nssm install GISDataCollector "C:\Python\python.exe"
nssm set GISDataCollector AppDirectory "C:\path\to\services\schedulers"
nssm set GISDataCollector AppParameters "unified_daily_collector.py"
nssm start GISDataCollector
```

## 📈 Performance

- **Collection Time**: ~2-3 minutes for all locations and news
- **Database Impact**: Minimal (inserts/updates only)
- **Memory Usage**: ~50-100 MB
- **CPU Usage**: Negligible (mostly I/O waiting)

## 🔐 Security Considerations

1. **API Keys**: Never commit `.env` to version control
2. **Database**: Use read-only credentials if possible
3. **Logging**: Logs may contain timestamps and locations (no sensitive data)
4. **Network**: Ensure firewall allows HTTPS outbound (443)

## 📚 Related Files

- `../api/daily_data_api.py` - API endpoints for accessing collected data
- `../agents/news_collector.py` - News collection agent
- `../models/news.py` - News article database model
- `../db_config.py` - Database configuration

## 🤝 Contributing

When adding new data sources:
1. Create a new `fetch_*_data()` method
2. Add corresponding database table in `ensure_tables_exist()`
3. Update `run_daily_collection()` to include new phase
4. Update report generation to include new metrics
5. Document in this README

## 📞 Support

For issues or questions:
1. Check logs: `tail -f unified_daily_collector.log`
2. Verify database: Check tables exist and have data
3. Test API keys: Use curl to test endpoints directly
4. Review reports: Check JSON reports for detailed errors
