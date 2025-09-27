"""
Orchestrator API Endpoints

This module provides REST API endpoints for the orchestrator workflow system,
enabling users to submit queries that are routed through the appropriate 
agent workflows (data view, collect & analyze, or full summary).

Author: Saabir
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
import logging
import json
import asyncio
from datetime import datetime

# Import orchestrator and agents
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents'))
from orchestrator import run_orchestrator_workflow, get_workflow_summary, classify_user_intent

from security.auth_middleware import get_current_user, get_optional_user
from models.user import UserDB
from db_config import DatabaseConfig

# Configure logging
logger = logging.getLogger(__name__)

# Create router
orchestrator_router = APIRouter(prefix="/orchestrator", tags=["Orchestrator"])

# Database configuration  
db_config = DatabaseConfig()

def get_db() -> Session:
    """Get database session"""
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()

# -------------------------
# Pydantic Models
# -------------------------
class WorkflowRequest(BaseModel):
    """Request model for orchestrator workflow"""
    query: str = Field(..., min_length=1, max_length=1000, description="Natural language query for data analysis")
    async_execution: bool = Field(default=False, description="Execute workflow asynchronously")
    include_visualizations: bool = Field(default=False, description="Include data visualizations in response")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "Analyze temperature trends for the past month in Colombo",
                "async_execution": False,
                "include_visualizations": True
            }
        }

class WorkflowResponse(BaseModel):
    """Response model for orchestrator workflow"""
    request_id: str
    workflow_type: str
    query: str
    status: str
    execution_time_ms: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str
    user_id: Optional[int] = None
    
    class Config:
        schema_extra = {
            "example": {
                "request_id": "req_12345",
                "workflow_type": "collect_analyze",
                "query": "Analyze temperature trends", 
                "status": "completed",
                "execution_time_ms": 2500,
                "result": {"workflow_output": "..."},
                "error": None,
                "timestamp": "2025-09-27T10:30:00Z",
                "user_id": 123
            }
        }

class WorkflowPreview(BaseModel):
    """Preview of what workflow will be executed"""
    query: str
    workflow_type: str
    description: str
    estimated_agents: List[str]
    estimated_duration: str
    
# -------------------------
# Storage for async workflows
# -------------------------
workflow_results = {}  # In production, use Redis or database

# -------------------------
# API Endpoints
# -------------------------
@orchestrator_router.post("/preview", response_model=WorkflowPreview)
async def preview_workflow(
    request: WorkflowRequest,
    current_user: UserDB = Depends(get_optional_user)
):
    """
    Preview what workflow will be executed for a given query without actually running it.
    
    Args:
        request: Workflow request containing the query
        current_user: Optional authenticated user
        
    Returns:
        WorkflowPreview: Description of the workflow that will be executed
    """
    try:
        workflow_type = classify_user_intent(request.query)
        
        # Map workflow types to agents and duration estimates
        workflow_mapping = {
            "data_view": {
                "description": "View available data using Collector Agent",
                "agents": ["Collector Agent"],
                "duration": "5-15 seconds"
            },
            "collect_analyze": {
                "description": "Collect data and perform trend analysis",
                "agents": ["Collector Agent", "Trend Analysis Agent"],
                "duration": "30-60 seconds"
            },
            "full_summary": {
                "description": "Complete workflow with comprehensive reporting",
                "agents": ["Collector Agent", "Trend Analysis Agent", "Report Generation Agent"], 
                "duration": "60-120 seconds"
            }
        }
        
        workflow_info = workflow_mapping.get(workflow_type, workflow_mapping["data_view"])
        
        return WorkflowPreview(
            query=request.query,
            workflow_type=workflow_type,
            description=workflow_info["description"],
            estimated_agents=workflow_info["agents"],
            estimated_duration=workflow_info["duration"]
        )
        
    except Exception as e:
        logger.error(f"Workflow preview failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to preview workflow"
        )

@orchestrator_router.post("/execute", response_model=WorkflowResponse)
async def execute_workflow(
    request: WorkflowRequest,
    background_tasks: BackgroundTasks,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Execute orchestrator workflow for the given query.
    
    Args:
        request: Workflow request containing query and options
        background_tasks: FastAPI background tasks
        current_user: Authenticated user
        db: Database session
        
    Returns:
        WorkflowResponse: Workflow execution results
    """
    import time
    import uuid
    
    request_id = f"req_{uuid.uuid4().hex[:8]}"
    start_time = time.time()
    
    try:
        # Log the request
        logger.info(f"Executing workflow for user {current_user.username}: {request.query}")
        
        if request.async_execution:
            # Execute asynchronously
            background_tasks.add_task(
                _execute_workflow_async,
                request_id,
                request.query,
                current_user.id
            )
            
            return WorkflowResponse(
                request_id=request_id,
                workflow_type=classify_user_intent(request.query),
                query=request.query,
                status="processing",
                execution_time_ms=None,
                result=None,
                error=None,
                timestamp=datetime.utcnow().isoformat(),
                user_id=current_user.id
            )
        else:
            # Execute synchronously
            workflow_result = run_orchestrator_workflow(request.query)
            execution_time = int((time.time() - start_time) * 1000)
            
            # Check for errors
            if workflow_result.get("error"):
                return WorkflowResponse(
                    request_id=request_id,
                    workflow_type=workflow_result.get("workflow_type", "unknown"),
                    query=request.query,
                    status="failed",
                    execution_time_ms=execution_time,
                    result=None,
                    error=workflow_result["error"],
                    timestamp=datetime.utcnow().isoformat(),
                    user_id=current_user.id
                )
            
            # Parse the final output
            try:
                result_data = json.loads(workflow_result.get("final_output", "{}"))
            except json.JSONDecodeError:
                result_data = {"raw_output": workflow_result.get("final_output", "")}
            
            return WorkflowResponse(
                request_id=request_id,
                workflow_type=workflow_result.get("workflow_type", "unknown"),
                query=request.query,
                status="completed",
                execution_time_ms=execution_time,
                result=result_data,
                error=None,
                timestamp=datetime.utcnow().isoformat(),
                user_id=current_user.id
            )
            
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        logger.error(f"Workflow execution failed: {e}")
        
        return WorkflowResponse(
            request_id=request_id,
            workflow_type="error",
            query=request.query,
            status="failed",
            execution_time_ms=execution_time,
            result=None,
            error=f"Workflow execution failed: {str(e)}",
            timestamp=datetime.utcnow().isoformat(),
            user_id=current_user.id
        )

