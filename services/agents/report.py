# Report Agent for Climate Data Analysis
import os
import pandas as pd
import numpy as np
import re
import json
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import sqlalchemy
from sqlalchemy import create_engine
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize LLM for intelligent report generation
llm = ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3  # Lower temperature for more factual, consistent reports
)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:ElDiabloX32@localhost:5432/PstDB")

def load_climate_data():
    """Load climate data from PostgreSQL database."""
    try:
        engine = create_engine(DATABASE_URL)
        query = "SELECT * FROM weather_data ORDER BY datetime"
        df = pd.read_sql(query, engine)
        engine.dispose()
        
        if df.empty:
            return pd.DataFrame()
            
        # Convert datetime column
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['year'] = df['datetime'].dt.year
        df['month'] = df['datetime'].dt.month
        
        return df
        
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

def extract_years_and_intent(user_query: str) -> dict:
    """Extract years and metrics from user query."""
    query = user_query.lower()
    
    # Extract years
    year_matches = re.findall(r'\b(19|20)\d{2}\b', query)
    years = [int(y) for y in year_matches]
    
    current_year = datetime.now().year
    start_year = min(years) if years else current_year - 1
    end_year = max(years) if years else current_year
    
    # Extract requested metrics
    metrics = []
    if any(word in query for word in ['temperature', 'temp', 'hot', 'cold']):
        metrics.extend(['temp', 'tempmax', 'tempmin'])
    if any(word in query for word in ['rain', 'precipitation', 'rainfall']):
        metrics.extend(['rain', 'rainsum'])
    if any(word in query for word in ['humidity', 'moisture']):
        metrics.append('humidity')
    if any(word in query for word in ['wind', 'windy']):
        metrics.extend(['windspeed', 'windgust'])
    if any(word in query for word in ['pressure']):
        metrics.append('sealevelpressure')
    if any(word in query for word in ['cloud', 'cloudy']):
        metrics.append('cloudcover')
    
    # If no specific metrics, include all major ones
    if not metrics:
        metrics = ['temp', 'tempmax', 'tempmin', 'humidity', 'rain', 'rainsum', 'windspeed']
    
    return {
        "start_year": start_year,
        "end_year": end_year,
        "requested_metrics": metrics
    }

def analyze_climate_trends(df: pd.DataFrame, metrics: list) -> dict:
    """Analyze climate trends in the data."""
    if df.empty:
        return {"error": "No data available for analysis"}
    
    analysis = {
        "period": f"{df['datetime'].min().strftime('%Y-%m-%d')} to {df['datetime'].max().strftime('%Y-%m-%d')}",
        "total_records": len(df),
        "metrics_analysis": {}
    }
    
    for metric in metrics:
        if metric in df.columns:
            values = df[metric].dropna()
            if len(values) > 0:
                analysis["metrics_analysis"][metric] = {
                    "mean": float(values.mean()),
                    "min": float(values.min()),
                    "max": float(values.max()),
                    "std": float(values.std()) if len(values) > 1 else 0,
                    "trend": "stable"  # Simple trend analysis
                }
                
                # Simple trend detection
                if len(values) >= 3:
                    recent_avg = values.tail(3).mean()
                    early_avg = values.head(3).mean()
                    if recent_avg > early_avg * 1.1:
                        analysis["metrics_analysis"][metric]["trend"] = "increasing"
                    elif recent_avg < early_avg * 0.9:
                        analysis["metrics_analysis"][metric]["trend"] = "decreasing"
    
    return analysis

def generate_climate_summary(analysis: dict) -> str:
    """Generate a human-readable climate summary."""
    if "error" in analysis:
        return f"❌ Analysis Error: {analysis['error']}"
    
    summary = f"📊 Climate Data Analysis Report\n"
    summary += f"Period: {analysis['period']}\n"
    summary += f"Total Records: {analysis['total_records']}\n\n"
    
    if not analysis["metrics_analysis"]:
        return summary + "No metric data available for analysis."
    
    summary += "🌡️ Metrics Summary:\n"
    for metric, data in analysis["metrics_analysis"].items():
        summary += f"\n{metric.upper()}:\n"
        summary += f"  • Average: {data['mean']:.2f}\n"
        summary += f"  • Range: {data['min']:.2f} - {data['max']:.2f}\n"
        summary += f"  • Trend: {data['trend']}\n"
        if data['std'] > 0:
            summary += f"  • Variability: {data['std']:.2f}\n"
    
    return summary

