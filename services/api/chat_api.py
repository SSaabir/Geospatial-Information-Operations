"""
Chat API with Groq integration for weather analytics conversations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from security.auth_middleware import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])

# Initialize Groq LLM
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    print("⚠️ GROQ_API_KEY not found in environment. Chat functionality will be limited.")
    llm = None
else:
    llm = ChatGroq(
        groq_api_key=groq_api_key,
        model_name="meta-llama/llama-4-scout-17b-16e-instruct",  # Fast, high-quality model
        temperature=0.7,
        max_tokens=1024
    )

# System prompt for weather analytics assistant
SYSTEM_PROMPT = """You are a helpful weather analytics assistant specializing in climate data analysis, 
weather predictions, and geospatial information operations. You help users understand weather patterns, 
analyze climate trends, and make data-driven decisions based on atmospheric conditions.

Key capabilities:
- Weather prediction and forecasting
- Climate trend analysis
- Data visualization explanations
- Risk assessment for weather events
- Historical weather data interpretation
- Geospatial weather analytics

Keep responses concise, informative, and focused on weather/climate topics. If asked about unrelated topics,
politely redirect to weather analytics capabilities."""


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    response: str
    timestamp: datetime


@router.post("/send", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Send a chat message and get AI-powered response using Groq
    
    Requires: Professional tier or higher
    """
    try:
        # Check if Groq is available
        if not llm:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Chat service is currently unavailable. Please check GROQ_API_KEY configuration."
            )
        
        # Check tier access (Professional tier required)
        user_tier = getattr(current_user, 'tier', 'free')
        if user_tier not in ["professional"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chat feature requires Professional tier subscription."
            )
        
        # Check quota and send notifications
        from db_config import DatabaseConfig
        from models.usage import UsageMetrics
        from utils.tier import check_and_notify_usage, enforce_quota_or_raise
        from middleware.event_logger import increment_usage_metrics
        
        db_config = DatabaseConfig()
        db = db_config.get_session()
        
        try:
            # Get or create usage metrics
            metrics = db.query(UsageMetrics).filter(UsageMetrics.user_id == current_user.id).first()
            if not metrics:
                metrics = UsageMetrics(user_id=current_user.id)
                db.add(metrics)
            
            # Check usage thresholds and notify
            check_and_notify_usage(metrics, user_tier, current_user.id, getattr(current_user, 'username', 'User'))
            
            # Enforce quota (will raise if exceeded)
            enforce_quota_or_raise(metrics, user_tier, current_user.id, getattr(current_user, 'username', 'User'))
            
            # Increment usage
            metrics.api_calls = (metrics.api_calls or 0) + 1
            db.commit()
            
            # Log usage
            increment_usage_metrics(current_user.id, api_calls=1)
        finally:
            db.close()
        
        # Build message history
        messages = [SystemMessage(content=SYSTEM_PROMPT)]
        
        # Add conversation history
        for msg in request.conversation_history[-10:]:  # Last 10 messages for context
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))
        
        # Add current user message
        messages.append(HumanMessage(content=request.message))
        
        # Get response from Groq
        response = llm.invoke(messages)
        
        return ChatResponse(
            response=response.content,
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Chat error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate chat response: {str(e)}"
        )


@router.get("/health")
async def chat_health_check():
    """Check if chat service is available"""
    return {
        "groq_available": llm is not None,
        "model": "mixtral-8x7b-32768" if llm else None,
        "status": "operational" if llm else "unavailable"
    }
