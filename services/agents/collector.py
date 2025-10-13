from langgraph.graph import StateGraph, END, START
from langchain.agents import initialize_agent
from langchain_community.agent_toolkits.load_tools import load_tools
from typing import TypedDict, Optional, List
from langchain_groq import ChatGroq
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, Engine
from langchain.tools import tool
import urllib.request
import json
from langchain_experimental.sql import SQLDatabaseChain
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain

import re, time, os
from datetime import date, datetime
from dotenv import load_dotenv

# ====================================================================
# TOKEN OPTIMIZATION AND CACHING
# ====================================================================

# Simple in-memory cache for database results (in production, use Redis)
query_cache = {}
cache_expiry = {}
CACHE_DURATION = 300  # 5 minutes

def get_cached_result(query_hash: str):
    """Get cached result if available and not expired"""
    import time
    current_time = time.time()
    
    if query_hash in query_cache and query_hash in cache_expiry:
        if current_time < cache_expiry[query_hash]:
            return query_cache[query_hash]
        else:
            # Remove expired cache
            del query_cache[query_hash]
            del cache_expiry[query_hash]
    return None

def cache_result(query_hash: str, result: str):
    """Cache result with expiry"""
    import time
    query_cache[query_hash] = result
    cache_expiry[query_hash] = time.time() + CACHE_DURATION

# Load environment variables
load_dotenv()

llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct",
               groq_api_key=os.getenv("GROQ_API_KEY")
               )

# Define tools (APIs, DB connectors)
tools = load_tools(["serpapi", "requests_all"], 
                   serpapi_api_key=os.getenv("SERPAPI_API_KEY"),
                   allow_dangerous_tools=True
                   )

from typing import Optional

# Database state globals
engine: Optional[Engine] = None
db: Optional[SQLDatabase] = None
sql_chain = None

def initialize_db(db_engine: Engine) -> None:
    """
    Initialize database connection using engine from orchestrator.
    This must be called before using any database-related functionality.
    
    Args:
        db_engine: SQLAlchemy Engine instance provided by the orchestrator
    """
    global engine, db, sql_chain
    if not isinstance(db_engine, Engine):
        raise TypeError("db_engine must be a SQLAlchemy Engine instance")
    
    engine = db_engine
    db = SQLDatabase(engine)
    sql_chain = create_sql_query_chain(llm, db)
    print("✅ Database connection initialized with orchestrator engine")


#Preprocess the data

def extract_date_or_placeholder(sunrise_val):
    if pd.isna(sunrise_val):
        return "###"  
    return sunrise_val.date()


def preprocess_weather_data_csv(df):

    df = df.drop(columns=['feelslike','feelslikemax','feelslikemin','dew','precipprob','precipcover','severerisk','stations','severerisk'])

    df["sunrise"] = pd.to_datetime(df["sunrise"], errors="coerce")
    df["datetime"] = df["sunrise"].apply(extract_date_or_placeholder)
    df["sunrise"] = df["sunrise"].dt.time

    if "sunset" in df.columns:
        df["sunset"] = pd.to_datetime(df["sunset"], errors="coerce").dt.time

    df["name"] = df["name"].astype(str).str.replace("", "")
    df["conditions"] = df["conditions"].astype(str).str.replace(",", "")
    df["country"] = "Sri Lanka"
    df.head()

    df = df.rename(columns={
    "name": "statedistrict",
    "precip": "rainsum",
    "preciptype": "rain",
    "tempmax": "tempmax",
    "tempmin": "tempmin",
    "temp": "temp",
    "humidity": "humidity",
    "snow": "snow",
    "snowdepth": "snowdepth",
    "windgust": "windgust",
    "windspeed": "windspeed",
    "winddir": "winddir",
    "sealevelpressure": "sealevelpressure",
    "cloudcover": "cloudcover",
    "visibility": "visibility",
    "solarradiation": "solarradiation",
    "solarenergy": "solarenergy",
    "uvindex": "uvindex",
    "sunrise": "sunrise",
    "sunset": "sunset",
    "moonphase": "moonphase",
    "conditions": "conditions",
    "description": "description",
    "icon": "icon",
    "country": "country"
    })

    for col in ['snow', 'rain']:
        # Convert existing values to boolean: True if any value exists, False if NaN or empty
        df[col] = df[col].apply(lambda x: True if pd.notna(x) and x != "" else False)


    output_path = "preprocessed_climate_dataset5.csv"
    df.to_csv(output_path, index=False)

    print("✅ Preprocessing completed. Saved to:", output_path)
    return df