@orchestrator_router.get("/status/{request_id}", response_model=WorkflowResponse)
async def get_workflow_status(
    request_id: str,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get the status of an asynchronously executed workflow.
    
    Args:
        request_id: Unique identifier for the workflow request
        current_user: Authenticated user
        
    Returns:
        WorkflowResponse: Current status and results of the workflow
    """
    try:
        if request_id not in workflow_results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow request not found"
            )
        
        result = workflow_results[request_id]
        
        # Check if user has permission to view this result
        if result.get("user_id") != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this workflow result"
            )
        
        return WorkflowResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve workflow status"
        )

@orchestrator_router.get("/workflows", response_model=List[str])
async def list_available_workflows():
    """
    List all available workflow types and their descriptions.
    
    Returns:
        List[str]: Available workflow types with descriptions
    """
    return [
        "data_view: View and retrieve available data from the database",
        "collect_analyze: Collect data and perform trend analysis with visualizations", 
        "full_summary: Complete workflow with data collection, analysis, and comprehensive reporting"
    ]

@orchestrator_router.delete("/results/{request_id}")
async def delete_workflow_result(
    request_id: str,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Delete a workflow result (for async executions).
    
    Args:
        request_id: Unique identifier for the workflow request
        current_user: Authenticated user
        
    Returns:
        Dict: Deletion confirmation
    """
    try:
        if request_id not in workflow_results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow request not found"
            )
        
        result = workflow_results[request_id]
        
        # Check permissions
        if result.get("user_id") != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to delete this workflow result"
            )
        
        del workflow_results[request_id]
        
        return {"message": f"Workflow result {request_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete workflow result: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete workflow result"
        )

# -------------------------
# Background Task Functions
# -------------------------
async def _execute_workflow_async(request_id: str, query: str, user_id: int):
    """Execute workflow in background task"""
    import time
    
    start_time = time.time()
    
    try:
        workflow_result = run_orchestrator_workflow(query)
        execution_time = int((time.time() - start_time) * 1000)
        
        # Parse results
        if workflow_result.get("error"):
            result = {
                "request_id": request_id,
                "workflow_type": workflow_result.get("workflow_type", "unknown"),
                "query": query,
                "status": "failed",
                "execution_time_ms": execution_time,
                "result": None,
                "error": workflow_result["error"],
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id
            }
        else:
            try:
                result_data = json.loads(workflow_result.get("final_output", "{}"))
            except json.JSONDecodeError:
                result_data = {"raw_output": workflow_result.get("final_output", "")}
            
            result = {
                "request_id": request_id,
                "workflow_type": workflow_result.get("workflow_type", "unknown"),
                "query": query,
                "status": "completed",
                "execution_time_ms": execution_time,
                "result": result_data,
                "error": None,
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id
            }
        
        # Store result (in production, use Redis or database)
        workflow_results[request_id] = result
        
        logger.info(f"Async workflow {request_id} completed in {execution_time}ms")
        
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        
        result = {
            "request_id": request_id,
            "workflow_type": "error",
            "query": query,
            "status": "failed",
            "execution_time_ms": execution_time,
            "result": None,
            "error": f"Async workflow execution failed: {str(e)}",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id
        }
        
        workflow_results[request_id] = result
        logger.error(f"Async workflow {request_id} failed: {e}")