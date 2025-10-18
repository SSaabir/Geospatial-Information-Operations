"""
Enhanced Multi-Agent Orchestrator with Security and Responsible AI Integration
Coordinates weather analysis agents with comprehensive security monitoring and ethical oversight
"""

import os
import json
import re
import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np
from langgraph.graph import StateGraph, END, START
from typing import TypedDict
from dotenv import load_dotenv

# Import existing agents
import sys
if __name__ == "__main__" or __package__:
    from .collector import run_collector_agent
    # Only import TrendAgent and others if not a direct SQL query
    if not (len(sys.argv) > 1 and sys.argv[1].strip().startswith('query_postgresql_tool')):
        from .TrendAgent import run_trend_analysis_agent, TrendAgent  # Import TrendAgent
        from .report import generate_summary_report
        from .security_agent import run_security_agent, get_security_agent
        from .responsible_ai import run_responsible_ai_assessment, get_responsible_ai_framework
else:
    from collector import run_collector_agent
    from TrendAgent import run_trend_analysis_agent, TrendAgent  # Import TrendAgent
    from report import generate_summary_report
    from security_agent import run_security_agent, get_security_agent
    from responsible_ai import run_responsible_ai_assessment, get_responsible_ai_framework

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowPriority(Enum):
    """Workflow execution priorities"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AgentStatus(Enum):
    """Agent execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class AgentResult:
    """Result from agent execution"""
    agent_name: str
    status: AgentStatus
    execution_time: float
    output: Any
    error: Optional[str] = None
    security_validated: bool = False
    ethics_validated: bool = False
    metadata: Optional[Dict] = None

class EnhancedWorkflowState(TypedDict):
    """Enhanced state for multi-agent workflow with security and ethics"""
    # User input and workflow management
    user_input: str
    workflow_type: str
    priority: str
    session_id: str
    user_context: Optional[Dict]
    
    # Agent execution tracking
    agent_execution_plan: Optional[List[str]]
    agent_results: Optional[Dict[str, AgentResult]]
    current_agent: Optional[str]
    
    # Core agent outputs
    collector_result: Optional[str]
    trend_result: Optional[str]
    report_result: Optional[str]
    visualization_paths: Optional[Dict]
    
    # Security and ethics monitoring
    security_assessment: Optional[Dict]
    ethics_assessment: Optional[Dict]
    security_alerts: Optional[List]
    compliance_status: str
    
    # Final output and metadata
    final_output: str
    execution_summary: Optional[Dict]
    step: str
    error: Optional[str]
    warnings: Optional[List[str]]

