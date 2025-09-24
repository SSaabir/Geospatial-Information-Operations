from langgraph.graph import StateGraph, END, START
from langchain.agents import initialize_agent
from langchain_community.agent_toolkits.load_tools import load_tools
from typing import TypedDict
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
import re, json, time, os
from datetime import date



llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct",
               groq_api_key="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"
               )

# Define tools (APIs, DB connectors)
tools = load_tools(["serpapi", "requests_all"], 
                   serpapi_api_key = "49a312e94db629a1d7d4efa33647dc82322dd921680f5cbe1441de0aee587bbd",
                   allow_dangerous_tools=True
                   )

# 2️⃣ Create SQLAlchemy engine
engine = create_engine('postgresql+psycopg2://postgres:ElDiabloX32@localhost:5432/GISDb')
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
    """


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

    # Step 1: generate SQL
    try:
        sql_raw = sql_chain.invoke({"question": question})
        sql_clean = extract_sql(str(sql_raw)).rstrip(";")
    except Exception as e:
        return json.dumps({"error": "sql_generation_failed", "details": str(e)})

    # Step 2: safety checks
    banned = r"\b(drop|delete|update|insert|alter|grant|truncate|create|replace|merge|shutdown)\b"
    if re.search(banned, sql_clean, flags=re.IGNORECASE):
        return json.dumps({"error": "disallowed_statement"})

    if not re.match(r"^\s*(select|with)\b", sql_clean, flags=re.IGNORECASE):
        return json.dumps({"error": "not_select", "raw": str(sql_raw)})

    # Step 3: enforce LIMIT
    if not re.search(r"\blimit\b", sql_clean, flags=re.IGNORECASE):
        sql_exec = sql_clean + " LIMIT 100"
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
        return json.dumps({"error": "execution_failed", "details": str(e), "sql": sql_exec})

    # Normalize rows
    def normalize_rows(r):
        if isinstance(r, list):
            return [dict(row) if hasattr(row, "keys") else list(row) for row in r]
        return str(r)

    rows = normalize_rows(raw)
    output = {"sql": sql_exec, "row_count": len(rows), "rows": rows}

    return json.dumps(output, default=str)



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
    # API Call
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}/{date}?unitGroup=metric&include=days&key=KGCW7SXGVXRYL7ZK7W7SEJSR8&contentType=json"
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
        host="localhost",
        database="GISDb",
        user="postgres",
        password="ElDiabloX32"
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

    api_key = "f875db6eac964594bbcd54e77f9d9b22"
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
    title: list | None
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
    """Run the collector agent with the given query and return the output."""
    result = app.invoke({"input": query})
    return result["output"]