@tool("upload_to_postgresql", return_direct=True)
def upload_to_postgresql(file_path: str) -> str:
    """Upload a CSV file into the PostgreSQL database."""
    df = pd.read_csv(file_path)
    df = preprocess_weather_data_csv(df)

    # 1️⃣ Replace missing values
    # Text columns → "N/A"
    text_cols = ['statedistrict', 'conditions', 'description', 'icon', 'country']
    df[text_cols] = df[text_cols].fillna("N/A").replace("", "N/A")

    # Numeric columns → 0
    num_cols = [
        'tempmax', 'tempmin', 'temp', 'humidity', 'rainsum', 'snow', 'snowdepth',
        'windgust', 'windspeed', 'winddir', 'sealevelpressure', 'cloudcover',
        'visibility', 'solarradiation', 'solarenergy', 'uvindex', 'moonphase'
    ]
    df[num_cols] = df[num_cols].fillna(0)

    # Boolean columns → False
    bool_cols = ['rain', 'snow']
    df[bool_cols] = df[bool_cols].fillna(False)


    # Convert datetime/time columns
    df['datetime'] = pd.to_datetime(df['datetime']).dt.date
    df['sunrise'] = pd.to_datetime(df['sunrise'], format='%H:%M:%S').dt.time
    df['sunset']  = pd.to_datetime(df['sunset'], format='%H:%M:%S').dt.time

    # 3️⃣ Insert into PostgreSQL table
    df.to_sql('weather_data', db, if_exists='append', index=False)




@tool("query_postgresql_tool", return_direct=True)

