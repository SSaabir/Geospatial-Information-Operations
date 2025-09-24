
# Simple LangGraph Workflow
from langgraph.graph import StateGraph, END, START
from langchain.tools import tool
from langchain_groq import ChatGroq
from typing import TypedDict, Dict, Any
import json
from collector import run_collector_agent
from trend import run_trend_agent



# Define the state for our workflow
class WorkflowState(TypedDict):
    """Simple state structure for the workflow"""
    user_input: str
    result: str
    step: str


# Define workflow nodes
def start_node(state: WorkflowState) -> WorkflowState:
    """Starting node of the workflow"""
    state["step"] = "started"
    return state

# In orchestrator.py (unchanged, for reference)
def process_node(state: WorkflowState) -> WorkflowState:
    """Processing node"""
    state["step"] = "processing"
    query = state["user_input"].lower()
    
    try:
        # Router logic to select agent
        if any(word in query for word in ["trend", "analyze", "trends", "analysis"]):
            state["agent_used"] = "trend"
            agent_result = run_trend_agent(state["user_input"], db_uri="postgresql+psycopg2://postgres:Mathu1312@localhost:5432/GISDb")
        else:
            state["agent_used"] = "collector"
            agent_result = run_collector_agent(state["user_input"])
        
        state["result"] = agent_result
    except Exception as e:
        state["result"] = f"Error: {e}"
        state["agent_used"] = "error"
    
    return state

def end_node(state: WorkflowState) -> WorkflowState:
    """Final node"""
    state["step"] = "completed"
    return state


# Create and build the workflow
workflow = StateGraph(WorkflowState)

# Add nodes
workflow.add_node("start", start_node)
workflow.add_node("process", process_node)
workflow.add_node("end", end_node)

# Add edges
workflow.add_edge(START, "start")
workflow.add_edge("start", "process")
workflow.add_edge("process", "end")
workflow.add_edge("end", END)

# Compile the workflow
app = workflow.compile()

print("✅ Simple workflow created successfully!")



# Test the workflow
def run_workflow(user_input: str):
    """Run the workflow with user input"""
    initial_state = WorkflowState(
        user_input=user_input,
        result="",
        step=""
    )

    result = app.invoke(initial_state)
    return result

# Example usage
# Test with collector-style query
test_input_collector = "get last 20 day cloudcover"
result_collector = run_workflow(test_input_collector)
print(f"Collector Input: {result_collector['user_input']}")
print(f"Collector Result: {result_collector['result']}")
print(f"Collector Final step: {result_collector['step']}")

# Test with trend-style query (NEW: Added for demonstration)
test_input_trend = "analyze trends last 20 day cloudcover"
result_trend = run_workflow(test_input_trend)
print(f"Trend Input: {result_trend['user_input']}")
print(f"Trend Result: {result_trend['result']}")
print(f"Trend Final step: {result_trend['step']}")