class EnhancedOrchestrator:
    """Enhanced orchestrator with security and responsible AI integration"""
    
    def __init__(self):
        """Initialize enhanced orchestrator"""
        self.security_agent = get_security_agent()
        self.responsible_ai = get_responsible_ai_framework()
        self.execution_history = []
        self.setup_workflow_rules()
    
    def setup_workflow_rules(self):
        """Setup workflow execution rules and constraints"""
        self.workflow_rules = {
            "data_collection": {
                "requires_security_validation": True,
                "requires_ethics_check": False,
                "max_execution_time": 300,  # 5 minutes
                "retry_attempts": 2
            },
            "trend_analysis": {
                "requires_security_validation": True,
                "requires_ethics_check": True,
                "max_execution_time": 600,  # 10 minutes
                "retry_attempts": 1
            },
            "report_generation": {
                "requires_security_validation": False,
                "requires_ethics_check": True,
                "max_execution_time": 300,
                "retry_attempts": 2
            }
        }
    
    def classify_user_intent(self, user_query: str) -> Dict[str, Any]:
        """Enhanced user intent classification with security considerations"""
        query_lower = user_query.lower()
        
        # Security-sensitive keywords
        sensitive_keywords = [
            'admin', 'delete', 'drop', 'truncate', 'modify', 'alter',
            'password', 'credential', 'token', 'key', 'secret'
        ]
        
        # Data access patterns
        data_keywords = ['show', 'view', 'display', 'list', 'get', 'fetch', 'retrieve']
        analysis_keywords = ['analyze', 'trend', 'pattern', 'forecast', 'predict', 'model']
        report_keywords = ['report', 'summary', 'export', 'generate', 'document']
        
        # Add additional keywords for better intent classification
        data_keywords.extend(['find', 'locate', 'identify'])
        analysis_keywords.extend(['correlation', 'relationship', 'association'])
        
        classification = {
            "intent": "unknown",
            "priority": WorkflowPriority.MEDIUM.value,
            "security_level": "standard",
            "requires_human_review": False,
            "estimated_complexity": "medium"
        }
        
        # Check for security-sensitive operations
        if any(keyword in query_lower for keyword in sensitive_keywords):
            classification["security_level"] = "high"
            classification["requires_human_review"] = True
            classification["priority"] = WorkflowPriority.HIGH.value
        
        # Determine primary intent
        if any(keyword in query_lower for keyword in data_keywords):
            if any(keyword in query_lower for keyword in analysis_keywords):
                classification["intent"] = "collect_analyze"
                classification["estimated_complexity"] = "high"
            else:
                classification["intent"] = "data_view"
                classification["estimated_complexity"] = "low"
        elif any(keyword in query_lower for keyword in analysis_keywords):
            classification["intent"] = "analyze_trends"
            classification["estimated_complexity"] = "high"
        elif any(keyword in query_lower for keyword in report_keywords):
            classification["intent"] = "generate_report"
            classification["estimated_complexity"] = "medium"
        
        # Adjust priority based on urgency indicators
        urgency_keywords = ['urgent', 'critical', 'emergency', 'immediate', 'asap']
        if any(keyword in query_lower for keyword in urgency_keywords):
            classification["priority"] = WorkflowPriority.CRITICAL.value
        
        return classification
    
    def plan_agent_execution(self, intent_classification: Dict, user_query: str) -> List[str]:
        """Plan optimal agent execution sequence"""
        intent = intent_classification["intent"]
        
        execution_plans = {
            "data_view": ["collector"],
            "collect_analyze": ["collector", "trend_analysis", "security_validation"],
            "analyze_trends": ["collector", "trend_analysis", "responsible_ai_check"],
            "generate_report": ["collector", "trend_analysis", "report_generation", "responsible_ai_check"],
            "full_analysis": ["collector", "trend_analysis", "report_generation", "security_validation", "responsible_ai_check"]
        }
        
        base_plan = execution_plans.get(intent, ["collector", "trend_analysis"])
        
        # Add security validation for high-security operations
        if intent_classification["security_level"] == "high":
            if "security_validation" not in base_plan:
                base_plan.insert(-1, "security_validation")
        
        # Add responsible AI check for analysis operations
        if "analyze" in intent or "predict" in user_query.lower():
            if "responsible_ai_check" not in base_plan:
                base_plan.append("responsible_ai_check")
        
        return base_plan

def enhanced_start_node(state: EnhancedWorkflowState) -> EnhancedWorkflowState:
    """Enhanced workflow initialization with security and ethics setup"""
    state["step"] = "initializing"
    state["session_id"] = datetime.now().strftime("%Y%m%d_%H%M%S")
    state["warnings"] = []
    state["compliance_status"] = "pending"
    
    try:
        orchestrator = EnhancedOrchestrator()
        # If the user_input is a direct SQL query, force data_view intent and collector-only plan
        if state["user_input"].strip().startswith("query_postgresql_tool"):
            state["workflow_type"] = "data_view"
            state["priority"] = WorkflowPriority.MEDIUM.value
            state["agent_execution_plan"] = ["collector"]
            state["agent_results"] = {}
            logger.info("🔎 Direct SQL query detected: Forcing data_view workflow and collector-only execution plan.")
        else:
            # Classify user intent with security considerations
            intent_classification = orchestrator.classify_user_intent(state["user_input"])
            state["workflow_type"] = intent_classification["intent"]
            state["priority"] = intent_classification["priority"]
            # Plan agent execution
            execution_plan = orchestrator.plan_agent_execution(intent_classification, state["user_input"])
            state["agent_execution_plan"] = execution_plan
            state["agent_results"] = {}
            # Security pre-check for high-risk operations
            if intent_classification["security_level"] == "high":
                state["warnings"].append("High-security operation detected - enhanced monitoring enabled")
            if intent_classification["requires_human_review"]:
                state["warnings"].append("Operation requires human review - flagged for manual oversight")
            logger.info(f"🚀 Enhanced workflow initialized: {state['workflow_type']} (Priority: {state['priority']})")
            logger.info(f"📋 Execution plan: {execution_plan}")
    except Exception as e:
        state["error"] = f"Workflow initialization failed: {str(e)}"
        logger.error(f"❌ Initialization error: {e}")
    return state

