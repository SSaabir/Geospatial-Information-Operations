# ---------------- Existing imports ----------------
import pandas as pd
import numpy as np
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ---------------- Load Dataset ----------------
# (your existing code remains here, unchanged)

# ... [all your existing code remains exactly as you provided] ...
# ... no modifications in your parsing, intent, analysis, pdf, etc. ...

# ---------------- NEW ENTRY POINT ----------------
def run_report_agent(user_query: str, generate_pdf: bool = False) -> str:
    """
    Main entry point for Orchestrator.
    Takes a user query, analyzes it, and returns a climate summary.
    If generate_pdf=True, also creates a PDF report.
    """
    try:
        # Step 1: Extract years + metrics
        extracted = extract_years_and_intent(user_query)

        # Step 2: Generate summary
        summary = generate_targeted_summary(
            extracted["start_year"],
            extracted["end_year"],
            extracted["requested_metrics"]
        )

        # Step 3: (Optional) PDF
        if generate_pdf and not summary.startswith("❌"):
            pdf_file = generate_pdf_report(summary)
            return f"{summary}\n\n📄 PDF report saved as: {pdf_file}"

        return summary

    except Exception as e:
        return f"❌ Report Agent Error: {e}"


# ============================================================
#               LANGCHAIN + LANGGRAPH INTEGRATION
# ============================================================

# ✅ Install first if not done:  pip install langchain langgraph

try:
    from langchain.schema import HumanMessage
    from langchain.chat_models import ChatOpenAI     # or other LLM you use
    from langgraph.graph import StateGraph, END
except ImportError:
    print("⚠️  LangChain or LangGraph not installed. Run: pip install langchain langgraph")

# ---- Define graph state ----
class ReportState(dict):
    """State object passed between graph nodes."""
    pass

# ---- Define graph nodes ----
def parse_query(state: ReportState):
    """Prepare user query for report generation."""
    # Here we just ensure the query exists
    state["user_query"] = state.get("user_query", "")
    return state

def generate_report_node(state: ReportState):
    """Call existing run_report_agent() to generate the report."""
    query = state["user_query"]
    result = run_report_agent(query, generate_pdf=False)
    state["report_result"] = result
    return state

def finish_node(state: ReportState):
    """End of the graph."""
    return state

# ---- Build LangGraph workflow ----
try:
    workflow = StateGraph(ReportState)
    workflow.add_node("parse_query", parse_query)
    workflow.add_node("generate_report", generate_report_node)
    workflow.add_node("finish", finish_node)

    workflow.add_edge("parse_query", "generate_report")
    workflow.add_edge("generate_report", "finish")

    workflow.set_entry_point("parse_query")

    graph = workflow.compile()
except Exception as e:
    print(f"⚠️ LangGraph setup skipped due to error: {e}")

# ---- Optional: LangChain LLM to polish final response ----
try:
    llm = ChatOpenAI(temperature=0)
except Exception as e:
    llm = None
    print("⚠️ LLM not initialized. Install/configure API if needed.")

def run_with_langchain_and_langgraph(user_text: str) -> dict:
    """
    Run the reporting pipeline via LangGraph and optionally
    post-process the output with an LLM.
    """
    init_state = ReportState(user_query=user_text)

    final_state = graph.invoke(init_state)
    raw_report = final_state["report_result"]

    polished = raw_report
    if llm:
        response = llm([HumanMessage(content=f"Make this report concise and clear:\n{raw_report}")])
        polished = response.content

    return {
        "raw_report": raw_report,
        "llm_summary": polished
    }


# ============================================================
#                   COMMAND LINE TEST
# ============================================================

if __name__ == "__main__":
    # Example interactive run
    user_query = input("Enter your climate report query: ")
    results = run_with_langchain_and_langgraph(user_query)
    print("\n==== RAW REPORT ====")
    print(results["raw_report"])
    print("\n==== LLM-REFINED SUMMARY ====")
    print(results["llm_summary"])
