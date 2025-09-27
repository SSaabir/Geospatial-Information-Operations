from langgraph.graph import StateGraph, END, START
from typing import TypedDict, Optional, List
import json
import os
import re
from dotenv import load_dotenv
from collector import run_collector_agent         # ✅ Collector agent
from TrendAgent import run_trend_analysis_agent   # ✅ Trend agent
from report import run_report_agent               # ✅ Report agent
#from predict.predict_too import run_predict_agent # ✅ Prediction agent

# Load environment variables
load_dotenv()

# -------------------------
# Enhanced Workflow State
# -------------------------
class WorkflowState(TypedDict):
    user_input: str
    workflow_type: str  # "data_view", "collect_analyze", "full_summary"
    collector_result: Optional[str]
    trend_result: Optional[str]  
    report_result: Optional[str]
    final_output: str
    step: str
    error: Optional[str]


# -------------------------
# Query Classification Functions
# -------------------------
def classify_user_intent(user_query: str) -> str:
    """
    Classify user intent into one of three workflow types:
    - data_view: User wants to see available data
    - collect_analyze: User wants to collect and analyze data  
    - full_summary: User wants complete summary with report
    """
    query_lower = user_query.lower()
    
    # Keywords for data viewing (simple data requests)
    view_keywords = [
        "show me data", "display data", "view data", "current data", 
        "existing data", "database content", "list data"
    ]
    
    # Keywords for analysis and recommendations
    analyze_keywords = [
        "analyze", "analysis", "trend", "trends", "pattern", "correlation",
        "forecast", "predict", "model", "statistics", "insights",
        # Added practical query keywords
        "what should", "recommend", "advice", "suggest", "should I",
        "what to wear", "how to", "best time", "conditions for",
        "prepare for", "expect", "planning", "activities"
    ]
    
    # Keywords for reporting/summary
    report_keywords = [
        "summary", "report", "summarize", "overview", "comprehensive",
        "full analysis", "complete", "document", "export", "detailed"
    ]
    
    # Count keyword matches
    view_count = sum(1 for keyword in view_keywords if keyword in query_lower)
    analyze_count = sum(1 for keyword in analyze_keywords if keyword in query_lower) 
    report_count = sum(1 for keyword in report_keywords if keyword in query_lower)
    
    # Check for practical/recommendation queries specifically
    practical_indicators = [
        "what should", "should I", "what to wear", "recommend", "advice", 
        "suggest", "how to", "prepare for", "best time", "conditions for",
        "carry an umbrella", "bring", "need", "planning", "going out"
    ]
    has_practical = any(indicator in query_lower for indicator in practical_indicators)
    
    # Also check for question words that indicate seeking advice
    question_words = ["should", "what", "how", "when", "where", "which"]
    has_question = any(word in query_lower for word in question_words)
    
    # Weather + questions = need analysis for good answers
    weather_mentioned = "weather" in query_lower or "rain" in query_lower or "temperature" in query_lower or "colombo" in query_lower
    
    # Decision logic - improved for better classification
    if report_count > 0 and ("comprehensive" in query_lower or "detailed" in query_lower or "summary" in query_lower or analyze_count > 0):
        return "full_summary"
    elif "generate" in query_lower and ("report" in query_lower or "summary" in query_lower):
        return "full_summary" 
    elif has_practical or analyze_count > 0:
        # Practical queries need analysis to provide good recommendations
        return "collect_analyze" 
    elif weather_mentioned and has_question:
        # Weather-related questions need analysis for proper recommendations
        return "collect_analyze"
    elif any(keyword in query_lower for keyword in ["show me data", "display data", "list data"]):
        return "data_view"
    else:
        # Default fallback
        if len(query_lower.split()) > 8:
            return "full_summary"
        elif any(word in query_lower for word in ["trend", "analyze", "pattern"]):
            return "collect_analyze"
        else:
            return "data_view"