def enhanced_collector_node(state: EnhancedWorkflowState) -> EnhancedWorkflowState:
    """Enhanced data collection with security validation"""
    state["step"] = "collecting_data"
    state["current_agent"] = "collector"
    
    try:
        start_time = datetime.now()
        logger.info(f"🔄 Starting Enhanced Collector Agent...")
        
        # Execute collector agent with error handling
        try:
            # Revert to original collector agent call
            collector_result = run_collector_agent(state["user_input"])
            if not collector_result:
                raise ValueError("Collector agent returned no data")
        except Exception as e:
            logger.error(f"Collector agent failed: {str(e)}")
            state["warnings"].append(f"Data collection failed: {str(e)}")
            collector_result = "No data collected due to error"
            
        # Calculate execution_time from start_time
        execution_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Execution time calculated: {execution_time:.2f}s")
        
        # Security validation of collected data
        security_input = {
            "data": collector_result,
            "source": "collector_agent",
            "user_id": state.get("user_context", {}).get("user_id", "unknown"),
            "action": "data_collection",
            "session_id": state["session_id"]
        }
        
        security_result = run_security_agent(security_input)
        security_data = json.loads(security_result)
        
        # Store results
        state["collector_result"] = collector_result
        state["security_assessment"] = security_data

        # Ethics assessment for data_view/direct SQL queries
        if state.get("workflow_type") == "data_view":
            try:
                # Use collector_result as both predictions and training_data for basic ethics check
                model_metadata = {
                    "name": "direct_sql_data_view",
                    "version": "1.0",
                    "algorithm": "none",
                    "session_id": state["session_id"]
                }
                ethics_result = run_responsible_ai_assessment(collector_result, collector_result, model_metadata)
                state["ethics_assessment"] = json.loads(ethics_result)
                logger.info("✅ Ethics assessment completed for data_view workflow.")
            except Exception as e:
                logger.warning(f"⚠️ Ethics assessment failed for data_view: {e}")
                state["ethics_assessment"] = {"ethics_level": "unknown", "error": str(e)}

        # Create agent result record
        state["agent_results"]["collector"] = AgentResult(
            agent_name="collector",
            status=AgentStatus.COMPLETED if not security_data.get("error") else AgentStatus.FAILED,
            execution_time=execution_time,
            output=collector_result,
            security_validated=security_data.get("security_status") != "HIGH_RISK",
            metadata={"security_assessment": security_data}
        )

        # Ensure execution_time is passed to the state
        state["execution_time"] = execution_time

        # Handle security violations
        if security_data.get("security_status") == "HIGH_RISK":
            state["warnings"].append("High-risk security status detected in data collection")
            state["compliance_status"] = "security_violation"
            # Stop workflow for critical security issues
            if security_data.get("risk_score", 0) > 0.8:
                state["error"] = "Workflow terminated due to critical security violation"
                return state

        logger.info(f"✅ Enhanced Collector completed: {execution_time:.2f}s")
        logger.info(f"🔒 Security Status: {security_data.get('security_status', 'Unknown')}")
        
    except Exception as e:
        state["error"] = f"Enhanced collector failed: {str(e)}"
        state["agent_results"]["collector"] = AgentResult(
            agent_name="collector",
            status=AgentStatus.FAILED,
            execution_time=0,
            output=None,
            error=str(e)
        )
        logger.error(f"❌ Enhanced Collector error: {e}")
    
    return state

