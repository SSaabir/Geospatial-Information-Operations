from langgraph.graph import StateGraph, END, START
from langchain.agents import initialize_agent
from langchain_community.agent_toolkits.load_tools import load_tools
from typing import TypedDict, Optional, List
from langchain_groq import ChatGroq
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from langchain.tools import tool
import urllib.request
import json
import psycopg2
from langchain_experimental.sql import SQLDatabaseChain
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain

import re, time, os
from datetime import date, datetime
from dotenv import load_dotenv
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

# 2️⃣ Create SQLAlchemy engine using environment variables
engine = create_engine(os.getenv("DATABASE_URL"))
db = SQLDatabase(engine)
sql_chain = create_sql_query_chain(llm, db)



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

    def summarize_large_result(rows, max_rows=50, max_length=5000):
        """
        Intelligently summarize large datasets to prevent token overflow.
        Returns a summary with key statistics and sample data.
        """
        if not rows or len(rows) == 0:
            return {"rows": [], "summary": "No data found"}

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
        raw = db.run(sql_exec)
    except Exception as e:
        error_result = json.dumps({"error": "execution_failed", "details": str(e), "sql": sql_exec})
        return error_result

    # Normalize rows
    def normalize_rows(r):
        if isinstance(r, list):
            return [dict(row) if hasattr(row, "keys") else list(row) for row in r]
        return str(r)

    rows = normalize_rows(raw)
    
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
    clean_date = urllib.parse.quote(date.strip(), safe='')
    
    # API Call
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}/{clean_date}?unitGroup=metric&include=days&key=KGCW7SXGVXRYL7ZK7W7SEJSR8&contentType=json"
    ResultBytes = urllib.request.urlopen(url)
    jsonData = json.load(ResultBytes)
    day = jsonData["days"][0]

    # Map to schema
    weather_info = {
        "country": "Sri Lanka",
        "statedistrict": city,
        "datetime": day["datetime"],
        "tempmax": day.get("tempmax"),
        "tempmin": day.get("tempmin"),
        "temp": day.get("temp"),
        "humidity": day.get("humidity"),
        "rain": day.get("precip", 0) > 0,
        "rainsum": day.get("precip"),
        "snow": day.get("snow", 0) > 0,
        "snowdepth": day.get("snowdepth"),
        "windgust": day.get("windgust"),
        "windspeed": day.get("windspeed"),
        "winddir": day.get("winddir"),
        "sealevelpressure": day.get("pressure"),
        "cloudcover": day.get("cloudcover"),
        "visibility": day.get("visibility"),
        "solarradiation": day.get("solarradiation"),
        "solarenergy": day.get("solarenergy"),
        "uvindex": day.get("uvindex"),
        "sunrise": day.get("sunrise"),
        "sunset": day.get("sunset"),
        "moonphase": day.get("moonphase"),
        "conditions": day.get("conditions"),
        "description": day.get("description"),
        "icon": day.get("icon")
    }

    # Insert into DB
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "GISDb"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD")
    )
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO weather_data (
        country, statedistrict, datetime, tempmax, tempmin, temp, humidity,
        rain, rainsum, snow, snowdepth, windgust, windspeed, winddir,
        sealevelpressure, cloudcover, visibility, solarradiation, solarenergy,
        uvindex, sunrise, sunset, moonphase, conditions, description, icon
    ) VALUES (
        %(country)s, %(statedistrict)s, %(datetime)s, %(tempmax)s, %(tempmin)s, %(temp)s, %(humidity)s,
        %(rain)s, %(rainsum)s, %(snow)s, %(snowdepth)s, %(windgust)s, %(windspeed)s, %(winddir)s,
        %(sealevelpressure)s, %(cloudcover)s, %(visibility)s, %(solarradiation)s, %(solarenergy)s,
        %(uvindex)s, %(sunrise)s, %(sunset)s, %(moonphase)s, %(conditions)s, %(description)s, %(icon)s
    )
    """, weather_info)
    conn.commit()
    cursor.close()
    conn.close()

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

# Define LangGraph nodes
graph = StateGraph(collectorState)

def collector_node(state: collectorState) -> collectorState:
    result = collector.run(state["input"])

    if isinstance(result, dict):
        state["title"] = result.get("title")
        state["url"] = result.get("url")
        state["publishedAt"] = result.get("publishedAt")
    else:
        state["output"] = result

    return state

graph.add_node("collector", collector_node)
graph.add_edge(START, "collector")  # input query
graph.add_edge("collector", END)  # outputs collected data

# Run graph
app = graph.compile()
#result = app.invoke({"input": "upload_air_quality_to_postgres for Colombo"})
#print(result["output"])


def run_collector_agent(query: str) -> str:

    """
    Run the collector agent with the given query and return the optimized output.
    Includes additional token optimization at the agent level.
    """
    import json  # Import at function start to avoid conflicts
    
    try:
        result = app.invoke({"input": query})
        output = result.get("output", "")
        
        # Apply additional token optimization at agent level
        if len(output) > 10000:  # If output is very large
            try:
                # Try to parse and summarize if it's JSON
                data = json.loads(output)
                
                # Create a summarized version
                summary = {
                    "query": query,
                    "result_type": "summarized",
                    "data_summary": "Large dataset truncated for token efficiency",
                    "note": "Full data available through direct database queries"
                }
                
                # Include key statistics if available
                if isinstance(data, dict):
                    if "row_count" in data:
                        summary["record_count"] = data["row_count"]
                    if "data" in data and isinstance(data["data"], dict):
                        if "summary" in data["data"]:
                            summary["statistics"] = data["data"]["summary"]
                        if "rows" in data["data"] and len(data["data"]["rows"]) > 0:
                            summary["sample_data"] = data["data"]["rows"][:3]  # Just 3 sample rows
                
                return json.dumps(summary, default=str)
                
            except (json.JSONDecodeError, Exception):
                # If not JSON or parsing fails, truncate as text
                truncated = output[:5000] + "... [TRUNCATED FOR TOKEN EFFICIENCY]"
                return truncated
        
        return output
        
    except Exception as e:
        error_response = {
            "error": f"Collector agent failed: {str(e)}",
            "query": query,
            "note": "Please try a more specific query or contact support"
        }
        return json.dumps(error_response)

    """Run the collector agent with the given query and return the output."""
    result = app.invoke({"input": query})
    return result["output"]


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
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "GISDb"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD")
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM weather_data")
        record_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print(f"📊 Current database records: {record_count}")
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
