from TrendAgent import TrendAgent
import datetime
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Feature alias mapping for common terms
FEATURE_ALIASES = {
    'temp': 'temp',
    'temperature': 'temp',
    'humidity': 'humidity',
    'humid': 'humidity',
    'pressure': 'sealevelpressure',
    'sealevelpressure': 'sealevelpressure',
    'wind': 'windspeed',
    'windspeed': 'windspeed',
    'windgust': 'windgust',
    'cloud': 'cloudcover',
    'cloudcover': 'cloudcover',
    'clouds': 'cloudcover',
    'rain': 'rainsum',
    'rainfall': 'rainsum',
    'rainsum': 'rainsum',
    'visibility': 'visibility',
    'solar': 'solarradiation',
    'solarradiation': 'solarradiation',
    'uv': 'uvindex',
    'uvindex': 'uvindex',
    'tempmax': 'tempmax',
    'temperaturemax': 'tempmax',
    'tempmin': 'tempmin',
    'temperaturemin': 'tempmin',
    'winddir': 'winddir',
    'winddirection': 'winddir',
    'moonphase': 'moonphase',
    'moon': 'moonphase',
    'snow': 'snow',
    'snowdepth': 'snowdepth',
    'solarenergy': 'solarenergy'
}

def normalize_feature_name(feature_query, available_columns):
    """
    Normalize user's feature query to actual column name
    
    Args:
        feature_query (str): User's feature request (e.g., "temp", "temperature")
        available_columns (list): List of actual column names in dataframe
    
    Returns:
        str or None: Normalized column name or None if not found
    """
    if not feature_query:
        return None
    
    feature_lower = feature_query.lower().strip()
    
    # Try exact match first (case-insensitive)
    for col in available_columns:
        if feature_lower == col.lower():
            return col
    
    # Try alias mapping
    if feature_lower in FEATURE_ALIASES:
        mapped = FEATURE_ALIASES[feature_lower]
        # Check if mapped name exists in available columns
        for col in available_columns:
            if mapped.lower() == col.lower():
                return col
    
    # Try partial match (substring search)
    for col in available_columns:
        col_lower = col.lower()
        if feature_lower in col_lower or col_lower in feature_lower:
            return col
    
    return None

def run_trend_agent(query, db_uri=None):
    """
    Run the TrendAgent based on the query.
    
    Args:
        query (str): The user query (e.g., "analyze trends last 20 day temperature")
        db_uri (str): PostgreSQL connection URI
    
    Returns:
        str: JSON string of the analysis results or error message
    """
    if db_uri is None:
        db_uri = os.getenv("DATABASE_URL")
    agent = TrendAgent(db_uri)
    
    if agent.df is None:
        return json.dumps({"error": "Failed to load data from database"})
    
    # Parse the query (e.g., "analyze trends last N day VARIABLE" or "analyze VARIABLE trends")
    parts = query.lower().split()
    start_date = None
    end_date = None
    start_date_str = None
    end_date_str = None
    variable = None
    
    # Check for "last N day" or "last N days" pattern
    for i in range(len(parts)):
        if parts[i] == "last" and i + 2 < len(parts) and parts[i + 2] in ["day", "days"]:
            try:
                N = int(parts[i + 1])
                # Use current date: October 9, 2025
                current_date = datetime.date(2025, 10, 9)
                start_date = current_date - datetime.timedelta(days=N)
                end_date = current_date
                start_date_str = start_date.strftime("%Y-%m-%d")
                end_date_str = end_date.strftime("%Y-%m-%d")
                
                # Look for variable after "day/days"
                for j in range(i + 3, len(parts)):
                    # Skip common words
                    if parts[j] in ['analyze', 'trend', 'trends', 'analysis', 'for', 'of', 'the']:
                        continue
                    
                    # Try to normalize the feature name
                    normalized = normalize_feature_name(parts[j], agent.df.columns)
                    if normalized:
                        variable = normalized
                        break
            except (ValueError, IndexError):
                pass
    
    # If no date range found, check for variable anywhere in query
    if not variable:
        for part in parts:
            # Skip common words
            if part in ['analyze', 'trend', 'trends', 'analysis', 'for', 'of', 'the', 'last', 'day', 'days']:
                continue
            
            # Try to normalize the feature name
            normalized = normalize_feature_name(part, agent.df.columns)
            if normalized:
                variable = normalized
                break
    
    # Run analysis with the extracted parameters
    try:
        # Pass the features parameter if a specific variable was requested
        if variable:
            results = agent.analyze_trends(
                start_date=start_date_str, 
                end_date=end_date_str,
                features=variable  # Pass the specific feature
            )
            # Add metadata about the requested feature
            if "error" not in results:
                results["requested_feature"] = variable
        else:
            # No specific feature requested, analyze all
            results = agent.analyze_trends(
                start_date=start_date_str, 
                end_date=end_date_str
                # features=None means analyze all columns
            )
            if "error" not in results:
                results["note"] = "No specific feature requested. Analyzed all numeric columns."
        
        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Trend analysis failed: {str(e)}"}, indent=2)