def enhanced_trend_analysis_node(state: EnhancedWorkflowState) -> EnhancedWorkflowState:
    """Enhanced trend analysis with responsible AI monitoring"""
    state["step"] = "analyzing_trends"
    state["current_agent"] = "trend_analysis"
    
    try:
        start_time = datetime.now()
        logger.info(f"🔬 Starting Enhanced Trend Analysis...")
        
        # Extract date range from user input
        date_pattern = r'(\d{4}-\d{2}-\d{2})'
        dates = re.findall(date_pattern, state["user_input"])
        start_date = dates[0] if len(dates) > 0 else None
        end_date = dates[1] if len(dates) > 1 else None
        
        # Use data already collected by the collector node
        collector_result = state.get("collector_result")
        if not collector_result:
            logger.error("No collector result found in state")
            raise ValueError("Collector agent returned no data - collector must run first")

        # Convert collector result to DataFrame
        try:
            if isinstance(collector_result, str):
                collector_result = json.loads(collector_result)
            
            # Handle different data formats from collector
            if isinstance(collector_result, list):
                # Direct list of records
                collector_df = pd.DataFrame(collector_result)
            elif isinstance(collector_result, dict):
                # Check for the standard collector response structure
                if 'data' in collector_result:
                    # Nested data structure: {"data": {"rows": [...], "summary": ...}, ...}
                    data_obj = collector_result['data']
                    if isinstance(data_obj, dict) and 'rows' in data_obj:
                        collector_df = pd.DataFrame(data_obj['rows'])
                    elif isinstance(data_obj, list):
                        collector_df = pd.DataFrame(data_obj)
                    else:
                        collector_df = pd.DataFrame([data_obj])
                elif 'rows' in collector_result:
                    # Direct rows structure: {"rows": [...], ...}
                    collector_df = pd.DataFrame(collector_result['rows'])
                else:
                    # Single record or unknown structure
                    collector_df = pd.DataFrame([collector_result])
            else:
                raise ValueError(f"Unexpected collector result type: {type(collector_result)}")
                
        except Exception as e:
            logger.error(f"Failed to parse collector result: {e}")
            logger.error(f"Collector result preview: {str(collector_result)[:500]}")
            raise ValueError(f"Could not convert collector result to DataFrame: {str(e)}")

        # Validate collector data
        if collector_df.empty:
            logger.error("collector_df is empty after conversion")
            raise ValueError("Invalid collector data: DataFrame is empty")
            
        logger.info(f"📊 Collector data shape: {collector_df.shape}")
        logger.info(f"📋 Collector columns: {list(collector_df.columns)}")
        logger.info(f"🔍 First few rows:\n{collector_df.head(3)}")

        # Check if datetime column is required based on query type
        query_lower = state["user_input"].lower()
        is_correlation_query = any(word in query_lower for word in ['correlation', 'correlate', 'relationship', 'association'])
        
        # Ensure datetime column is properly formatted
        if 'datetime' in collector_df.columns:
            collector_df['datetime'] = pd.to_datetime(collector_df['datetime'], errors='coerce')
            collector_df.set_index('datetime', inplace=True)
            logger.info(f"✅ DateTime index set successfully")
        else:
            # Try to find alternative date columns
            date_cols = [col for col in collector_df.columns if 'date' in col.lower() or 'time' in col.lower()]
            if date_cols:
                logger.info(f"Found alternative date column: {date_cols[0]}")
                collector_df['datetime'] = pd.to_datetime(collector_df[date_cols[0]], errors='coerce')
                collector_df.set_index('datetime', inplace=True)
            elif is_correlation_query:
                logger.info(f"ℹ️ DateTime not required for correlation analysis. Available columns: {list(collector_df.columns)}")
            else:
                logger.warning(f"⚠️ No 'datetime' column found. Available columns: {list(collector_df.columns)}")
                logger.error("No datetime-like column found in collector data")

        # Pass the DataFrame to TrendAgent
        trend_agent = TrendAgent()
        trend_agent.df = collector_df
        logger.info(f"✅ TrendAgent initialized with {len(collector_df)} records")

        # Run the TrendAgent analysis
        trend_result = trend_agent.analyze_trends(start_date=start_date, end_date=end_date)
        state["trend_result"] = trend_result
        
        # Generate visualizations using smart visualization method
        try:
            logger.info(f"📊 Generating visualizations...")
            
            # Use TrendAgent's smart visualization method
            output_dir = f"visualizations/session_{state['session_id']}"
            visualization_paths = trend_agent.generate_smart_visualizations(
                user_query=state["user_input"],
                start_date=start_date,
                end_date=end_date,
                output_dir=output_dir
            )
            
            # Check if visualization was successful
            if "error" in visualization_paths:
                logger.warning(f"⚠️ Visualization error: {visualization_paths['error']}")
                state["warnings"].append(f"Visualization: {visualization_paths['error']}")
                state["visualization_paths"] = {}
            elif "warning" in visualization_paths:
                logger.info(f"ℹ️ Visualization warning: {visualization_paths['warning']}")
                state["visualization_paths"] = {}
            else:
                state["visualization_paths"] = visualization_paths
                logger.info(f"✅ Generated {len(visualization_paths)} visualizations")
                
                # Log the paths
                for viz_name, viz_path in visualization_paths.items():
                    logger.info(f"   📈 {viz_name}: {viz_path}")
                
        except Exception as e:
            logger.warning(f"⚠️ Visualization generation failed: {e}")
            logger.error(f"Error details: {str(e)}", exc_info=True)
            state["warnings"].append(f"Visualization generation failed: {str(e)}")
            state["visualization_paths"] = {}
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Responsible AI assessment
        if state.get("collector_result"):
            try:
                # Parse collector result for training data
                training_data = state["collector_result"]
                if isinstance(training_data, str):
                    training_data = json.loads(training_data) if training_data.startswith('{') else []
                
                # Parse trend result for predictions
                predictions = trend_result
                if isinstance(predictions, str):
                    predictions = json.loads(predictions) if predictions.startswith('{') else []
                
                model_metadata = {
                    "name": "weather_trend_model",
                    "version": "1.0",
                    "algorithm": "Time Series Analysis",
                    "session_id": state["session_id"]
                }
                
                ethics_result = run_responsible_ai_assessment(
                    predictions, training_data, model_metadata
                )
                state["ethics_assessment"] = json.loads(ethics_result)
                
            except Exception as e:
                logger.warning(f"⚠️ Responsible AI assessment failed: {e}")
                state["warnings"].append(f"Ethics assessment failed: {str(e)}")
        
        # Store results
        state["trend_result"] = trend_result
        
        # Determine ethics compliance
        ethics_compliant = True
        if state.get("ethics_assessment"):
            ethics_level = state["ethics_assessment"].get("ethics_level", "compliant")
            ethics_compliant = ethics_level not in ["major_concern", "critical_violation"]
        
        state["agent_results"]["trend_analysis"] = AgentResult(
            agent_name="trend_analysis",
            status=AgentStatus.COMPLETED,
            execution_time=execution_time,
            output=trend_result,
            ethics_validated=ethics_compliant,
            metadata={"ethics_assessment": state.get("ethics_assessment")}
        )
        
        # Handle ethics violations
        if not ethics_compliant:
            state["warnings"].append("Ethics compliance issues detected in trend analysis")
            if state["ethics_assessment"].get("ethics_level") == "critical_violation":
                state["compliance_status"] = "ethics_violation"
        
        logger.info(f"✅ Enhanced Trend Analysis completed: {execution_time:.2f}s")
        logger.info(f"🤖 Ethics Status: {'Compliant' if ethics_compliant else 'Issues Detected'}")
        
    except Exception as e:
        state["error"] = f"Enhanced trend analysis failed: {str(e)}"
        state["agent_results"]["trend_analysis"] = AgentResult(
            agent_name="trend_analysis",
            status=AgentStatus.FAILED,
            execution_time=0,
            output=None,
            error=str(e)
        )
        logger.error(f"❌ Enhanced Trend Analysis error: {e}")
    
    return state