def generate_targeted_summary(start_year: int, end_year: int, requested_metrics: list) -> str:
    """Generate a targeted climate summary for specific years and metrics."""
    try:
        df = load_climate_data()
        
        if df.empty:
            return "❌ No climate data available in database"
        
        # Filter by year range if data has year info
        if 'year' in df.columns:
            df_filtered = df[(df['year'] >= start_year) & (df['year'] <= end_year)]
        else:
            df_filtered = df
        
        if df_filtered.empty:
            return f"❌ No data available for years {start_year}-{end_year}"
        
        analysis = analyze_climate_trends(df_filtered, requested_metrics)
        return generate_climate_summary(analysis)
        
    except Exception as e:
        return f"❌ Report Generation Error: {str(e)}"

def generate_pdf_report(summary_text: str, filename: str = None) -> str:
    """Generate a PDF report from summary text."""
    try:
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"climate_report_{timestamp}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title = Paragraph("Climate Data Analysis Report", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Content
        lines = summary_text.split('\n')
        for line in lines:
            if line.strip():
                if line.startswith('📊') or line.startswith('🌡️'):
                    para = Paragraph(line, styles['Heading2'])
                else:
                    para = Paragraph(line, styles['Normal'])
                story.append(para)
                story.append(Spacer(1, 6))
        
        doc.build(story)
        return filename
        
    except Exception as e:
        return f"❌ PDF Generation Error: {str(e)}"

def generate_llm_report(user_query: str, collector_data: str, trend_analysis: str, visualizations: dict = None) -> str:
    """
    Use LLM to generate an intelligent, natural language report from raw data.
    This handles ANY type of data - weather, ethics, or whatever the collector returned.
    """
    try:
        # Prepare context for the LLM
        prompt = f"""You are a professional data analyst creating a comprehensive report.

USER QUERY: {user_query}

COLLECTED DATA:
{collector_data[:3000]}  # Limit to prevent token overflow

TREND ANALYSIS:
{trend_analysis[:2000] if trend_analysis else "No trend analysis available"}

{"VISUALIZATIONS: " + str(len(visualizations)) + " charts were generated" if visualizations else ""}

INSTRUCTIONS:
1. Analyze the collected data and provide a clear, professional summary
2. If the data is weather-related, provide temperature, humidity, rainfall insights
3. If the data is about other topics, analyze what was actually returned
4. Include key statistics and trends
5. Provide actionable insights and recommendations
6. Use clear sections with emojis for readability
7. Keep the report concise (300-500 words)
8. If there's an error in the data, explain it clearly and suggest how to fix the query

REPORT FORMAT:
📊 ANALYSIS REPORT
==================

📋 SUMMARY:
[Brief overview of what data was analyzed]

🔍 KEY FINDINGS:
[Main insights from the data]

📈 TRENDS & PATTERNS:
[Notable trends if any]

💡 RECOMMENDATIONS:
[Actionable suggestions based on the analysis]

Generate the report now:"""

        # Call LLM to generate report
        response = llm.invoke(prompt)
        
        # Extract content from response
        if hasattr(response, 'content'):
            report = response.content
        else:
            report = str(response)
        
        # Add metadata footer
        report += f"\n\n---\n🎯 Query Addressed: {user_query}\n"
        report += f"📅 Analysis Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return report
        
    except Exception as e:
        # NO FALLBACK - Show the actual error
        import traceback
        error_details = traceback.format_exc()
        return f"❌ LLM REPORT GENERATION ERROR\n\n{str(e)}\n\nFull traceback:\n{error_details}"