# -------------------------
# Workflow Nodes
# -------------------------
def start_node(state: WorkflowState) -> WorkflowState:
    """Initialize workflow and classify user intent"""
    state["step"] = "started"
    state["workflow_type"] = classify_user_intent(state["user_input"])
    state["error"] = None
    return state

def collector_node(state: WorkflowState) -> WorkflowState:
    """Run collector agent to fetch/view data"""
    state["step"] = "collecting_data"
    try:
        print(f"🔄 Starting Collector Agent...")
        print(f"🔍 Input Query: {state['user_input']}")
        
        collector_result = run_collector_agent(state["user_input"])
        state["collector_result"] = collector_result
        
        print(f"✅ Collector completed: {len(str(collector_result))} characters")
        print(f"📊 Collector Result Preview: {str(collector_result)[:200]}...")
        
    except Exception as e:
        state["error"] = f"Collector failed: {str(e)}"
        print(f"❌ Collector error: {e}")
        import traceback
        print(f"🔍 Full error: {traceback.format_exc()}")
    return state

def trend_analysis_node(state: WorkflowState) -> WorkflowState:
    """Run trend analysis on collected data"""
    state["step"] = "analyzing_trends"
    try:
        print(f"🔬 Starting Trend Analysis...")
        print(f"📊 Input Query: {state['user_input']}")
        
        # Extract date range from user input if available
        date_pattern = r'(\d{4}-\d{2}-\d{2})'
        dates = re.findall(date_pattern, state["user_input"])
        start_date = dates[0] if len(dates) > 0 else None
        end_date = dates[1] if len(dates) > 1 else None
        
        print(f"📅 Date Range: {start_date} to {end_date}")
        
        trend_result = run_trend_analysis_agent(
            state["user_input"], 
            start_date=start_date, 
            end_date=end_date
        )
        state["trend_result"] = trend_result
        
        print(f"✅ Trend analysis completed")
        print(f"📊 Trend Result Length: {len(str(trend_result))} characters")
        print(f"📊 Trend Result Preview: {str(trend_result)[:200]}...")
        
    except Exception as e:
        state["error"] = f"Trend analysis failed: {str(e)}"
        print(f"❌ Trend analysis error: {e}")
        import traceback
        print(f"🔍 Full error: {traceback.format_exc()}")
    return state

def report_generation_node(state: WorkflowState) -> WorkflowState:
    """Generate comprehensive report based on trend analysis"""
    state["step"] = "generating_report"
    try:
        print(f"📋 Starting Report Generation...")
        print(f"📝 Input Query: {state['user_input']}")
        
        # Prepare input for report agent that includes trend analysis
        trend_data = state.get("trend_result", "No trend analysis available")
        collector_data = state.get("collector_result", "No data collected")
        
        report_input = {
            "user_query": state["user_input"],
            "trend_analysis": trend_data,
            "collector_data": collector_data
        }
        
        # Call report agent with trend analysis data
        from report import generate_summary_report
        report_result = generate_summary_report(report_input)
        state["report_result"] = report_result
        
        print(f"✅ Report generated")
        print(f"📋 Report Result Length: {len(str(report_result))} characters")  
        print(f"📋 Report Result Preview: {str(report_result)[:200]}...")
        
    except Exception as e:
        # Fallback to original report agent if new function doesn't exist
        try:
            print(f"⚠️ Using fallback report method...")
            report_result = run_report_agent(state["user_input"], generate_pdf=False)
            state["report_result"] = report_result
        except Exception as e2:
            state["error"] = f"Report generation failed: {str(e)}, Fallback also failed: {str(e2)}"
            print(f"❌ Report error: {e}")
    return state