def enhanced_report_generation_node(state: EnhancedWorkflowState) -> EnhancedWorkflowState:
    """Enhanced report generation with comprehensive oversight"""
    state["step"] = "generating_report"
    state["current_agent"] = "report_generation"
    
    try:
        start_time = datetime.now()
        logger.info(f"📋 Starting Enhanced Report Generation...")
        
        # Prepare comprehensive input for report generation
        trend_data = state.get("trend_result", "No trend analysis available")
        collector_data = state.get("collector_result", "No data collected")
        security_summary = state.get("security_assessment", {})
        ethics_summary = state.get("ethics_assessment", {})
        
        # Enhanced report input with security and ethics context
        report_input = {
            "user_query": state["user_input"],
            "trend_analysis": trend_data,
            "collector_data": collector_data,
            "security_summary": {
                "status": security_summary.get("security_status", "Unknown"),
                "risk_score": security_summary.get("risk_score", 0),
                "recommendations": security_summary.get("recommendations", [])
            },
            "ethics_summary": {
                "level": ethics_summary.get("ethics_level", "Unknown"),
                "transparency_score": ethics_summary.get("transparency_score", 0),
                "bias_count": ethics_summary.get("bias_count", 0),
                "recommendations": ethics_summary.get("recommendations", [])
            },
            "session_metadata": {
                "session_id": state["session_id"],
                "workflow_type": state["workflow_type"],
                "priority": state["priority"],
                "compliance_status": state["compliance_status"],
                "visualizations": state.get("visualization_paths", {})  # Add visualizations for report context
            }
        }
        
        # Generate enhanced report
        report_result = generate_summary_report(report_input)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        state["report_result"] = report_result
        
        state["agent_results"]["report_generation"] = AgentResult(
            agent_name="report_generation",
            status=AgentStatus.COMPLETED,
            execution_time=execution_time,
            output=report_result,
            metadata={"enhanced_features": True}
        )
        
        logger.info(f"✅ Enhanced Report Generation completed: {execution_time:.2f}s")
        
    except Exception as e:
        state["error"] = f"Enhanced report generation failed: {str(e)}"
        state["agent_results"]["report_generation"] = AgentResult(
            agent_name="report_generation",
            status=AgentStatus.FAILED,
            execution_time=0,
            output=None,
            error=str(e)
        )
        logger.error(f"❌ Enhanced Report Generation error: {e}")
    
    return state