def generate_summary_report(input_data: dict) -> str:
    """
    Generate a summary report based on trend analysis results.
    This is the main function called by the orchestrator.
    NOW USES LLM FOR INTELLIGENT REPORT GENERATION!
    """
    try:
        user_query = input_data.get("user_query", "")
        trend_analysis = input_data.get("trend_analysis", "")
        collector_data = input_data.get("collector_data", "")
        visualizations = input_data.get("session_metadata", {}).get("visualizations", {})
        
        # DEBUG: Print what we received
        print(f"\n{'='*60}")
        print(f"🔍 REPORT GENERATION DEBUG")
        print(f"{'='*60}")
        print(f"📊 Collector Data Type: {type(collector_data)}")
        print(f"📊 Collector Data Length: {len(str(collector_data))}")
        print(f"📊 Collector Data Preview: {str(collector_data)[:200]}...")
        print(f"📈 Trend Analysis Type: {type(trend_analysis)}")
        print(f"📈 Trend Analysis: {str(trend_analysis)[:200]}...")
        print(f"📊 Visualizations: {visualizations}")
        print(f"{'='*60}\n")
        
        # Convert trend_analysis to string if it's a dict
        if isinstance(trend_analysis, dict):
            trend_analysis = json.dumps(trend_analysis, indent=2)
        
        # Convert collector_data to string if it's a dict
        if isinstance(collector_data, dict):
            collector_data = json.dumps(collector_data, indent=2)
        
        # Use LLM to generate intelligent report
        print("🤖 Generating LLM-powered report...")
        llm_report = generate_llm_report(user_query, collector_data, trend_analysis, visualizations)
        
        # Return the LLM report directly (no fallback!)
        return llm_report
        
    except Exception as e:
        # NO FALLBACK - Show the actual error
        import traceback
        error_details = traceback.format_exc()
        return f"❌ SUMMARY REPORT ERROR\n\n{str(e)}\n\nFull traceback:\n{error_details}"