def query_postgresql_tool(question: str) -> str:
    """
    Safely convert a natural-language question into a SQL SELECT using LangChain's SQLDatabaseChain.
    Implements intelligent result truncation and caching to prevent token limit issues.
    """
    import hashlib
    global db, sql_chain, engine

    # Ensure db and sql_chain are initialized
    if db is None or sql_chain is None:
        if engine is None:
            from db_config import get_database_engine
            engine = get_database_engine()
        db = SQLDatabase(engine)
        sql_chain = create_sql_query_chain(llm, db)

    # Create cache key
    query_hash = hashlib.md5(question.encode()).hexdigest()

    # Check cache first
    cached_result = get_cached_result(query_hash)
    if cached_result:
        return cached_result

    audit_path = os.environ.get("SQL_AUDIT_LOG", "sql_audit.log")

    # --- helper to clean SQL ---
    def extract_sql(text: str) -> str:
        # Capture SQL inside ```sql ... ```
        match = re.search(r"```sql\s+(.*?)\s+```", text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        # Otherwise, return the first SELECT/WITH onwards
        match = re.search(r"(select|with)\b.*", text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(0).strip()
        return text.strip()

    def make_json_serializable(obj):
        # Recursively convert datetime/date objects to strings in dicts/lists
        import datetime
        if isinstance(obj, dict):
            return {k: make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [make_json_serializable(v) for v in obj]
        elif isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        else:
            return obj

    def summarize_large_result(rows, max_rows=50, max_length=5000):
        """
        Intelligently summarize large datasets to prevent token overflow.
        Returns a summary with key statistics and sample data.
        """
        if not rows or len(rows) == 0:
            return {"rows": [], "summary": "No data found"}

        # Convert all rows to JSON-serializable
        rows = make_json_serializable(rows)
        total_rows = len(rows)
        # If result is small, return as-is
        if total_rows <= max_rows:
            result_str = json.dumps(rows, default=str)
            if len(result_str) <= max_length:
                return {"rows": rows, "summary": f"Complete dataset with {total_rows} records"}

        # For large datasets, create intelligent summary
        sample_size = min(max_rows, total_rows)
        sample_rows = rows[:sample_size]
        # Generate statistics if numeric columns exist
        summary_stats = {}
        if rows and isinstance(rows[0], dict):
            first_row = rows[0]
            for key, value in first_row.items():
                try:
                    # Check if column contains numeric data
                    numeric_values = []
                    for row in rows[:100]:  # Sample first 100 for stats
                        if isinstance(row, dict) and key in row:
                            val = row[key]
                            if isinstance(val, (int, float)) and val is not None:
                                numeric_values.append(val)
                    if len(numeric_values) > 5:  # If we have enough numeric data
                        summary_stats[key] = {
                            "count": len(numeric_values),
                            "min": min(numeric_values),
                            "max": max(numeric_values),
                            "avg": round(sum(numeric_values) / len(numeric_values), 2)
                        }
                except:
                    continue
        summary = {
            "total_records": total_rows,
            "sample_size": sample_size,
            "showing": f"First {sample_size} records out of {total_rows} total",
            "statistics": summary_stats if summary_stats else "No numeric data found"
        }
        return {
            "rows": sample_rows,
            "summary": summary,
            "truncated": True,
            "note": f"Dataset truncated to prevent token overflow. Showing {sample_size}/{total_rows} records."
        }

    # Step 1: generate SQL
    try:
        sql_raw = sql_chain.invoke({"question": question})
        sql_clean = extract_sql(str(sql_raw)).rstrip(";")
    except Exception as e:
        error_result = json.dumps({"error": "sql_generation_failed", "details": str(e)})
        cache_result(query_hash, error_result)
        return error_result

    # Step 2: safety checks
    banned = r"\b(drop|delete|update|insert|alter|grant|truncate|create|replace|merge|shutdown)\b"
    if re.search(banned, sql_clean, flags=re.IGNORECASE):
        error_result = json.dumps({"error": "disallowed_statement"})
        return error_result

    if not re.match(r"^\s*(select|with)\b", sql_clean, flags=re.IGNORECASE):
        error_result = json.dumps({"error": "not_select", "raw": str(sql_raw)})
        return error_result

    # Step 3: enforce reasonable LIMIT for token management
    max_limit = 200  # Further reduced for token safety
    if not re.search(r"\blimit\b", sql_clean, flags=re.IGNORECASE):
        sql_exec = sql_clean + f" LIMIT {max_limit}"
    else:
        # Extract existing limit and cap it
        limit_match = re.search(r"\blimit\s+(\d+)", sql_clean, flags=re.IGNORECASE)
        if limit_match:
            existing_limit = int(limit_match.group(1))
            if existing_limit > max_limit:
                sql_exec = re.sub(r"\blimit\s+\d+", f"LIMIT {max_limit}", sql_clean, flags=re.IGNORECASE)
            else:
                sql_exec = sql_clean
        else:
            sql_exec = sql_clean

    # Step 4: audit
    try:
        with open(audit_path, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}  QUESTION: {question}  SQL: {sql_exec}\n")
    except Exception:
        pass

    # Step 5: execute query
    try:
        # Use pandas.read_sql for robust, predictable results with column names
        import pandas as pd
        if engine is None:
            from db_config import get_database_engine
            engine = get_database_engine()
        df = pd.read_sql(sql_exec, engine)
        # Convert datetimes to ISO strings and ensure JSON-serializable
        def _convert(val):
            try:
                if hasattr(val, 'isoformat'):
                    return val.isoformat()
            except Exception:
                pass
            return val

        records = df.to_dict(orient='records')
        rows = [{k: _convert(v) for k, v in rec.items()} for rec in records]
    except Exception as e:
        error_result = json.dumps({"error": "execution_failed", "details": str(e), "sql": sql_exec})
        return error_result
    
    # Apply intelligent summarization
    result_data = summarize_large_result(rows, max_rows=30, max_length=3000)  # More conservative limits
    
    output = {
        "sql": sql_exec,
        "row_count": len(rows),
        "data": result_data,
        "token_optimized": True,
        "cached": False
    }

    # Final safety check for JSON size
    output_str = json.dumps(output, default=str)
    if len(output_str) > 6000:  # Conservative limit
        # Emergency truncation
        emergency_summary = {
            "sql": sql_exec,
            "row_count": len(rows),
            "data": {
                "rows": rows[:5] if rows else [],  # Only 5 rows in emergency
                "summary": f"Large dataset with {len(rows)} records. Emergency truncation applied.",
                "truncated": True,
                "note": "Result heavily truncated due to size constraints"
            },
            "token_optimized": True,
            "emergency_truncated": True,
            "cached": False
        }
        output_str = json.dumps(emergency_summary, default=str)

    # Cache the result
    cache_result(query_hash, output_str)
    
    return output_str



@tool("fetch_weather_tool", return_direct=True)
def fetch_weather_tool (tool_input: str) -> str:
    """
    tool_input: expected format "city=Colombo;date=yesterday"
    """
    # Parse input
    params = dict(item.split("=") for item in tool_input.split(";"))
    city = params.get("city", "Colombo")
    date = params.get("date", "yesterday")

    # Call the original function
    weather_info = fetch_and_store_weather(city, date)
    print(weather_info)
    # Return as JSON string for the agent
    return json.dumps(weather_info)

def fetch_and_store_weather(city="Colombo", date="yesterday"):
    """Fetch weather data from API and store in PostgreSQL."""
    # Clean up date parameter to avoid URL encoding issues
    import urllib.parse
    import requests
    from datetime import datetime
    import json

    clean_date = urllib.parse.quote(date.strip(), safe='')
    
    # API Call with proper error handling
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}/{clean_date}?unitGroup=metric&include=days&key=KGCW7SXGVXRYL7ZK7W7SEJSR8&contentType=json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for 4XX/5XX errors
        jsonData = response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise Exception(f"Weather data not found for {city} on {date}. Please check the city name and date.")
        elif e.response.status_code == 401 or e.response.status_code == 403:
            raise Exception("API key error or rate limit exceeded. Please check your API key configuration.")
        else:
            raise Exception(f"API request failed: {str(e)}")
    except requests.exceptions.Timeout:
        raise Exception(f"API request timed out after 10 seconds for {city}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Invalid JSON response from weather API")
    
    # Validate response structure
    if not jsonData.get("days"):
        raise Exception(f"No weather data available for {city} on {date}")
        
    try:
        day = jsonData["days"][0]
    except (KeyError, IndexError):
        raise Exception("Unexpected API response format - missing days data")

    # Map to schema
    # Validate critical fields from API response
    required_fields = ["datetime", "temp"]
    missing_fields = [field for field in required_fields if field not in day]
    if missing_fields:
        raise Exception(f"Missing required weather data fields: {', '.join(missing_fields)}")

    # Map and validate weather data with defaults
    try:
        weather_info = {
            "country": "Sri Lanka",
            "statedistrict": city,
            "datetime": day["datetime"],  # Required field
            "tempmax": float(day.get("tempmax", 0)) if day.get("tempmax") is not None else None,
            "tempmin": float(day.get("tempmin", 0)) if day.get("tempmin") is not None else None,
            "temp": float(day["temp"]),  # Required field
            "humidity": float(day.get("humidity", 0)) if day.get("humidity") is not None else None,
            "rain": bool(day.get("precip", 0) > 0),
            "rainsum": float(day.get("precip", 0)) if day.get("precip") is not None else 0.0,
            "snow": bool(day.get("snow", 0) > 0),
            "snowdepth": float(day.get("snowdepth", 0)) if day.get("snowdepth") is not None else 0.0,
            "windgust": float(day.get("windgust", 0)) if day.get("windgust") is not None else None,
            "windspeed": float(day.get("windspeed", 0)) if day.get("windspeed") is not None else None,
            "winddir": float(day.get("winddir", 0)) if day.get("winddir") is not None else None,
            "sealevelpressure": float(day.get("pressure", 0)) if day.get("pressure") is not None else None,
            "cloudcover": float(day.get("cloudcover", 0)) if day.get("cloudcover") is not None else None,
            "visibility": float(day.get("visibility", 0)) if day.get("visibility") is not None else None,
            "solarradiation": float(day.get("solarradiation", 0)) if day.get("solarradiation") is not None else None,
            "solarenergy": float(day.get("solarenergy", 0)) if day.get("solarenergy") is not None else None,
            "uvindex": float(day.get("uvindex", 0)) if day.get("uvindex") is not None else None,
            "sunrise": day.get("sunrise"),
            "sunset": day.get("sunset"),
            "moonphase": float(day.get("moonphase", 0)) if day.get("moonphase") is not None else None,
            "conditions": str(day.get("conditions", "")) or "Unknown",
            "description": str(day.get("description", "")) or None,
            "icon": str(day.get("icon", "")) or None
        }
    except (ValueError, TypeError) as e:
        raise Exception(f"Error processing weather data fields: {str(e)}")

    # Validate data types and ranges
    try:
        # Temperature range validation (-100 to +100 Celsius should cover all scenarios)
        for temp_field in ["temp", "tempmax", "tempmin"]:
            if weather_info.get(temp_field) is not None:
                if not -100 <= weather_info[temp_field] <= 100:
                    raise ValueError(f"Invalid temperature value for {temp_field}: {weather_info[temp_field]}")
        
        # Humidity validation (0-100%)
        if weather_info["humidity"] is not None and not 0 <= weather_info["humidity"] <= 100:
            raise ValueError(f"Invalid humidity value: {weather_info['humidity']}")
        
        # Date validation
        datetime.strptime(weather_info["datetime"], "%Y-%m-%d")  # Will raise ValueError if invalid
        
    except ValueError as e:
        raise Exception(f"Data validation error: {str(e)}")

    # Check database connection
    if engine is None:
        raise RuntimeError("Database not initialized. Call initialize_db first.")
        
    # Convert data into DataFrame for SQLAlchemy insertion
    import pandas as pd
    df = pd.DataFrame([weather_info])
    
    # Attempt database insertion with detailed error handling
    try:
        df.to_sql('weather_data', engine, if_exists='append', index=False)
        print(f"✅ Weather data for {city} ({weather_info['datetime']}) stored successfully")
        
        # Log successful insertion
        with open("collector_log.txt", "a") as log:
            log.write(f"{datetime.now().isoformat()}: Successfully stored weather data for {city} on {weather_info['datetime']}\n")
            
    except Exception as e:
        error_msg = f"Error storing weather data: {str(e)}"
        print(f"❌ {error_msg}")
        
        # Log error
        with open("collector_error_log.txt", "a") as error_log:
            error_log.write(f"{datetime.now().isoformat()}: {error_msg} - City: {city}, Date: {weather_info['datetime']}\n")
            
        raise RuntimeError(error_msg)

    return weather_info



'''

@tool("fetch_climate_news", return_direct=True)
def fetch_climate_news(query: str = "climate change"):



    import requests

    api_key = os.getenv("WEATHER_API_KEY")
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 5,
        "apiKey": api_key,
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
    except Exception:
        return {
            "title": [None]*5,
            "url": [None]*5,
            "publishedAt": [None]*5
        }

    articles = data.get("articles", [])
    titles, urls, dates = [], [], []
    for a in articles[:5]:
        titles.append(a.get("title"))
        urls.append(a.get("url"))
        dates.append(a.get("publishedAt"))

    # Pad lists if fewer than 5 articles
    while len(titles) < 5:
        titles.append(None)
        urls.append(None)
        dates.append(None)

    return {
        "title": titles,
        "url": urls,
        "publishedAt": dates
    }

'''


@tool("fetch_extra_earth_data", return_direct=True)
def fetch_extra_earth_data(location: str = "colombo") -> str:
    """Fetch air quality metrics (pm10, pm2_5, carbon_monoxide, ozone) using Open-Meteo.

    This uses Open-Meteo's Air Quality API (no API key). `location` can be a city name or "lat,lon".
    Returns a JSON string with the latest available values or an error dict.
    """
    import requests
    import json
    import re

    def geocode_city(city_name: str):
        # Simple geocode via Nominatim (OpenStreetMap) - no key but rate-limited
        try:
            r = requests.get("https://nominatim.openstreetmap.org/search", params={"q": city_name, "format": "json", "limit": 1}, headers={"User-Agent": "collector-agent/1.0"}, timeout=10)
            if r.status_code == 200:
                j = r.json()
                if j:
                    return float(j[0]["lat"]), float(j[0]["lon"])
        except Exception:
            return None
        return None

    # Parse location: allow "lat,lon" or city name
    lat_lon_match = re.match(r"^\s*([-+]?\d+\.?\d*)\s*,\s*([-+]?\d+\.?\d*)\s*$", location)
    if lat_lon_match:
        lat, lon = float(lat_lon_match.group(1)), float(lat_lon_match.group(2))
    else:
        gc = geocode_city(location)
        if gc is None:
            # fallback to Colombo coordinates
            lat, lon = 6.9271, 79.8612
        else:
            lat, lon = gc

    # Open-Meteo Air Quality API
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
    "latitude": lat,
    "longitude": lon,
    "hourly": "pm10,pm2_5,carbon_monoxide,ozone"
}
    try:
        resp = requests.get(url, params=params, timeout=10)
    except Exception as e:
        return json.dumps({"error": "request_failed", "details": str(e)})

    if resp.status_code != 200:
        return json.dumps({"error": "open_meteo_error", "status_code": resp.status_code, "details": resp.text})

    try:
        data = resp.json()
    except Exception as e:
        return json.dumps({"error": "invalid_json", "details": str(e)})

    # Get latest index (last hourly point)
    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    if not times:
        return json.dumps({"error": "no_hourly_data"})

    idx = -1
    try:
        latest = {
            "time": times[idx],
            "pm10": hourly.get("pm10", [None])[idx],
            "pm2_5": hourly.get("pm2_5", [None])[idx],
            "carbon_monoxide": hourly.get("carbon_monoxide", [None])[idx],
            "ozone": hourly.get("ozone", [None])[idx],
            "lat": lat,
            "lon": lon,
        }
    except Exception as e:
        return json.dumps({"error": "parse_error", "details": str(e), "raw": data})

    return json.dumps(latest)


@tool("upload_air_quality_to_postgres", return_direct=True)
def upload_air_quality_to_postgres(location: str = "Colombo") -> str:
    """
    Fetch latest air quality data via fetch_extra_earth_data and upload to PostgreSQL.
    """
    import json
    from datetime import datetime

    try:
        # Use the existing tool instead of refetching
        data_json = fetch_extra_earth_data.invoke(location)
        data = json.loads(data_json)
    except Exception as e:
        return json.dumps({"error": "fetch_failed", "details": str(e)})

    # Check for errors in fetch
    if data.get("error"):
        return json.dumps({"error": "fetch_error", "details": data})

    # Extract fields, safely using None if missing
    datetime_val = data.get("time") or str(datetime.today().date())
    pm10 = data.get("pm10")
    pm2_5 = data.get("pm2_5")
    carbon_monoxide = data.get("carbon_monoxide")
    ozone = data.get("ozone")
    lat = data.get("lat")
    lon = data.get("lon")
    country = data.get("country") or "Sri Lanka"  # optional default
    statedistrict = location
    source = "Open-Meteo Air Quality API"

    # Insert into PostgreSQL
    try:
        sql = f"""
        INSERT INTO air_quality_data (
            country, statedistrict, datetime, pm10, pm2_5, carbon_monoxide, ozone, lat, lon, source
        ) VALUES (
            '{country}', '{statedistrict}', '{datetime_val}', {pm10}, {pm2_5}, {carbon_monoxide}, {ozone}, {lat}, {lon}, '{source}'
        );
        """
        db.run(sql)
    except Exception as e:
        return json.dumps({"error": "db_insert_failed", "details": str(e), "sql": sql})

    return json.dumps({"success": True, "uploaded_data": data}, default=str)



tools.append(upload_to_postgresql)
tools.append(fetch_weather_tool)
# add the new tools we inserted above
# fetch_climate_news and fetch_extra_earth_data are defined in earlier cells
try:
    #tools.append(fetch_climate_news)
    tools.append(fetch_extra_earth_data)
    tools.append(query_postgresql_tool)
    tools.append(upload_air_quality_to_postgres)
except NameError:
    # In case the notebook is executed top-to-bottom and the cells haven't been run yet,
    # we proceed silently; the agent will fail to initialize until those cells are run.
    pass

# Collector agent
collector = initialize_agent(
    tools, llm, agent="zero-shot-react-description", verbose=True,
)

class collectorState(TypedDict):
    input: str  # input query
    title: list | None #Optional[List] can be used 
    url: list | None
    publishedAt: list | None
    output: str  # collected data

# Define collector node function
def collector_node(state: collectorState) -> collectorState:
    """
    Enhanced collector that prioritizes database queries.
    Always attempts to query the database first before using external APIs.
    """
    import json
    
    query = state["input"]
    
    # First, try to get data from the database
    print("🔍 Checking database first...")
    try:
        # Attempt database query for any query type
        db_result = query_postgresql_tool.invoke(query)
        
        # Parse the result to check if we got valid data
        try:
            db_data = json.loads(db_result)
            
            # Check if we got meaningful data from database
            if not db_data.get("error") and db_data.get("row_count", 0) > 0:
                print(f"✅ Found {db_data.get('row_count')} records in database")
                state["output"] = db_result
                return state
            else:
                print(f"⚠️ No data in database or query error: {db_data.get('error', 'No results')}")
        except json.JSONDecodeError:
            # If result is not JSON, it might still be valid data
            if db_result and len(db_result) > 50:
                print("✅ Retrieved data from database")
                state["output"] = db_result
                return state
            print("⚠️ Database query returned no usable data")
                
    except Exception as e:
        print(f"⚠️ Database query attempt failed: {str(e)}")
    
    # If database didn't return useful data, fall back to the agent with all tools
    print("🔄 Database empty or no results - using collector agent with external tools...")
    result = collector.run(query)

    if isinstance(result, dict):
        state["title"] = result.get("title")
        state["url"] = result.get("url")
        state["publishedAt"] = result.get("publishedAt")
    else:
        state["output"] = result

    return state

# Lazy initialization to prevent duplicate node errors
def _create_collector_graph():
    """Create and return the compiled collector graph"""
    graph = StateGraph(collectorState)
    graph.add_node("collector", collector_node)
    graph.add_edge(START, "collector")  # input query
    graph.add_edge("collector", END)  # outputs collected data
    return graph.compile()

_collector_app_instance = None

def _get_collector_app():
    """Get or create the collector graph"""
    global _collector_app_instance
    if _collector_app_instance is None:
        _collector_app_instance = _create_collector_graph()
    return _collector_app_instance


def run_collector_agent(query: str) -> str:

    """
    Run the collector agent with the given query and return the optimized output.
    If the query is a direct SQL query, skip LLM/tool initialization and run SQL directly.
    """
    import json
    global engine
    if query.strip().startswith('query_postgresql_tool'):
        # Direct SQL query mode (no LLM/tools needed)
        if engine is None:
            from db_config import get_database_engine
            engine = get_database_engine()
        sql = query.replace('query_postgresql_tool', '').strip()
        import pandas as pd
        try:
            df = pd.read_sql(sql, engine)
        except Exception as e:
            return json.dumps({"error": "execution_failed", "details": str(e), "sql": sql})

        # Convert records to JSON-serializable dicts
        records = df.to_dict(orient='records')
        def _conv(v):
            try:
                if hasattr(v, 'isoformat'):
                    return v.isoformat()
            except Exception:
                pass
            return v

        rows = [{k: _conv(v) for k, v in rec.items()} for rec in records]

        # Build a simple summary and return structured JSON so orchestrator/frontend can parse
        data_obj = {
            "rows": rows,
            "summary": "No data found" if len(rows) == 0 else {"total_records": len(rows), "showing": f"Showing {len(rows)} records"},
            "truncated": False if len(rows) <= 200 else True
        }

        output = {
            "sql": sql,
            "row_count": len(rows),
            "data": data_obj,
            "token_optimized": True,
            "cached": False
        }

        return json.dumps(output, default=str)
    # Otherwise, use the agent workflow (LLM/tools)
    try:
        app = _get_collector_app()
        result = app.invoke({"input": query})
        output = result.get("output", "")
        if len(output) > 10000:
            try:
                data = json.loads(output)
                summary = {
                    "query": query,
                    "result_type": "summarized",
                    "data_summary": "Large dataset truncated for token efficiency",
                    "note": "Full data available through direct database queries"
                }
                if isinstance(data, dict):
                    if "row_count" in data:
                        summary["record_count"] = data["row_count"]
                    if "data" in data and isinstance(data["data"], dict):
                        if "summary" in data["data"]:
                            summary["statistics"] = data["data"]["summary"]
                        if "rows" in data["data"] and len(data["data"]["rows"]) > 0:
                            summary["sample_data"] = data["data"]["rows"][:3]
                return json.dumps(summary, default=str)
            except (json.JSONDecodeError, Exception):
                return output[:5000] + "... [TRUNCATED FOR TOKEN EFFICIENCY]"
        return output
    except Exception as e:
        error_response = {
            "error": f"Collector agent failed: {str(e)}",
            "query": query,
            "note": "Please try a more specific query or contact support"
        }
        return json.dumps(error_response)


# ====================================================================
# DAILY AUTOMATION FUNCTIONS
# ====================================================================

def fetch_current_weather_batch(locations=None, date_param="today"):
    """
    Fetch current weather data for multiple locations and store in database.
    
    Args:
        locations (list): List of city names. Defaults to Sri Lankan cities.
        date_param (str): Date parameter for API ("today", "yesterday", etc.)
        
    Returns:
        dict: Results summary with success/failure counts and details
    """
    if locations is None:
        locations = ["Colombo", "Kandy", "Galle", "Jaffna", "Trincomalee", "Negombo"]
    
    results = {
        "timestamp": date.today().isoformat(),
        "total_locations": len(locations),
        "successful": 0,
        "failed": 0,
        "details": [],
        "errors": []
    }
    
    print(f"🌤️ Starting batch weather collection for {len(locations)} locations...")
    print(f"📅 Date parameter: {date_param}")
    print(f"📍 Locations: {', '.join(locations)}")
    
    for i, city in enumerate(locations, 1):
        try:
            print(f"\n[{i}/{len(locations)}] Fetching weather for {city}...")
            weather_data = fetch_and_store_weather(city, date_param)
            
            results["successful"] += 1
            results["details"].append({
                "location": city,
                "status": "success",
                "temperature": weather_data.get("temp"),
                "conditions": weather_data.get("conditions"),
                "timestamp": weather_data.get("datetime")
            })
            
            print(f"✅ {city}: {weather_data.get('temp')}°C, {weather_data.get('conditions')}")
            
        except Exception as e:
            results["failed"] += 1
            error_msg = f"Failed to fetch weather for {city}: {str(e)}"
            results["errors"].append(error_msg)
            results["details"].append({
                "location": city,
                "status": "error", 
                "error": str(e)
            })
            
            print(f"❌ {city}: {str(e)}")
    
    # Print summary
    print(f"\n📊 BATCH COLLECTION SUMMARY")
    print(f"=" * 40)
    print(f"✅ Successful: {results['successful']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"📍 Total locations: {results['total_locations']}")
    print(f"📅 Date: {results['timestamp']}")
    
    return results


def setup_daily_weather_collection():
    """
    Setup function to configure daily weather data collection.
    This function can be called to perform the daily collection routine.
    """
    from datetime import datetime
    
    print("🚀 DAILY WEATHER COLLECTION STARTED")
    print("=" * 50)
    print(f"⏰ Collection time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check database connection first
    if engine is None:
        error_msg = "Database not initialized. Call initialize_db first."
        print(f"❌ {error_msg}")
        return {"error": error_msg}
        
    try:
        result = engine.execute("SELECT COUNT(*) FROM weather_data").scalar()
        print(f"📊 Current database records: {result}")
        print("✅ Database connection verified")
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return {"error": "Database connection failed", "details": str(e)}
    
    # Collect today's weather data
    weather_results = fetch_current_weather_batch(date_param="today")
    
    # Collect air quality data for major cities
    air_quality_results = {"successful": 0, "failed": 0, "details": []}
    major_cities = ["Colombo", "Kandy", "Galle"]
    
    print(f"\n🌬️ Collecting air quality data for {len(major_cities)} major cities...")
    
    for city in major_cities:
        try:
            result_json = upload_air_quality_to_postgres.invoke(city)
            result_data = json.loads(result_json)
            
            if result_data.get("success"):
                air_quality_results["successful"] += 1
                air_quality_results["details"].append({
                    "location": city,
                    "status": "success"
                })
                print(f"✅ Air quality data collected for {city}")
            else:
                air_quality_results["failed"] += 1
                air_quality_results["details"].append({
                    "location": city,
                    "status": "error",
                    "error": result_data.get("error", "Unknown error")
                })
                print(f"❌ Air quality collection failed for {city}")
                
        except Exception as e:
            air_quality_results["failed"] += 1
            air_quality_results["details"].append({
                "location": city,
                "status": "error", 
                "error": str(e)
            })
            print(f"❌ Air quality error for {city}: {str(e)}")
    
    # Final summary
    print(f"\n🎯 DAILY COLLECTION COMPLETED")
    print(f"=" * 50)
    print(f"🌤️ Weather data: {weather_results['successful']}/{weather_results['total_locations']} locations")
    print(f"🌬️ Air quality data: {air_quality_results['successful']}/{len(major_cities)} cities")
    print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return {
        "weather_results": weather_results,
        "air_quality_results": air_quality_results,
        "completion_time": datetime.now().isoformat()
    }


@tool("daily_weather_collection_tool", return_direct=True)
def daily_weather_collection_tool(trigger: str = "manual") -> str:
    """
    Tool to trigger daily weather collection process.
    Can be used by agents or called directly for automation.
    
    Args:
        trigger (str): How the collection was triggered ("manual", "scheduled", "agent")
    """
    try:
        print(f"🔄 Daily weather collection triggered: {trigger}")
        results = setup_daily_weather_collection()
        return json.dumps(results, default=str)
    except Exception as e:
        error_result = {
            "error": "Daily collection failed", 
            "details": str(e),
            "timestamp": datetime.now().isoformat()
        }
        return json.dumps(error_result, default=str)


# Add the new tool to the tools list
try:
    tools.append(daily_weather_collection_tool)
    print("✅ Daily weather collection tool added successfully")
except NameError:
    pass
