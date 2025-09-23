
# Simple LangGraph Workflow
from langgraph.graph import StateGraph, END, START
from langchain.tools import tool
from langchain_groq import ChatGroq
from typing import TypedDict, Dict, Any
import json
from collector import run_collector_agent



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

def process_node(state: WorkflowState) -> WorkflowState:
    """Processing node"""
    state["step"] = "processing"
    # Send query to collector agent
    query = "get last 7 day weather_data"
    try:
        agent_result = run_collector_agent(query)
        state["result"] = agent_result
    except Exception as e:
        state["result"] = f"Error: {e}"
    
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
test_input = "Hello, this is a test"
result = run_workflow(test_input)

print(f"Input: {result['user_input']}")
print(f"Result: {result['result']}")
print(f"Final step: {result['step']}")

