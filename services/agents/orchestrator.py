from langgraph.graph import StateGraph, END, START
from typing import TypedDict
import json
from collector import run_collector_agent         # ✅ Collector agent
from predict.predict_too import run_predict_agent        # ✅ Prediction agent

# -------------------------
# Define workflow state
# -------------------------
class WorkflowState(TypedDict):
    user_input: str
    result: dict
    step: str

'''
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
    '''


# -------------------------
# Define workflow nodes
# -------------------------
def start_node(state: WorkflowState) -> WorkflowState:
    state["step"] = "started"
    return state

def process_node(state: WorkflowState) -> WorkflowState:
    state["step"] = "processing"
    try:
        # 1️⃣ Run collector agent
        query = "get last 7 day weather_data"
        collector_result = run_collector_agent(query)
        print("Debug: Collector Result:", collector_result)

        # 2️⃣ Prepare input for prediction (can use collector_result if needed)
        predict_input = json.dumps({
            "datetime": "02/02/1997",
            "sunrise": "06:59:19 AM",
            "sunset": "06:49:34 PM",
            "humidity": 74.2,
            "sealevelpressure": 1009.4,
            "temp": 24.5
        })

        # 3️⃣ Run prediction agent
        prediction_result = run_predict_agent(predict_input)
        print("Debug: Prediction Result:", prediction_result)

        # 4️⃣ Save both results in state
        state["result"] = {
            "collector_output": collector_result,
            "prediction_output": prediction_result
        }

    except Exception as e:
        state["result"] = {"error": str(e)}

    return state


def end_node(state: WorkflowState) -> WorkflowState:
    state["step"] = "completed"
    return state


# -------------------------
# Build workflow
# -------------------------
workflow = StateGraph(WorkflowState)

workflow.add_node("start", start_node)
workflow.add_node("process", process_node)
workflow.add_node("end", end_node)

workflow.add_edge(START, "start")
workflow.add_edge("start", "process")
workflow.add_edge("process", "end")
workflow.add_edge("end", END)

app = workflow.compile()
print("✅ Workflow with collector + prediction created successfully!")


# -------------------------
# Run workflow
# -------------------------
def run_workflow(user_input: str):
    initial_state = WorkflowState(
        user_input=user_input,
        result={},
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

# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    test_input = "Run weather workflow"
    result = run_workflow(test_input)


    print("\n--- Workflow Output ---")
    print(f"Input: {result['user_input']}")
    print(f"Collector Result: {result['result'].get('collector_output')}")
    print(f"Prediction Result: {result['result'].get('prediction_output')}")
    print(f"Final Step: {result['step']}")