def output_compilation_node(state: WorkflowState) -> WorkflowState:
    """Compile final output based on workflow type"""
    state["step"] = "compiling_output"
    
    if state.get("error"):
        state["final_output"] = f"❌ Workflow Error: {state['error']}"
        return state
    
    try:
        workflow_type = state["workflow_type"]
        
        if workflow_type == "data_view":
            # Simple data view output
            state["final_output"] = json.dumps({
                "workflow_type": "data_view",
                "query": state["user_input"],
                "data": state.get("collector_result", "No data available"),
                "timestamp": "2025-09-27"
            }, indent=2)
            
        elif workflow_type == "collect_analyze":
            # Data + Analysis output
            state["final_output"] = json.dumps({
                "workflow_type": "collect_analyze", 
                "query": state["user_input"],
                "collected_data": state.get("collector_result", "No data collected"),
                "trend_analysis": state.get("trend_result", "No analysis performed"),
                "timestamp": "2025-09-27"
            }, indent=2)
            
        elif workflow_type == "full_summary":
            # Complete workflow output
            state["final_output"] = json.dumps({
                "workflow_type": "full_summary",
                "query": state["user_input"], 
                "collected_data": state.get("collector_result", "No data collected"),
                "trend_analysis": state.get("trend_result", "No analysis performed"),
                "comprehensive_report": state.get("report_result", "No report generated"),
                "timestamp": "2025-09-27"
            }, indent=2)
            
    except Exception as e:
        state["final_output"] = f"❌ Output compilation failed: {str(e)}"
    
    return state

def end_node(state: WorkflowState) -> WorkflowState:
    """Finalize workflow"""
    state["step"] = "completed"
    return state


# -------------------------
# Build Enhanced Workflow with Conditional Logic
# -------------------------
workflow = StateGraph(WorkflowState)

# Add all nodes
workflow.add_node("start", start_node)
workflow.add_node("collector", collector_node)
workflow.add_node("trend_analysis", trend_analysis_node)
workflow.add_node("report_generation", report_generation_node)
workflow.add_node("output_compilation", output_compilation_node)
workflow.add_node("end", end_node)

# Define conditional routing based on workflow type
def should_run_trend_analysis(state: WorkflowState) -> str:
    """Route to trend analysis if workflow requires it"""
    workflow_type = state.get("workflow_type", "data_view")
    print(f"🔀 Routing decision after collector: workflow_type={workflow_type}")
    
    if workflow_type in ["collect_analyze", "full_summary"]:
        print(f"➡️ Routing to trend_analysis")
        return "trend_analysis"
    else:
        print(f"➡️ Routing directly to output_compilation")
        return "output_compilation"

def should_run_report_generation(state: WorkflowState) -> str:
    """Route to report generation for analysis requests"""
    workflow_type = state.get("workflow_type", "data_view")
    print(f"🔀 Routing decision after trend analysis: workflow_type={workflow_type}")
    
    # Generate user-friendly reports for both full summaries and analysis requests
    if workflow_type in ["full_summary", "collect_analyze"]:
        print(f"➡️ Routing to report_generation")
        return "report_generation"
    else:
        print(f"➡️ Routing directly to output_compilation")
        return "output_compilation"

# Add edges
workflow.add_edge(START, "start")
workflow.add_edge("start", "collector")
workflow.add_conditional_edges(
    "collector",
    should_run_trend_analysis,
    {
        "trend_analysis": "trend_analysis",
        "output_compilation": "output_compilation"
    }
)
workflow.add_conditional_edges(
    "trend_analysis", 
    should_run_report_generation,
    {
        "report_generation": "report_generation",
        "output_compilation": "output_compilation"
    }
)
workflow.add_edge("report_generation", "output_compilation")
workflow.add_edge("output_compilation", "end")
workflow.add_edge("end", END)

app = workflow.compile()
print("✅ Enhanced orchestrator workflow created successfully!")


# -------------------------
# Main Orchestrator Functions
# -------------------------
def run_orchestrator_workflow(user_input: str) -> dict:
    """
    Main entry point for orchestrator. Routes user queries through appropriate workflow.
    
    Args:
        user_input (str): User's natural language query
        
    Returns:
        dict: Complete workflow results including all agent outputs
    """
    initial_state = WorkflowState(
        user_input=user_input,
        workflow_type="",
        collector_result=None,
        trend_result=None, 
        report_result=None,
        final_output="",
        step="",
        error=None
    )
    
    try:
        result = app.invoke(initial_state)
        return result
    except Exception as e:
        return {
            "user_input": user_input,
            "error": f"Orchestrator failed: {str(e)}",
            "final_output": f"❌ Workflow execution failed: {str(e)}",
            "step": "error"
        }