def enhanced_output_compilation_node(state: EnhancedWorkflowState) -> EnhancedWorkflowState:
    """Enhanced output compilation with comprehensive summary"""
    state["step"] = "compiling_output"
    
    try:
        logger.info(f"📊 Starting Enhanced Output Compilation...")
        
        # Compile execution summary - handle None values gracefully
        agent_results = state.get("agent_results", {}) or {}
        
        total_execution_time = sum(
            result.execution_time for result in agent_results.values()
            if hasattr(result, 'execution_time')
        )
        
        successful_agents = [
            name for name, result in agent_results.items()
            if hasattr(result, 'status') and result.status == AgentStatus.COMPLETED
        ]
        
        failed_agents = [
            name for name, result in agent_results.items()
            if hasattr(result, 'status') and result.status == AgentStatus.FAILED
        ]
        
        # Determine final compliance status
        if state["compliance_status"] == "pending":
            if state.get("security_assessment", {}).get("security_status") == "ACCEPTABLE" and \
               state.get("ethics_assessment", {}).get("ethics_level") in ["compliant", "minor_concern"]:
                state["compliance_status"] = "compliant"
            else:
                state["compliance_status"] = "needs_review"
        
        # Create comprehensive execution summary
        state["execution_summary"] = {
            "session_id": state["session_id"],
            "workflow_type": state["workflow_type"],
            "priority": state["priority"],
            "total_execution_time": total_execution_time,
            "agents_executed": list(state["agent_results"].keys()),
            "successful_agents": successful_agents,
            "failed_agents": failed_agents,
            "security_status": state.get("security_assessment", {}).get("security_status", "Unknown"),
            "ethics_status": state.get("ethics_assessment", {}).get("ethics_level", "Unknown"),
            "compliance_status": state["compliance_status"],
            "warnings": state.get("warnings", []),
            "timestamp": datetime.now().isoformat()
        }
        
        # Generate final output based on workflow type
        if state["workflow_type"] == "data_view":
            collector_result = state.get('collector_result', 'No data collected')
            
            # Create a structured output with complete data (consistent with other workflows)
            import json
            state["final_output"] = json.dumps({
                "session_id": state['session_id'],
                "workflow_type": state["workflow_type"],
                "security_status": state.get('security_assessment', {}).get('security_status', 'Unknown'),
                "collector_data": collector_result,  # FULL DATA
                "execution_time": total_execution_time,
                "successful_agents": successful_agents
            })
        
        elif state["workflow_type"] in ["collect_analyze", "analyze_trends"]:
            # Include FULL collector result (not just preview) for frontend to parse
            collector_result = state.get('collector_result', 'No data collected')
            
            # Get FULL trend result (don't truncate)
            trend_result = state.get('trend_result', 'No trend analysis')
            
            # Format visualizations
            viz_paths = state.get('visualization_paths', {})
            viz_section = ""
            if viz_paths:
                viz_section = "\n**📊 Visualizations Generated:**\n"
                for viz_name, viz_path in viz_paths.items():
                    viz_section += f"   📈 {viz_name}: {viz_path}\n"
            
            # Create a structured output with complete data
            import json
            state["final_output"] = json.dumps({
                "session_id": state['session_id'],
                "workflow_type": state["workflow_type"],
                "security_status": state.get('security_assessment', {}).get('security_status', 'Unknown'),
                "ethics_status": state.get('ethics_assessment', {}).get('ethics_level', 'Unknown'),
                "collector_data": collector_result,  # FULL DATA
                "trend_analysis": trend_result,  # FULL TREND DATA (not truncated)
                "visualizations": viz_paths,
                "compliance_status": state['compliance_status'],
                "execution_time": total_execution_time,
                "successful_agents": successful_agents
            })
        
        elif state["workflow_type"] == "generate_report":
            # Include FULL data for report generation workflow
            collector_result = state.get('collector_result', 'No data collected')
            trend_result = state.get('trend_result', 'No trend analysis')
            report_result = state.get('report_result', 'No report generated')
            viz_paths = state.get('visualization_paths', {})
            
            # Create a structured output with complete data
            import json
            state["final_output"] = json.dumps({
                "session_id": state['session_id'],
                "workflow_type": state["workflow_type"],
                "generated_at": datetime.now().isoformat(),
                "security_status": state.get('security_assessment', {}).get('security_status', 'Unknown'),
                "ethics_status": state.get('ethics_assessment', {}).get('ethics_level', 'Unknown'),
                "collector_data": collector_result,  # FULL DATA
                "trend_analysis": trend_result,
                "report_content": report_result,
                "visualizations": viz_paths,
                "compliance_status": state['compliance_status'],
                "execution_time": total_execution_time,
                "successful_agents": successful_agents,
                "warnings": state.get('warnings', [])
            })
        
        else:
            # Fallback comprehensive output
            state["final_output"] = f"""
🤖 **Multi-Agent Analysis Complete**
Session: {state['session_id']}

**Results Summary:**
- Data Collection: {'✅' if 'collector' in successful_agents else '❌'}
- Trend Analysis: {'✅' if 'trend_analysis' in successful_agents else '❌'}
- Report Generation: {'✅' if 'report_generation' in successful_agents else '❌'}

**Compliance Status:** {state['compliance_status']}
**Security Status:** {state.get('security_assessment', {}).get('security_status', 'Unknown')}
**Ethics Status:** {state.get('ethics_assessment', {}).get('ethics_level', 'Unknown')}

**Warnings:** {len(state.get('warnings', []))} issues detected
{chr(10).join(f"⚠️ {warning}" for warning in state.get('warnings', [])[:3])}

---
Enhanced execution completed in {total_execution_time:.2f}s
"""
        
        logger.info(f"✅ Enhanced Output Compilation completed")
        logger.info(f"🎯 Final compliance status: {state['compliance_status']}")
        
    except Exception as e:
        state["error"] = f"Enhanced output compilation failed: {str(e)}"
        logger.error(f"❌ Enhanced Output Compilation error: {e}")
    
    return state

