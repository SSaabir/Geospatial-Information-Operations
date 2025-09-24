from TrendAgent import TrendAgent
import datetime
import json

def run_trend_agent(query, db_uri="postgresql+psycopg2://postgres:Mathu1312@localhost:5432/GISDb"):
    """
    Run the TrendAgent based on the query.
    
    Args:
        query (str): The user query (e.g., "analyze trends last 20 day cloudcover")
        db_uri (str): PostgreSQL connection URI
    
    Returns:
        str: JSON string of the analysis results or error message
    """
    agent = TrendAgent(db_uri)
    
    if agent.df is None:
        return json.dumps({"error": "Failed to load data from database"})
    
    # Parse the query (e.g., "analyze trends last N day VARIABLE" or "analyze VARIABLE trends")
    parts = query.lower().split()
    start_date = None
    end_date = None
    variable = None
    
    # Check for "last N day" pattern
    for i in range(len(parts)):
        if parts[i] == "last" and i + 2 < len(parts) and parts[i + 2] == "day":
            try:
                N = int(parts[i + 1])
                # Use the provided current date for calculations (2025-09-23)
                current_date = datetime.date(2025, 9, 23)
                start_date = current_date - datetime.timedelta(days=N)
                end_date = current_date
                start_date_str = start_date.strftime("%Y-%m-%d")
                end_date_str = end_date.strftime("%Y-%m-%d")
                # Look for variable after "day" or elsewhere
                for j in range(i + 3, len(parts)):
                    if parts[j] in agent.df.columns:
                        variable = parts[j]
                        break
            except ValueError:
                pass
    
    # If no date range found, check for variable in query
    if not variable:
        for part in parts:
            if part in agent.df.columns:
                variable = part
                break
    
    # Run analysis
    try:
        results = agent.analyze_trends(start_date=start_date_str, end_date=end_date_str)
        
        # If a specific variable was requested, extract it; else return all
        if variable and variable in results:
            results = {variable: results[variable], "date_range": results["date_range"], "data_points": results["data_points"]}
        
        return json.dumps(results)
    except Exception as e:
        return json.dumps({"error": str(e)})