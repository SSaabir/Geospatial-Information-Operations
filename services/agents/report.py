import pandas as pd
import numpy as np
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ---------------- Load Dataset ----------------
try:
    DF = pd.read_csv("preprocessed_climate_dataset5.csv")
    DF["datetime"] = pd.to_datetime(DF["datetime"], errors="coerce")
    DF["year"] = DF["datetime"].dt.year
    print(f"✅ Dataset loaded: {len(DF)} records from {DF['year'].min()} to {DF['year'].max()}")
    print(f"📋 Available columns: {DF.columns.tolist()}")
except Exception as e:
    print(f"❌ Error loading dataset: {e}")
    DF = pd.DataFrame()

def extract_years_from_text(user_query: str) -> dict:
    """Extract years directly from text using regex patterns."""
    query_lower = user_query.lower()
    
    # Pattern 1: Direct year ranges like "1997-2023", "1997 to 2023", "1997-2023"
    year_range_patterns = [
        r'(\d{4})\s*[-–to]\s*(\d{4})',  # 1997-2023, 1997 to 2023
        r'(\d{4})\s*(\d{4})',           # 1997 2023
        r'from\s*(\d{4})\s*to\s*(\d{4})', # from 1997 to 2023
    ]
    
    for pattern in year_range_patterns:
        match = re.search(pattern, user_query)
        if match:
            start_year = int(match.group(1))
            end_year = int(match.group(2))
            return {"start_year": start_year, "end_year": end_year}
    
    # Pattern 2: Single year like "2022", "in 2023"
    single_year_pattern = r'\b(\d{4})\b'
    years_found = re.findall(single_year_pattern, user_query)
    if years_found:
        year = int(years_found[0])  # Use first year found
        return {"start_year": year, "end_year": year}
    
    # Pattern 3: "last X years"
    last_years_pattern = r'last\s*(\d+)\s*years?'
    match = re.search(last_years_pattern, query_lower)
    if match:
        num_years = int(match.group(1))
        end_year = int(DF['year'].max())
        start_year = end_year - num_years + 1
        return {"start_year": start_year, "end_year": end_year}
    
    # Default: last 5 years
    return {
        "start_year": int(DF['year'].max() - 4),
        "end_year": int(DF['year'].max())
    }

def analyze_query_intent(user_query: str) -> dict:
    """Analyze what specific climate metrics the user wants."""
    query_lower = user_query.lower()
    
    # Define keyword mappings for different climate aspects
    intent_keywords = {
        'temperature': ['temp', 'hot', 'cold', 'warm', 'cool', 'heat', 'thermal'],
        'humidity': ['humid', 'moisture', 'dry', 'wet'],
        'precipitation': ['rain', 'precip', 'rainfall', 'shower', 'storm'],
        'wind': ['wind', 'breeze', 'gust', 'air flow'],
        'pressure': ['pressure', 'barometric', 'atmospheric'],
        'uv': ['uv', 'ultraviolet', 'sun', 'solar', 'radiation'],
        'general': ['summary', 'overview', 'all', 'complete', 'full', 'everything']
    }
    
    # Check which categories match the query
    requested_metrics = []
    for category, keywords in intent_keywords.items():
        if any(keyword in query_lower for keyword in keywords):
            requested_metrics.append(category)
    
    # If no specific metrics found or general terms used, return basic temperature
    if not requested_metrics or 'general' in requested_metrics:
        requested_metrics = ['temperature']  # Default to temperature only
    
    return {
        'metrics': requested_metrics,
        'is_specific': len(requested_metrics) == 1 and 'general' not in requested_metrics
    }

def extract_years_and_intent(user_query: str) -> dict:
    """Extract years and understand what metrics user wants."""
    
    # Step 1: Extract years using regex (more reliable)
    years_info = extract_years_from_text(user_query)
    
    # Step 2: Analyze what climate metrics user wants
    intent = analyze_query_intent(user_query)
    
    # Combine results
    result = {
        "start_year": years_info["start_year"],
        "end_year": years_info["end_year"],
        "requested_metrics": intent['metrics']
    }
    
    print(f"🔍 Query: '{user_query}'")
    print(f"📅 Extracted years: {result['start_year']} to {result['end_year']}")
    print(f"📊 Requested metrics: {result['requested_metrics']}")
    
    return result