def enhanced_end_node(state: EnhancedWorkflowState) -> EnhancedWorkflowState:
    """Enhanced workflow finalization with audit logging"""
    state["step"] = "completed"
    
    try:
        # Log workflow completion for audit trail
        audit_entry = {
            "session_id": state["session_id"],
            "user_input": state["user_input"],
            "workflow_type": state["workflow_type"],
            "execution_summary": state.get("execution_summary", {}),
            "compliance_status": state["compliance_status"],
            "completion_time": datetime.now().isoformat()
        }
        
        logger.info(f"🏁 Enhanced workflow completed: {state['session_id']}")
        logger.info(f"📋 Audit entry created for compliance tracking")
        
        # Store audit entry (implement database storage as needed)
        # self.store_audit_entry(audit_entry)
        
    except Exception as e:
        logger.error(f"❌ Enhanced workflow finalization error: {e}")
    
    return state

# Enhanced routing functions
def should_run_trend_analysis(state: EnhancedWorkflowState) -> str:
    """Enhanced routing decision for trend analysis"""
    workflow_type = state.get("workflow_type", "data_view")
    security_status = state.get("security_assessment", {}).get("security_status", "ACCEPTABLE")
    
    # Skip trend analysis if security violation
    if security_status == "HIGH_RISK":
        logger.warning("⚠️ Skipping trend analysis due to security concerns")
        return "enhanced_output_compilation"
    
    if workflow_type in ["collect_analyze", "analyze_trends", "generate_report"]:
        return "enhanced_trend_analysis"
    else:
        return "enhanced_output_compilation"

def should_run_report_generation(state: EnhancedWorkflowState) -> str:
    """Enhanced routing decision for report generation"""
    workflow_type = state.get("workflow_type", "")
    ethics_status = state.get("ethics_assessment", {}).get("ethics_level", "compliant")
    
    # Skip report generation if critical ethics violation
    if ethics_status == "critical_violation":
        logger.warning("⚠️ Skipping report generation due to ethics concerns")
        return "enhanced_output_compilation"
    
    if workflow_type == "generate_report":
        return "enhanced_report_generation"
    else:
        return "enhanced_output_compilation"

# Lazy initialization to prevent duplicate node errors
def _create_enhanced_workflow():
    """Create and return the compiled enhanced orchestrator workflow"""
    enhanced_workflow = StateGraph(EnhancedWorkflowState)
    
    # Add enhanced nodes
    enhanced_workflow.add_node("enhanced_start", enhanced_start_node)
    enhanced_workflow.add_node("enhanced_collector", enhanced_collector_node)
    enhanced_workflow.add_node("enhanced_trend_analysis", enhanced_trend_analysis_node)
    enhanced_workflow.add_node("enhanced_report_generation", enhanced_report_generation_node)
    enhanced_workflow.add_node("enhanced_output_compilation", enhanced_output_compilation_node)
    enhanced_workflow.add_node("enhanced_end", enhanced_end_node)
    
    # Add enhanced edges with conditional routing
    enhanced_workflow.add_edge(START, "enhanced_start")
    enhanced_workflow.add_edge("enhanced_start", "enhanced_collector")
    enhanced_workflow.add_conditional_edges(
        "enhanced_collector",
        should_run_trend_analysis,
        {
            "enhanced_trend_analysis": "enhanced_trend_analysis",
            "enhanced_output_compilation": "enhanced_output_compilation"
        }
    )
    enhanced_workflow.add_conditional_edges(
        "enhanced_trend_analysis",
        should_run_report_generation,
        {
            "enhanced_report_generation": "enhanced_report_generation",
            "enhanced_output_compilation": "enhanced_output_compilation"
        }
    )
    enhanced_workflow.add_edge("enhanced_report_generation", "enhanced_output_compilation")
    enhanced_workflow.add_edge("enhanced_output_compilation", "enhanced_end")
    enhanced_workflow.add_edge("enhanced_end", END)
    
    return enhanced_workflow.compile()