def generate_trend_summary(trend_data: dict, user_query: str) -> str:
    """Generate a user-friendly, non-technical summary from trend analysis data."""
    try:
        summary = "🌤️ WEATHER ANALYSIS REPORT FOR COLOMBO\n"
        summary += "=" * 50 + "\n\n"
        
        # Dataset overview - make it user-friendly
        if "dataset_info" in trend_data:
            dataset = trend_data["dataset_info"]
            record_count = dataset.get('shape', [0, 0])[0]
            
            if "date_range" in dataset:
                start_date = dataset['date_range']['start'][:10]  # Just the date part
                end_date = dataset['date_range']['end'][:10]
                summary += f"📅 Analysis Period: {start_date} to {end_date}\n"
                summary += f"📊 Data Points: {record_count} daily weather records\n"
                summary += f"🌍 Location: Colombo, Sri Lanka\n\n"
            
            # Add weather context
            if record_count < 7:
                summary += "📝 Note: This analysis covers less than a week of data.\n\n"
            elif record_count < 30:
                summary += "📝 Note: This analysis covers several weeks of weather data.\n\n"
            else:
                summary += "📝 Note: This analysis covers an extended period of weather observations.\n\n"
        
        # Extract and present analysis results in plain language
        analysis_results = trend_data.get("analysis_results", {})
        
        # Temperature Analysis - Make it conversational
        if "temp" in analysis_results:
            temp_data = analysis_results["temp"]
            avg_temp = temp_data.get("mean", 0)
            min_temp = temp_data.get("min", 0)
            max_temp = temp_data.get("max", 0)
            temp_trend = temp_data.get("trend", {})
            
            summary += f"🌡️ TEMPERATURE OVERVIEW:\n"
            summary += f"   • Average Temperature: {avg_temp:.1f}°C ({avg_temp * 9/5 + 32:.1f}°F)\n"
            summary += f"   • Temperature Range: {min_temp:.1f}°C to {max_temp:.1f}°C\n"
            
            # Interpret temperature trend
            if temp_trend.get("slope", 0) > 0.05:
                summary += f"   • Trend: Temperatures are gradually increasing over time ↗️\n"
            elif temp_trend.get("slope", 0) < -0.05:
                summary += f"   • Trend: Temperatures are gradually decreasing over time ↘️\n"
            else:
                summary += f"   • Trend: Temperatures remain fairly stable 📊\n"
            
            # Comfort assessment
            if avg_temp > 30:
                summary += f"   • Comfort: Hot weather conditions prevailing\n"
            elif avg_temp > 25:
                summary += f"   • Comfort: Warm and pleasant weather conditions\n"
            else:
                summary += f"   • Comfort: Mild temperature conditions\n"
            summary += "\n"
        
        # Humidity Analysis
        if "humidity" in analysis_results:
            humidity_data = analysis_results["humidity"]
            avg_humidity = humidity_data.get("mean", 0)
            
            summary += f"💧 HUMIDITY CONDITIONS:\n"
            summary += f"   • Average Humidity: {avg_humidity:.1f}%\n"
            
            if avg_humidity > 80:
                summary += f"   • Conditions: High humidity - may feel muggy and sticky\n"
            elif avg_humidity > 60:
                summary += f"   • Conditions: Moderate humidity - generally comfortable\n"
            else:
                summary += f"   • Conditions: Low humidity - may feel dry\n"
            summary += "\n"
        
        # Rainfall Analysis
        if "rainsum" in analysis_results:
            rain_data = analysis_results["rainsum"]
            avg_rain = rain_data.get("mean", 0)
            max_rain = rain_data.get("max", 0)
            
            summary += f"🌧️ RAINFALL PATTERNS:\n"
            summary += f"   • Average Daily Rainfall: {avg_rain:.1f}mm\n"
            summary += f"   • Highest Daily Rainfall: {max_rain:.1f}mm\n"
            
            if avg_rain > 10:
                summary += f"   • Pattern: Frequent rainy days - expect regular showers\n"
            elif avg_rain > 5:
                summary += f"   • Pattern: Occasional rain showers\n"
            else:
                summary += f"   • Pattern: Mostly dry conditions\n"
            summary += "\n"
        
        # Wind Conditions
        if "windspeed" in analysis_results:
            wind_data = analysis_results["windspeed"]
            avg_wind = wind_data.get("mean", 0)
            
            summary += f"💨 WIND CONDITIONS:\n"
            summary += f"   • Average Wind Speed: {avg_wind:.1f} km/h\n"
            
            if avg_wind > 25:
                summary += f"   • Conditions: Windy conditions - expect breezy weather\n"
            elif avg_wind > 15:
                summary += f"   • Conditions: Moderate breeze - pleasant wind conditions\n"
            else:
                summary += f"   • Conditions: Light winds - mostly calm weather\n"
            summary += "\n"
        
        # Weather Summary for Regular People
        summary += f"🎯 WHAT THIS MEANS FOR YOU:\n"
        
        # Overall weather assessment
        if analysis_results:
            temp_data = analysis_results.get("temp", {})
            humidity_data = analysis_results.get("humidity", {})
            rain_data = analysis_results.get("rainsum", {})
            
            avg_temp = temp_data.get("mean", 27)
            avg_humidity = humidity_data.get("mean", 80)
            avg_rain = rain_data.get("mean", 5)
            
            # Clothing recommendations
            summary += f"   👕 What to Wear:\n"
            if avg_temp > 30:
                summary += f"      • Light, breathable clothing recommended\n"
                summary += f"      • Sun protection advisable\n"
            elif avg_temp > 25:
                summary += f"      • Comfortable summer clothing\n"
                summary += f"      • Light fabrics work well\n"
            else:
                summary += f"      • Light layers recommended\n"
            
            # Activity suggestions
            summary += f"   🏃 Activity Recommendations:\n"
            if avg_rain > 10:
                summary += f"      • Plan indoor activities or carry umbrellas\n"
            elif avg_humidity > 85:
                summary += f"      • Early morning or evening outdoor activities\n"
            else:
                summary += f"      • Good conditions for outdoor activities\n"
            
            # Health considerations
            summary += f"   💊 Health & Comfort:\n"
            if avg_humidity > 85 and avg_temp > 28:
                summary += f"      • Stay hydrated - hot and humid conditions\n"
                summary += f"      • Take breaks in air-conditioned spaces\n"
            elif avg_temp > 30:
                summary += f"      • Drink plenty of water\n"
                summary += f"      • Avoid prolonged sun exposure\n"
            else:
                summary += f"      • Generally comfortable weather conditions\n"
            
            summary += "\n"
        
        # Simple trend explanation
        summary += f"📈 RECENT CHANGES:\n"
        changes_found = False
        
        for metric in ["temp", "humidity", "rainsum"]:
            if metric in analysis_results:
                trend = analysis_results[metric].get("trend", {})
                slope = trend.get("slope", 0)
                p_value = trend.get("p_value", 1)
                
                if p_value < 0.05:  # Statistically significant
                    changes_found = True
                    if metric == "temp":
                        if slope > 0:
                            summary += f"   🌡️ Temperatures have been gradually rising\n"
                        else:
                            summary += f"   🌡️ Temperatures have been gradually cooling\n"
                    elif metric == "humidity":
                        if slope > 0:
                            summary += f"   💧 Humidity levels are increasing\n"
                        else:
                            summary += f"   � Humidity levels are decreasing\n"
                    elif metric == "rainsum":
                        if slope > 0:
                            summary += f"   🌧️ Rainfall amounts are increasing\n"
                        else:
                            summary += f"   🌧️ Rainfall amounts are decreasing\n"
        
        if not changes_found:
            summary += f"   📊 Weather conditions remain relatively stable\n"
            summary += f"   📅 No significant changes observed in the analysis period\n"
        
        summary += "\n"
        
        # If we don't have structured data, provide a general summary
        if len(summary) < 200:
            summary = f"📊 CLIMATE ANALYSIS SUMMARY\n"
            summary += f"=" * 40 + "\n\n"
            summary += f"Based on the analysis of available climate data:\n\n"
            
            # Try to extract some basic info from raw data
            raw_text = str(trend_data)
            if "temperature" in raw_text.lower():
                summary += f"• Temperature patterns have been analyzed\n"
            if "humidity" in raw_text.lower():
                summary += f"• Humidity trends have been examined\n"
            if "rain" in raw_text.lower():
                summary += f"• Rainfall patterns have been studied\n"
            
            summary += f"\nThe analysis reveals various climate patterns and trends "
            summary += f"that provide insights into regional weather behavior.\n"
        
        summary += f"\n🎯 Query Addressed: {user_query}\n"
        summary += f"📅 Analysis Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return summary
        
    except Exception as e:
        return f"❌ Trend Summary Error: {str(e)}"

