from TrendAgent import TrendAgent
import datetime
import json
import os
import pandas as pd
import numpy as np
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
    if not feature_query or not available_columns:
        return None
    
    # Ensure we have valid inputs
    if not isinstance(feature_query, str) or not isinstance(available_columns, (list, pd.Index)):
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
    # Initialize variables
    agent = None
    parts = []
    start_date = None
    end_date = None
    start_date_str = None
    end_date_str = None
    variable = None
    
    # Add global error handler
    def handle_error(error_type, error_msg, **kwargs):
        error_data = {
            "error": error_type,
            "details": str(error_msg)
        }
        error_data.update(kwargs)
        return json.dumps(error_data)

    # Validate input query
    if not isinstance(query, str) or not query.strip():
        return json.dumps({"error": "Invalid query. Please provide a non-empty string."})
    
    try:
        # Get database URI
        if db_uri is None:
            db_uri = os.getenv("DATABASE_URL")
            if not db_uri:
                return json.dumps({"error": "No database URI provided or found in environment"})
        
        # Initialize trend agent
        agent = TrendAgent(db_uri)
        
        if agent.df is None or agent.df.empty:
            return json.dumps({
                "error": "No data available",
                "details": "Failed to load data from database or database is empty"
            })
        
        # Ensure proper datetime index
        if not isinstance(agent.df.index, pd.DatetimeIndex):
            if 'datetime' in agent.df.columns:
                try:
                    agent.df['datetime'] = pd.to_datetime(agent.df['datetime'], errors='coerce')
                    agent.df.set_index('datetime', inplace=True)
                    if agent.df.index.isna().any():
                        return json.dumps({
                            "error": "Invalid datetime values",
                            "details": "Some datetime values could not be parsed"
                        })
                except Exception as e:
                    return json.dumps({
                        "error": "Failed to convert datetime column",
                        "details": str(e)
                    })
            else:
                return json.dumps({
                    "error": "Invalid data format",
                    "details": "No datetime column found in the data"
                })
                
        # Initialize query parsing
        parts = query.lower().strip().split()
        
    except Exception as e:
        return json.dumps({
            "error": "Initialization failed",
            "details": str(e),
            "query": query
        })
    
    # Check for "last N day" or "last N days" pattern
    try:
        for i in range(len(parts)):
            if parts[i] == "last" and i + 2 < len(parts) and parts[i + 2] in ["day", "days"]:
                try:
                    N = int(parts[i + 1])
                    if N <= 0 or N > 365:  # Validate reasonable range
                        continue
                        
                    # Use current date from system or parameter
                    try:
                        current_date = datetime.date(2025, 10, 10)  # Updated to current context date
                        start_date = current_date - datetime.timedelta(days=N)
                        end_date = current_date
                        start_date_str = start_date.strftime("%Y-%m-%d")
                        end_date_str = end_date.strftime("%Y-%m-%d")
                    except Exception as date_error:
                        return json.dumps({
                            "error": "Date calculation failed",
                            "details": str(date_error)
                        })
                    
                    # Look for variable after "day/days"
                    for j in range(i + 3, len(parts)):
                        if parts[j] in ['analyze', 'trend', 'trends', 'analysis', 'for', 'of', 'the']:
                            continue
                        
                        normalized = normalize_feature_name(parts[j], agent.df.columns)
                        if normalized:
                            variable = normalized
                            break
                except (ValueError, IndexError) as e:
                    print(f"Warning: Failed to parse 'last N days' pattern: {e}")
                    continue
        
        # If no date range found, check for variable anywhere in query
        if not variable:
            for part in parts:
                if part in ['analyze', 'trend', 'trends', 'analysis', 'for', 'of', 'the', 'last', 'day', 'days']:
                    continue
                
                normalized = normalize_feature_name(part, agent.df.columns)
                if normalized:
                    variable = normalized
                    break
        
        # If no specific dates provided, use last 30 days as default
        if not start_date_str or not end_date_str:
            current_date = datetime.date(2025, 10, 10)  # Updated to current context date
            start_date = current_date - datetime.timedelta(days=30)
            end_date = current_date
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
    except Exception as parsing_error:
        return json.dumps({
            "error": "Query parsing failed",
            "details": str(parsing_error),
            "query": query
        })
    
    # Validate parameters and run analysis
    try:
        # Validate date range
        if start_date_str and end_date_str:
            try:
                start_dt = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
                end_dt = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
                if start_dt > end_dt:
                    return json.dumps({
                        "error": "Invalid date range",
                        "details": "Start date must be before end date",
                        "start_date": start_date_str,
                        "end_date": end_date_str
                    })
            except ValueError as date_error:
                return json.dumps({
                    "error": "Invalid date format",
                    "details": str(date_error)
                })
        
        # Run analysis with proper error handling
        try:
            # First validate we have valid data to analyze
            if agent.df is None or agent.df.empty:
                return json.dumps({
                    "error": "No data available",
                    "details": "Dataset is empty or not properly loaded",
                    "parameters": {
                        "date_range": {"start": start_date_str, "end": end_date_str},
                        "variable": variable,
                        "query": query
                    }
                })
            
            # Validate we have numeric data
            numeric_cols = agent.df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                return json.dumps({
                    "error": "No numeric data",
                    "details": "No numeric columns available for analysis",
                    "available_columns": list(agent.df.columns)
                })
            
            if variable:
                # Verify the variable exists in the dataframe and is numeric
                if not any(col.lower() == variable.lower() for col in numeric_cols):
                    return json.dumps({
                        "error": "Invalid variable requested",
                        "details": f"Variable '{variable}' not found in numeric data",
                        "available_variables": list(numeric_cols)
                    })
                
                # Get actual column name with correct case
                variable = next(col for col in numeric_cols if col.lower() == variable.lower())
                
                # Verify we have non-null data for the variable
                valid_data = agent.df[variable].notna()
                if not valid_data.any():
                    return json.dumps({
                        "error": "No valid data",
                        "details": f"No non-null values found for {variable}",
                        "date_range": {"start": start_date_str, "end": end_date_str}
                    })
                
                results = agent.analyze_trends(
                    start_date=start_date_str, 
                    end_date=end_date_str,
                    features=variable
                )
                
                if results and not isinstance(results, dict):
                    return json.dumps({
                        "error": "Invalid analysis results",
                        "details": "Expected dictionary result"
                    })
                    
                if "error" not in results:
                    results.update({
                        "requested_feature": variable,
                        "date_range": {
                            "start": start_date_str,
                            "end": end_date_str
                        },
                        "query": query
                    })
            else:
                results = agent.analyze_trends(
                    start_date=start_date_str, 
                    end_date=end_date_str
                )
                
                if results and not isinstance(results, dict):
                    return json.dumps({
                        "error": "Invalid analysis results",
                        "details": "Expected dictionary result"
                    })
                    
                if "error" not in results:
                    results.update({
                        "note": "Analyzed all numeric columns",
                        "date_range": {
                            "start": start_date_str,
                            "end": end_date_str
                        },
                        "query": query
                    })
            
            # Validate results before returning
            if not results:
                return json.dumps({
                    "error": "No results generated",
                    "details": "Analysis completed but no data was produced"
                })
                
            # Check for empty or invalid results
            if isinstance(results, dict) and not any(key for key in results if key not in ['error', 'date_range', 'query', 'note']):
                return json.dumps({
                    "error": "No valid data found",
                    "details": "Analysis completed but no valid data was found for the specified parameters",
                    "parameters": {
                        "date_range": {"start": start_date_str, "end": end_date_str},
                        "variable": variable,
                        "query": query
                    }
                })
            
            return json.dumps(results, indent=2)
            
        except Exception as analysis_error:
            return json.dumps({
                "error": "Analysis execution failed",
                "details": str(analysis_error),
                "parameters": {
                    "date_range": {"start": start_date_str, "end": end_date_str},
                    "variable": variable,
                    "query": query
                }
            })
            
    except Exception as e:
        return json.dumps({
            "error": "Unexpected error in trend analysis",
            "details": str(e),
            "query": query
        })