_enhanced_app_instance = None

def _get_enhanced_app():
    """Get or create the enhanced orchestrator workflow"""
    global _enhanced_app_instance
    if _enhanced_app_instance is None:
        _enhanced_app_instance = _create_enhanced_workflow()
    return _enhanced_app_instance

def run_enhanced_orchestrator_workflow(user_input: str, user_context: Dict = None) -> Dict:
    """
    Run enhanced orchestrator workflow with security and responsible AI integration
    
    Args:
        user_input: User's natural language query
        user_context: Additional user context (user_id, permissions, etc.)
        
    Returns:
        Dict: Comprehensive workflow results with security and ethics assessments
    """
    initial_state = EnhancedWorkflowState(
        user_input=user_input,
        workflow_type="",
        priority="medium",
        session_id="",
        user_context=user_context or {},
        agent_execution_plan=None,
        agent_results=None,
        current_agent=None,
        collector_result=None,
        trend_result=None,
        report_result=None,
        visualization_paths=None,
        security_assessment=None,
        ethics_assessment=None,
        security_alerts=None,
        compliance_status="pending",
        final_output="",
        execution_summary=None,
        step="",
        error=None,
        warnings=None
    )
    
    try:
        enhanced_app = _get_enhanced_app()
        result = enhanced_app.invoke(initial_state)
        return result
    except Exception as e:
        error_time = datetime.now()
        error_id = error_time.strftime("%Y%m%d_%H%M%S")
        error_details = {
            'error_type': type(e).__name__,
            'error_message': str(e),
            'traceback': traceback.format_exc(),
            'step': initial_state.get('step', 'unknown'),
            'current_agent': initial_state.get('current_agent', 'none'),
            'user_input': user_input
        }
        
        # Log detailed error information
        logger.error(f"Orchestrator error {error_id}: {error_details['error_type']} - {error_details['error_message']}")
        logger.debug(f"Detailed error information for {error_id}:\n{error_details['traceback']}")
        
        # Create user-friendly error message
        user_message = "An error occurred while processing your request. "
        if initial_state.get('current_agent'):
            user_message += f"The error happened during the {initial_state['current_agent']} phase. "
        if hasattr(e, 'detail'):  # FastAPI HTTPException
            user_message += str(e.detail)
        elif "No module named" in str(e):
            user_message += "A required component is missing. Please contact support."
        elif "connection" in str(e).lower():
            user_message += "There was a problem connecting to the data source. Please try again later."
        else:
            user_message += "Please try again or contact support if the problem persists."
        
        return {
            "user_input": user_input,
            "error": user_message,
            "error_details": error_details,  # Detailed error info for debugging
            "error_id": error_id,  # Unique identifier for the error
            "final_output": f"❌ Workflow execution failed (Error ID: {error_id})\n{user_message}",
            "step": initial_state.get('step', 'error'),
            "compliance_status": "system_error",
            "session_id": error_time.strftime("%Y%m%d_%H%M%S")
        }

# Module level function for classification
def classify_user_intent(query: str) -> str:
    """
    Module-level function to classify user intent

    """
    orchestrator = EnhancedOrchestrator()
    classification = orchestrator.classify_user_intent(query)
    return classification["intent"]

# Test function
if __name__ == "__main__":
    print("🚀 Testing Enhanced Multi-Agent Orchestrator...")
    
    test_queries = [
        "Show me weather data for Colombo last 7 days",
        "Analyze temperature trends and generate comprehensive report",
        "Get current weather patterns and forecast risks"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*50}")
        print(f"🧪 Test {i}: {query}")
        print(f"{'='*50}")
        
        result = run_enhanced_orchestrator_workflow(
            query,
            {"user_id": f"test_user_{i}", "role": "analyst"}
        )
        
        print(f"📊 Session: {result.get('session_id')}")
        print(f"🔒 Security: {result.get('security_assessment', {}).get('security_status', 'Unknown')}")
        print(f"🤖 Ethics: {result.get('ethics_assessment', {}).get('ethics_level', 'Unknown')}")
        print(f"✅ Status: {result.get('compliance_status')}")
        print(f"📋 Output: {result.get('final_output', 'No output')[:200]}...")
        
        if result.get('warnings'):
            print(f"⚠️ Warnings: {len(result['warnings'])}")
    
    print("\n✅ Enhanced orchestrator testing complete!")