def get_workflow_summary(user_input: str) -> str:
    """
    Get a concise summary of what workflow will be executed for a given query.
    
    Args:
        user_input (str): User's query
        
    Returns:
        str: Description of the workflow that will be executed
    """
    workflow_type = classify_user_intent(user_input)
    
    workflow_descriptions = {
        "data_view": "📊 Data View Workflow: Collector Agent → Display Available Data",
        "collect_analyze": "🔬 Collect & Analyze Workflow: Collector Agent → Trend Analysis Agent → Results", 
        "full_summary": "📋 Full Summary Workflow: Collector Agent → Trend Analysis Agent → Report Generation Agent → Comprehensive Summary"
    }
    
    return workflow_descriptions.get(workflow_type, "❓ Unknown workflow type")

# -------------------------
# Example Usage & Testing
# -------------------------
def test_all_workflows():
    """Test all three workflow types"""
    
    test_cases = [
        # Data View Tests
        {
            "query": "Show me available weather data",
            "expected_type": "data_view"
        },
        {
            "query": "Get current temperature data from database", 
            "expected_type": "data_view"
        },
        
        # Collect & Analyze Tests  
        {
            "query": "Analyze temperature trends for the past month",
            "expected_type": "collect_analyze"
        },
        {
            "query": "Find patterns in humidity and rainfall correlation",
            "expected_type": "collect_analyze"
        },
        
        # Full Summary Tests
        {
            "query": "Generate comprehensive climate summary report for Sri Lanka",
            "expected_type": "full_summary" 
        },
        {
            "query": "Create detailed analysis summary of weather patterns with trends",
            "expected_type": "full_summary"
        }
    ]
    
    print("🧪 Testing Orchestrator Workflow Classification...")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        expected = test_case["expected_type"]
        actual = classify_user_intent(query)
        
        status = "✅" if actual == expected else "❌"
        print(f"{status} Test {i}: {actual}")
        print(f"   Query: {query}")
        print(f"   Expected: {expected}, Got: {actual}")
        print(f"   Workflow: {get_workflow_summary(query)}")
        print()

if __name__ == "__main__":
    # Run classification tests
    test_all_workflows()
    
    print("\n🚀 Running Sample Workflows...")
    print("=" * 60)
    
    # Test each workflow type
    sample_queries = [
        "Show me recent weather data of colombo from the db",  # data_view
        "Analyze temperature trends over the last week of colombo from the db", # collect_analyze  
        "Create a comprehensive climate report summary of colombo from the db" # full_summary
    ]
    
    for query in sample_queries:
        print(f"\n📝 Query: {query}")
        print(f"🎯 Workflow: {get_workflow_summary(query)}")
        
        # Execute the actual workflow
        try:
            print("🔄 Executing workflow...")
            result = run_orchestrator_workflow(query)
            
            print(f"✅ Status: {result.get('step', 'unknown')}")
            print(f"� Workflow Type: {result.get('workflow_type', 'unknown')}")
            
            if result.get('error'):
                print(f"❌ Error: {result['error']}")
            else:
                print(f"📊 Final Output Preview: {str(result.get('final_output', 'No output'))[:300]}...")
                
            # Show which agents were executed
            executed_agents = []
            if result.get('collector_result'):
                executed_agents.append('Collector Agent')
            if result.get('trend_result'):
                executed_agents.append('Trend Analysis Agent')  
            if result.get('report_result'):
                executed_agents.append('Report Generation Agent')
                
            print(f"🤖 Executed Agents: {executed_agents}")
            
        except Exception as e:
            print(f"❌ Workflow execution failed: {str(e)}")
        
        print("-" * 50)
        
    print("\n✅ Orchestrator setup complete! Use run_orchestrator_workflow(query) to execute.")