def generate_targeted_summary(start_year: int, end_year: int, requested_metrics: list) -> str:
    """Generate a targeted climate summary based on requested metrics only."""
    if DF.empty:
        return "❌ Dataset not loaded properly."
        
    data = DF[(DF["year"] >= start_year) & (DF["year"] <= end_year)]
    
    if data.empty:
        return f"❌ No data available for {start_year}–{end_year}."

    available_columns = data.columns.tolist()
    report_sections = []
    
    # 1. Temperature Analysis (if requested)
    if 'temperature' in requested_metrics:
        if "temp" not in available_columns:
            report_sections.append("❌ Temperature data not available in dataset.")
        else:
            yearly_avg = data.groupby("year")["temp"].mean()
            yearly_max = data.groupby("year")["tempmax"].max() if "tempmax" in available_columns else None
            yearly_min = data.groupby("year")["tempmin"].min() if "tempmin" in available_columns else None

            avg_temp = yearly_avg.mean()
            hottest_year = yearly_avg.idxmax()
            coldest_year = yearly_avg.idxmin()
            temp_trend = yearly_avg.iloc[-1] - yearly_avg.iloc[0]
            temp_trend_direction = "increase" if temp_trend > 0 else "decrease"

            temp_section = [
                f"🌡️ TEMPERATURE ANALYSIS ({start_year}–{end_year})",
                f"Average Temperature: {avg_temp:.2f} °C",
                f"Hottest Year: {hottest_year} ({yearly_avg[hottest_year]:.2f} °C avg)",
                f"Coldest Year: {coldest_year} ({yearly_avg[coldest_year]:.2f} °C avg)",
                f"Temperature Trend: {temp_trend:+.2f} °C ({temp_trend_direction} over period)"
            ]
            
            if yearly_max is not None:
                temp_section.append(f"Highest Recorded: {yearly_max.max():.2f} °C in {yearly_max.idxmax()}")
            if yearly_min is not None:
                temp_section.append(f"Lowest Recorded: {yearly_min.min():.2f} °C in {yearly_min.idxmin()}")
            
            report_sections.append("\n".join(temp_section))

    # 2. Humidity Analysis (if requested and available)
    if 'humidity' in requested_metrics:
        if "humidity" not in available_columns:
            report_sections.append("❌ Humidity data not available in dataset.")
        else:
            yearly_humidity = data.groupby("year")["humidity"].mean()
            avg_humidity = yearly_humidity.mean()
            humidity_trend = yearly_humidity.iloc[-1] - yearly_humidity.iloc[0]
            humidity_direction = "increase" if humidity_trend > 0 else "decrease"
            
            humidity_section = [
                f"💧 HUMIDITY ANALYSIS ({start_year}–{end_year})",
                f"Average Humidity: {avg_humidity:.1f}%",
                f"Humidity Trend: {humidity_trend:+.1f}% ({humidity_direction} over period)",
                f"Most Humid Year: {yearly_humidity.idxmax()} ({yearly_humidity.max():.1f}%)",
                f"Least Humid Year: {yearly_humidity.idxmin()} ({yearly_humidity.min():.1f}%)"
            ]
            report_sections.append("\n".join(humidity_section))

    # 3. Precipitation Analysis (if requested and available)
    if 'precipitation' in requested_metrics:
        precip_columns = [col for col in available_columns if 'precip' in col.lower() or 'rain' in col.lower()]
        if not precip_columns:
            report_sections.append("❌ Precipitation data not available in dataset.")
        else:
            precip_col = precip_columns[0]
            yearly_precip = data.groupby("year")[precip_col].sum()
            avg_precip = yearly_precip.mean()
            precip_trend = yearly_precip.iloc[-1] - yearly_precip.iloc[0]
            precip_direction = "increase" if precip_trend > 0 else "decrease"
            
            precip_section = [
                f"🌧️ PRECIPITATION ANALYSIS ({start_year}–{end_year})",
                f"Average Annual Precipitation: {avg_precip:.1f} mm",
                f"Precipitation Trend: {precip_trend:+.1f} mm ({precip_direction} over period)",
                f"Wettest Year: {yearly_precip.idxmax()} ({yearly_precip.max():.1f} mm)",
                f"Driest Year: {yearly_precip.idxmin()} ({yearly_precip.min():.1f} mm)"
            ]
            report_sections.append("\n".join(precip_section))

    # 4. Wind Analysis (if requested and available)
    if 'wind' in requested_metrics:
        wind_columns = [col for col in available_columns if 'wind' in col.lower()]
        if not wind_columns:
            report_sections.append("❌ Wind data not available in dataset.")
        else:
            wind_col = wind_columns[0]
            yearly_wind = data.groupby("year")[wind_col].mean()
            avg_wind = yearly_wind.mean()
            wind_trend = yearly_wind.iloc[-1] - yearly_wind.iloc[0]
            wind_direction = "increase" if wind_trend > 0 else "decrease"
            
            wind_section = [
                f"💨 WIND ANALYSIS ({start_year}–{end_year})",
                f"Average Wind Speed: {avg_wind:.1f} km/h",
                f"Wind Trend: {wind_trend:+.1f} km/h ({wind_direction} over period)",
                f"Windiest Year: {yearly_wind.idxmax()} ({yearly_wind.max():.1f} km/h avg)",
                f"Calmest Year: {yearly_wind.idxmin()} ({yearly_wind.min():.1f} km/h avg)"
            ]
            report_sections.append("\n".join(wind_section))

    # 5. Pressure Analysis (if requested and available)
    if 'pressure' in requested_metrics:
        pressure_columns = [col for col in available_columns if 'pressure' in col.lower() or 'press' in col.lower()]
        if not pressure_columns:
            report_sections.append("❌ Pressure data not available in dataset.")
        else:
            pressure_col = pressure_columns[0]
            yearly_pressure = data.groupby("year")[pressure_col].mean()
            avg_pressure = yearly_pressure.mean()
            pressure_trend = yearly_pressure.iloc[-1] - yearly_pressure.iloc[0]
            pressure_direction = "increase" if pressure_trend > 0 else "decrease"
            
            pressure_section = [
                f"📊 ATMOSPHERIC PRESSURE ANALYSIS ({start_year}–{end_year})",
                f"Average Pressure: {avg_pressure:.1f} hPa",
                f"Pressure Trend: {pressure_trend:+.1f} hPa ({pressure_direction} over period)",
                f"Highest Pressure Year: {yearly_pressure.idxmax()} ({yearly_pressure.max():.1f} hPa avg)",
                f"Lowest Pressure Year: {yearly_pressure.idxmin()} ({yearly_pressure.min():.1f} hPa avg)"
            ]
            report_sections.append("\n".join(pressure_section))

    # 6. UV Analysis (if requested and available)
    if 'uv' in requested_metrics:
        uv_columns = [col for col in available_columns if 'uv' in col.lower()]
        if not uv_columns:
            report_sections.append("❌ UV data not available in dataset.")
        else:
            uv_col = uv_columns[0]
            yearly_uv = data.groupby("year")[uv_col].mean()
            avg_uv = yearly_uv.mean()
            uv_trend = yearly_uv.iloc[-1] - yearly_uv.iloc[0]
            uv_direction = "increase" if uv_trend > 0 else "decrease"
            
            uv_section = [
                f"☀️ UV INDEX ANALYSIS ({start_year}–{end_year})",
                f"Average UV Index: {avg_uv:.1f}",
                f"UV Trend: {uv_trend:+.1f} ({uv_direction} over period)",
                f"Highest UV Year: {yearly_uv.idxmax()} ({yearly_uv.max():.1f} avg)",
                f"Lowest UV Year: {yearly_uv.idxmin()} ({yearly_uv.min():.1f} avg)"
            ]
            report_sections.append("\n".join(uv_section))

    # If no valid metrics were found/available
    if not report_sections:
        return f"❌ No data available for requested metrics in {start_year}–{end_year}."

    return "\n\n".join(report_sections)

def generate_pdf_report(summary: str, filename: str = "summary_report.pdf") -> str:
    """Generate a PDF report from the summary text."""
    try:
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        
        story = []
        story.append(Paragraph("🌍 Climate Summary Report", styles["Title"]))
        story.append(Spacer(1, 20))
        
        for line in summary.split("\n"):
            if line.strip():
                story.append(Paragraph(line, styles["Normal"]))
                story.append(Spacer(1, 10))
        
        doc.build(story)
        return filename
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None

def get_dataset_info() -> dict:
    """Get information about the loaded dataset."""
    if DF.empty:
        return {
            "status": "error",
            "message": "Dataset not loaded",
            "data_years": None,
            "available_columns": [],
            "total_records": 0
        }
    
    return {
        "status": "healthy",
        "data_years": f"{DF['year'].min()}–{DF['year'].max()}",
        "available_columns": DF.columns.tolist(),
        "total_records": len(DF)
    }   