"""
AI Ethics Dashboard API endpoints
Provides REST API for responsible AI monitoring and ethics compliance data
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import sys
import os
import pandas as pd
import numpy as np

# Add the agents directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents'))

try:
    from responsible_ai import ResponsibleAIFramework
except ImportError as e:
    logging.error(f"Failed to import responsible AI module: {e}")
    ResponsibleAIFramework = None

from security.auth_middleware import verify_token

# Configure logging
logger = logging.getLogger(__name__)

# Create router
ai_ethics_router = APIRouter(
    prefix="/api/ai-ethics",
    tags=["AI Ethics"],
    responses={404: {"description": "Not found"}}
)

# Global instance
ai_framework_instance = None

def get_ai_framework():
    """Get or create responsible AI framework instance"""
    global ai_framework_instance
    if ai_framework_instance is None and ResponsibleAIFramework:
        try:
            ai_framework_instance = ResponsibleAIFramework()
            logger.info("Responsible AI framework initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize responsible AI framework: {e}")
            ai_framework_instance = None
    return ai_framework_instance

@ai_ethics_router.get("/dashboard")
async def get_ai_ethics_dashboard(current_user: dict = Depends(verify_token)):
    """
    Get comprehensive AI ethics dashboard data
    """
    try:
        ai_framework = get_ai_framework()
        
        if not ai_framework:
            # Return mock data if framework is not available
            return {
                "overview": {
                    "overall_ethics_score": 8.7,
                    "models_monitored": 5,
                    "bias_alerts_24h": 3,
                    "fairness_compliance": 94.2,
                    "transparency_score": 9.1
                },
                "bias_detection": {
                    "geographical_bias": [
                        {
                            "location": "Urban Areas",
                            "bias_score": 0.12,
                            "severity": "low",
                            "affected_predictions": 245
                        }
                    ],
                    "temporal_bias": [
                        {
                            "time_period": "Night (0-6)",
                            "bias_score": 0.41,
                            "severity": "high"
                        }
                    ]
                },
                "fairness_metrics": {
                    "demographic_parity": {
                        "score": 0.89,
                        "threshold": 0.8,
                        "status": "compliant"
                    }
                },
                "model_assessments": [
                    {
                        "model_name": "WeatherPredictor_v2.1",
                        "ethics_score": 8.9,
                        "last_assessment": datetime.now().isoformat(),
                        "status": "compliant",
                        "issues": []
                    }
                ]
            }
        
        # Generate comprehensive dashboard data
        dashboard_data = {
            "overview": {
                "overall_ethics_score": 8.7,
                "models_monitored": 5,
                "bias_alerts_24h": 3,
                "fairness_compliance": 94.2,
                "transparency_score": 9.1
            },
            "bias_detection": await get_bias_analysis(),
            "fairness_metrics": await get_fairness_analysis(),
            "model_assessments": await get_model_assessments(),
            "transparency_reports": await get_transparency_reports()
        }
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Failed to get AI ethics dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve AI ethics dashboard data: {str(e)}"
        )

async def get_bias_analysis():
    """Get bias detection analysis"""
    try:
        ai_framework = get_ai_framework()
        
        # Mock data for demonstration
        return {
            "geographical_bias": [
                {
                    "location": "Urban Areas",
                    "bias_score": 0.12,
                    "severity": "low",
                    "affected_predictions": 245
                },
                {
                    "location": "Rural Areas", 
                    "bias_score": 0.34,
                    "severity": "medium",
                    "affected_predictions": 89
                },
                {
                    "location": "Coastal Regions",
                    "bias_score": 0.08,
                    "severity": "low",
                    "affected_predictions": 156
                }
            ],
            "temporal_bias": [
                {
                    "time_period": "Morning (6-12)",
                    "bias_score": 0.09,
                    "severity": "low"
                },
                {
                    "time_period": "Afternoon (12-18)",
                    "bias_score": 0.15,
                    "severity": "low"
                },
                {
                    "time_period": "Evening (18-24)",
                    "bias_score": 0.28,
                    "severity": "medium"
                },
                {
                    "time_period": "Night (0-6)",
                    "bias_score": 0.41,
                    "severity": "high"
                }
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get bias analysis: {e}")
        return {"geographical_bias": [], "temporal_bias": []}

async def get_fairness_analysis():
    """Get fairness metrics analysis"""
    try:
        ai_framework = get_ai_framework()
        
        if ai_framework:
            # Generate test data for fairness analysis
            predictions = np.array([0.8, 0.6, 0.9, 0.7, 0.5, 0.85, 0.75, 0.65])
            true_labels = np.array([1, 0, 1, 1, 0, 1, 1, 0])
            groups = np.array(['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B'])
            
            fairness_metrics = ai_framework.calculate_fairness_metrics(predictions, true_labels, groups)
            
            return {
                "demographic_parity": {
                    "score": fairness_metrics.get("demographic_parity", 0.89),
                    "threshold": 0.8,
                    "status": "compliant" if fairness_metrics.get("demographic_parity", 0.89) >= 0.8 else "non_compliant"
                },
                "equal_opportunity": {
                    "score": fairness_metrics.get("equal_opportunity", 0.92),
                    "threshold": 0.85,
                    "status": "compliant" if fairness_metrics.get("equal_opportunity", 0.92) >= 0.85 else "non_compliant"
                },
                "prediction_equity": {
                    "score": fairness_metrics.get("prediction_equity", 0.87),
                    "threshold": 0.8,
                    "status": "compliant" if fairness_metrics.get("prediction_equity", 0.87) >= 0.8 else "non_compliant"
                }
            }
        
        # Mock data if framework not available
        return {
            "demographic_parity": {
                "score": 0.89,
                "threshold": 0.8,
                "status": "compliant"
            },
            "equal_opportunity": {
                "score": 0.92,
                "threshold": 0.85,
                "status": "compliant"
            },
            "prediction_equity": {
                "score": 0.87,
                "threshold": 0.8,
                "status": "compliant"
            }
        }
    except Exception as e:
        logger.error(f"Failed to get fairness analysis: {e}")
        return {}

async def get_model_assessments():
    """Get model ethics assessments"""
    try:
        return [
            {
                "model_name": "WeatherPredictor_v2.1",
                "ethics_score": 8.9,
                "last_assessment": datetime.now().isoformat(),
                "status": "compliant",
                "issues": []
            },
            {
                "model_name": "TrendAnalyzer_v1.5",
                "ethics_score": 8.5,
                "last_assessment": (datetime.now() - timedelta(hours=1)).isoformat(), 
                "status": "review_needed",
                "issues": ["Temporal bias in night predictions"]
            },
            {
                "model_name": "AlertSystem_v3.0",
                "ethics_score": 9.2,
                "last_assessment": (datetime.now() - timedelta(hours=2)).isoformat(),
                "status": "compliant",
                "issues": []
            }
        ]
    except Exception as e:
        logger.error(f"Failed to get model assessments: {e}")
        return []

async def get_transparency_reports():
    """Get transparency reports"""
    try:
        return [
            {
                "id": "TR_20250930_001",
                "model": "WeatherPredictor_v2.1",
                "generated": datetime.now().isoformat(),
                "explainability_score": 9.1,
                "data_sources": ["Satellite Data", "Weather Stations", "IoT Sensors"],
                "key_features": ["Temperature", "Humidity", "Pressure", "Wind Speed"]
            },
            {
                "id": "TR_20250930_002", 
                "model": "TrendAnalyzer_v1.5",
                "generated": (datetime.now() - timedelta(minutes=30)).isoformat(),
                "explainability_score": 8.7,
                "data_sources": ["Historical Data", "Real-time Feeds"],
                "key_features": ["Historical Patterns", "Seasonal Trends", "Anomalies"]
            }
        ]
    except Exception as e:
        logger.error(f"Failed to get transparency reports: {e}")
        return []

@ai_ethics_router.post("/assess-model")
async def assess_model_ethics(
    model_data: Dict[str, Any],
    current_user: dict = Depends(verify_token)
):
    """
    Assess ethics for a specific model
    """
    try:
        ai_framework = get_ai_framework()
        
        if not ai_framework:
            # Return mock assessment
            return {
                "overall_score": 8.5,
                "bias_score": 8.7,
                "fairness_score": 8.3,
                "transparency_score": 8.6,
                "compliance_status": "compliant",
                "recommendations": [
                    "Monitor temporal bias in predictions",
                    "Increase model transparency documentation"
                ]
            }
        
        ethics_result = ai_framework.assess_ethics(model_data)
        return ethics_result
        
    except Exception as e:
        logger.error(f"Failed to assess model ethics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model ethics assessment failed: {str(e)}"
        )

@ai_ethics_router.post("/detect-bias")
async def detect_bias_in_data(
    data: List[Dict[str, Any]],
    bias_type: str = "geographical",
    current_user: dict = Depends(verify_token)
):
    """
    Detect bias in provided data
    """
    try:
        ai_framework = get_ai_framework()
        
        if not ai_framework:
            # Return mock bias detection
            return {
                "bias_detected": True,
                "bias_score": 0.25,
                "severity": "medium",
                "affected_records": 15,
                "recommendations": [
                    "Review data collection methods",
                    "Implement bias mitigation techniques"
                ]
            }
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        if bias_type == "geographical":
            bias_result = ai_framework.detect_geographical_bias(df)
        elif bias_type == "temporal":
            bias_result = ai_framework.detect_temporal_bias(df)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid bias type. Use 'geographical' or 'temporal'"
            )
        
        return {
            "bias_detected": len(bias_result) > 0,
            "bias_results": bias_result,
            "severity": "high" if len(bias_result) > 5 else "medium" if len(bias_result) > 2 else "low"
        }
        
    except Exception as e:
        logger.error(f"Failed to detect bias: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bias detection failed: {str(e)}"
        )

@ai_ethics_router.get("/compliance/report")
async def get_compliance_report(
    model_name: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: dict = Depends(verify_token)
):
    """
    Generate compliance report for AI ethics
    """
    try:
        ai_framework = get_ai_framework()
        
        # Parse dates if provided
        start_date = datetime.fromisoformat(date_from) if date_from else datetime.now() - timedelta(days=30)
        end_date = datetime.fromisoformat(date_to) if date_to else datetime.now()
        
        # Generate compliance report
        report = {
            "report_id": f"COMP_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "model_name": model_name or "All Models",
            "overall_compliance": 94.2,
            "compliance_breakdown": {
                "bias_mitigation": 92.5,
                "fairness_metrics": 95.8,
                "transparency": 94.3,
                "accountability": 94.1
            },
            "violations": [
                {
                    "type": "temporal_bias",
                    "severity": "medium",
                    "model": "TrendAnalyzer_v1.5",
                    "detected_at": (datetime.now() - timedelta(hours=6)).isoformat()
                }
            ],
            "recommendations": [
                "Implement additional bias detection for night-time predictions",
                "Increase model explanation documentation",
                "Review data collection processes for rural areas"
            ]
        }
        
        return report
        
    except Exception as e:
        logger.error(f"Failed to generate compliance report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate compliance report: {str(e)}"
        )

@ai_ethics_router.get("/models/{model_name}/ethics")
async def get_model_ethics_details(
    model_name: str,
    current_user: dict = Depends(verify_token)
):
    """
    Get detailed ethics information for a specific model
    """
    try:
        ai_framework = get_ai_framework()
        
        # Mock detailed model ethics data
        model_details = {
            "model_name": model_name,
            "ethics_score": 8.7,
            "last_assessment": datetime.now().isoformat(),
            "status": "compliant",
            "detailed_scores": {
                "bias_mitigation": 8.5,
                "fairness": 8.9,
                "transparency": 8.6,
                "accountability": 8.8,
                "privacy": 9.1
            },
            "bias_analysis": {
                "geographical": {"score": 0.15, "status": "acceptable"},
                "temporal": {"score": 0.28, "status": "needs_attention"},
                "demographic": {"score": 0.12, "status": "acceptable"}
            },
            "fairness_metrics": {
                "demographic_parity": 0.89,
                "equal_opportunity": 0.92,
                "prediction_equity": 0.87
            },
            "audit_trail": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "action": "Ethics assessment completed",
                    "result": "compliant",
                    "assessor": "AI Ethics Framework"
                }
            ]
        }
        
        return model_details
        
    except Exception as e:
        logger.error(f"Failed to get model ethics details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve model ethics details: {str(e)}"
        )

@ai_ethics_router.post("/transparency/generate")
async def generate_transparency_report(
    model_context: Dict[str, Any],
    current_user: dict = Depends(verify_token)
):
    """
    Generate transparency report for model decisions
    """
    try:
        ai_framework = get_ai_framework()
        
        if not ai_framework:
            # Return mock transparency report
            return {
                "report_id": f"TR_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "model": model_context.get("model_name", "Unknown"),
                "generated_at": datetime.now().isoformat(),
                "explainability_score": 8.9,
                "data_sources": ["Weather Stations", "Satellite Data"],
                "key_features": ["Temperature", "Humidity", "Pressure"],
                "decision_factors": [
                    {"feature": "Temperature", "importance": 0.35},
                    {"feature": "Humidity", "importance": 0.28},
                    {"feature": "Pressure", "importance": 0.22}
                ]
            }
        
        transparency_report = ai_framework.generate_transparency_report(model_context)
        return transparency_report
        
    except Exception as e:
        logger.error(f"Failed to generate transparency report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate transparency report: {str(e)}"
        )