def run_report_agent(user_query: str, generate_pdf: bool = False) -> str:
    """
    Original report agent function - kept for backwards compatibility.
    Takes a user query, analyzes it, and returns a climate summary.
    If generate_pdf=True, also creates a PDF report.
    """
    try:
        # Step 1: Extract years + metrics from query
        extracted = extract_years_and_intent(user_query)
        
        # Step 2: Generate summary
        summary = generate_targeted_summary(
            extracted["start_year"],
            extracted["end_year"], 
            extracted["requested_metrics"]
        )
        
        # Step 3: Optional PDF generation
        if generate_pdf and not summary.startswith("❌"):
            pdf_file = generate_pdf_report(summary)
            if not pdf_file.startswith("❌"):
                return f"{summary}\n\n📄 PDF report saved as: {pdf_file}"
        
        return summary
        
    except Exception as e:
        return f"❌ Report Agent Error: {str(e)}"


# ============================================================
#               LANGCHAIN + LANGGRAPH INTEGRATION
# ============================================================

try:
    from langchain_core.messages import HumanMessage
    from langchain_groq import ChatGroq
    from langgraph.graph import StateGraph, END
    
    # Define graph state
    class ReportState(dict):
        """State object passed between graph nodes."""
        pass
    
    # Define graph nodes
    def parse_query_node(state: ReportState):
        """Prepare user query for report generation."""
        state["user_query"] = state.get("user_query", "")
        state["generate_pdf"] = state.get("generate_pdf", False)
        return state
    
    def generate_report_node(state: ReportState):
        """Call generate_summary_report to create a trend-based summary."""
        query = state["user_query"]
        pdf = state.get("generate_pdf", False)
        
        # Check if we have trend analysis data in state
        trend_data = state.get("trend_analysis", "")
        collector_data = state.get("collector_data", "")
        
        if trend_data:
            # Use new summary function with trend data
            report_input = {
                "user_query": query,
                "trend_analysis": trend_data,
                "collector_data": collector_data
            }
            result = generate_summary_report(report_input)
        else:
            # Fall back to original function
            result = run_report_agent(query, generate_pdf=pdf)
            
        state["report_result"] = result
        return state
    
    def finish_node(state: ReportState):
        """End of the graph."""
        return state
    
    # Build LangGraph workflow
    workflow = StateGraph(ReportState)
    workflow.add_node("parse_query", parse_query_node)
    workflow.add_node("generate_report", generate_report_node)
    workflow.add_node("finish", finish_node)
    
    workflow.add_edge("parse_query", "generate_report")
    workflow.add_edge("generate_report", "finish")
    workflow.set_entry_point("parse_query")
    
    graph = workflow.compile()
    
    # Optional LLM for response polishing
    try:
        groq_api_key = os.getenv("GROQ_API_KEY")
        if groq_api_key:
            llm = ChatGroq(
                groq_api_key=groq_api_key,
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                temperature=0
            )
        else:
            llm = None
            print("⚠️ GROQ_API_KEY not found in environment")
    except Exception as e:
        llm = None
        print(f"⚠️ LLM not initialized: {e}")

    def run_with_langchain_and_langgraph(user_text: str, generate_pdf: bool = False) -> dict:
        """
        Run the reporting pipeline via LangGraph and optionally
        post-process the output with an LLM.
        """
        init_state = ReportState(user_query=user_text, generate_pdf=generate_pdf)
        
        final_state = graph.invoke(init_state)
        raw_report = final_state["report_result"]
        
        polished = raw_report
        if llm and not raw_report.startswith("❌"):
            try:
                response = llm.invoke([HumanMessage(content=f"Make this climate report more concise and professional:\n\n{raw_report}")])
                polished = response.content
            except Exception as e:
                print(f"⚠️ LLM polishing failed: {e}")
        
        return {
            "raw_report": raw_report,
            "llm_summary": polished,
            "status": "success" if not raw_report.startswith("❌") else "error"
        }

except ImportError as e:
    print(f"⚠️ LangChain/LangGraph not fully available: {e}")
    
    def run_with_langchain_and_langgraph(user_text: str, generate_pdf: bool = False) -> dict:
        """Fallback function when LangGraph is not available."""
        result = run_report_agent(user_text, generate_pdf)
        return {
            "raw_report": result,
            "llm_summary": result,
            "status": "success" if not result.startswith("❌") else "error"
        }

# ============================================================
#                   COMMAND LINE TEST
# ============================================================

if __name__ == "__main__":
    # Test with sample query
    test_query = "Generate climate report for temperature and rainfall"
    print("🧪 Testing Report Agent...")
    print(f"Query: {test_query}")
    print("\n" + "="*50)
    
    results = run_with_langchain_and_langgraph(test_query)
    
    print("📋 RAW REPORT:")
    print(results["raw_report"])
    
    if results["llm_summary"] != results["raw_report"]:
        print("\n🤖 LLM-REFINED SUMMARY:")
        print(results["llm_summary"])
    
    print(f"\n✅ Status: {results['status']}")
