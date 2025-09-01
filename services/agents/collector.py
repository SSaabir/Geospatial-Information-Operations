import requests
import json

# -- API Collector-- 

def fetch_api_weather():
    """
    Fetches weather data for a given city from the OpenWeatherMap API
    and returns the temprature in Celsius.
    
    """
    TOKEN = "FKmlSONbiymBMpNUOgTleShCUMtNrsMv"
    headers = {'token': TOKEN}
    url = "https://www.ncei.noaa.gov/cdo-web/api/v2/{endpoint}".format(endpoint="datasets")
    
    params = {
        "datasetid": "ACMH",   # Daily summaries
        "locationid": "FIPS:37",  # New York City
        "stationid": "COOP:010957",  # Central Park, NY
        "startdate": "1970-10-03",
        "enddate": "2012-09-10",
        "sortfield": "date",
        "sortorder": "desc",
        "limit": 42, 
        "units": "metric",
        "includemetadata": "false"
    }
    response = requests.get(url,headers=headers ,  params=params)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

# --- Run code here ---
if __name__ == "__main__":
    city = "New York"
    weather_data = fetch_api_weather()
    print(weather_data)
    