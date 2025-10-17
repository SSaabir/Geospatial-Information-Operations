# api/weather_prediction_api.py
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field, validator
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
import os
import sys
import json
from typing import Dict, Optional
import logging
import traceback

# Add agents directory to path for responsible AI import
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents'))

try:
    from responsible_ai import run_responsible_ai_assessment, get_responsible_ai_framework
    RESPONSIBLE_AI_AVAILABLE = True
except Exception as e:
    RESPONSIBLE_AI_AVAILABLE = False
    print(f"⚠️ Responsible AI framework not available: {e}")

# Set up logging
logger = logging.getLogger(__name__)

# Log Responsible AI availability
if RESPONSIBLE_AI_AVAILABLE:
    logger.info("✅ Responsible AI framework loaded for prediction endpoint")
else:
    logger.warning("⚠️ Responsible AI framework not available - predictions will run without ethics checks")

# Create router
weather_router = APIRouter(
    prefix="/api/weather",
    tags=["Weather Prediction"]
)

# Define model path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "agents", "predict")

logger.info(f"Weather Prediction API - Model directory: {MODEL_DIR}")

# Load models at module level
model = None
label_encoder = None
imputer = None

def load_models():
    """Load ML models"""
    global model, label_encoder, imputer
    
    try:
        # Try optimized model first, then fall back to regular model
        model_file = os.path.join(MODEL_DIR, "climate_condition_model_optimized.pkl")
        if not os.path.exists(model_file):
            model_file = os.path.join(MODEL_DIR, "climate_condition_model.pkl")
        
        encoder_file = os.path.join(MODEL_DIR, "label_encoder.pkl")
        imputer_file = os.path.join(MODEL_DIR, "feature_imputer.pkl")
        
        # Check if directory exists
        if not os.path.exists(MODEL_DIR):
            logger.error(f"❌ Model directory not found: {MODEL_DIR}")
            return False
        
        # Log which files exist
        logger.info(f"Checking model files in: {MODEL_DIR}")
        logger.info(f"  - Model file exists: {os.path.exists(model_file)} ({os.path.basename(model_file)})")
        logger.info(f"  - Encoder file exists: {os.path.exists(encoder_file)}")
        logger.info(f"  - Imputer file exists: {os.path.exists(imputer_file)}")
        
        # Check if all files exist
        if not all(os.path.exists(f) for f in [model_file, encoder_file, imputer_file]):
            logger.error("❌ One or more model files not found")
            return False
        
        # Load models
        model = joblib.load(model_file)
        label_encoder = joblib.load(encoder_file)
        imputer = joblib.load(imputer_file)
        
        logger.info("✅ Weather prediction models loaded successfully")
        logger.info(f"✅ Available conditions: {list(label_encoder.classes_)}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error loading weather prediction models: {e}")
        logger.error(traceback.format_exc())
        return False

# Try to load models on import
models_loaded = load_models()
if models_loaded:
    logger.info("🚀 Weather prediction API ready")
else:
    logger.warning("⚠️ Weather prediction API started but models not loaded")

# Pydantic models
class WeatherInput(BaseModel):
    datetime: str = Field(..., description="Date in MM/DD/YYYY format", example="2/19/1997")
    sunrise: str = Field(..., description="Sunrise time in hh:mm:ss AM/PM format", example="6:56:39 AM")
    sunset: str = Field(..., description="Sunset time in hh:mm:ss AM/PM format", example="6:52:29 PM")
    humidity: float = Field(..., ge=0, le=100, description="Humidity percentage (0-100)", example=70.0)
    sealevelpressure: float = Field(..., ge=900, le=1100, description="Sea level pressure in hPa", example=1020.0)
    temp: float = Field(..., ge=-50, le=60, description="Temperature in Celsius", example=20.0)
    
    @validator('datetime')
    def validate_datetime(cls, v):
        try:
            pd.to_datetime(v, format="%m/%d/%Y")
            return v
        except:
            raise ValueError("Date must be in MM/DD/YYYY format")
    
    @validator('sunrise', 'sunset')
    def validate_time(cls, v):
        try:
            pd.to_datetime(v, format="%I:%M:%S %p")
            return v
        except:
            raise ValueError("Time must be in hh:mm:ss AM/PM format")

class PredictionResponse(BaseModel):
    result: str
    confidence: float
    all_probabilities: Dict[str, float]
    processed_features: Dict[str, float]

# Helper function to get optional user
async def get_optional_user(authorization: Optional[str] = Header(None)):
    """Get user if authenticated, return None if not"""
    if not authorization:
        return None
    
    try:
        from security.auth_middleware import get_current_user
        # Try to get user, but don't fail if not authenticated
        return await get_current_user(authorization)
    except:
        return None

@weather_router.get("/health")
async def weather_health():
    """Check if weather prediction service is available"""
    models_loaded = all([model is not None, label_encoder is not None, imputer is not None])
    
    return {
        "status": "healthy" if models_loaded else "models_not_loaded",
        "models_loaded": models_loaded,
        "model_directory": MODEL_DIR,
        "model_files_exist": {
            "optimized_model": os.path.exists(os.path.join(MODEL_DIR, "climate_condition_model_optimized.pkl")),
            "regular_model": os.path.exists(os.path.join(MODEL_DIR, "climate_condition_model.pkl")),
            "label_encoder": os.path.exists(os.path.join(MODEL_DIR, "label_encoder.pkl")),
            "feature_imputer": os.path.exists(os.path.join(MODEL_DIR, "feature_imputer.pkl"))
        },
        "available_conditions": list(label_encoder.classes_) if label_encoder else []
    }

@weather_router.get("/conditions")
async def get_conditions():
    """Get all available weather conditions"""
    if label_encoder is None:
        raise HTTPException(
            status_code=503,
            detail="Weather prediction models not loaded. Please ensure model files exist."
        )
    
    return {
        "conditions": list(label_encoder.classes_),
        "total": len(label_encoder.classes_)
    }

@weather_router.post("/predict", response_model=PredictionResponse)
async def predict_weather(data: WeatherInput):
    """
    Predict weather condition based on atmospheric parameters
    PUBLIC ENDPOINT - No authentication required
    
    - **datetime**: Date in MM/DD/YYYY format
    - **sunrise**: Sunrise time in hh:mm:ss AM/PM format
    - **sunset**: Sunset time in hh:mm:ss AM/PM format
    - **humidity**: Humidity percentage (0-100)
    - **sealevelpressure**: Sea level pressure in hPa (900-1100)
    - **temp**: Temperature in Celsius (-50 to 60)
    """
    
    # Check if models are loaded
    if model is None or label_encoder is None or imputer is None:
        # Try to reload models
        if not load_models():
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "Weather prediction models not loaded",
                    "message": "Please ensure model files exist in the agents/predict directory",
                    "model_path": MODEL_DIR,
                    "required_files": [
                        "climate_condition_model_optimized.pkl OR climate_condition_model.pkl",
                        "label_encoder.pkl",
                        "feature_imputer.pkl"
                    ]
                }
            )
    
    try:
        logger.info(f"📥 Weather prediction request - Date: {data.datetime}, Temp: {data.temp}°C")
        
        # Parse datetime
        dt = pd.to_datetime(data.datetime, format="%m/%d/%Y")
        sunrise = pd.to_datetime(data.sunrise, format="%I:%M:%S %p")
        sunset = pd.to_datetime(data.sunset, format="%I:%M:%S %p")
        
        # Feature engineering (same as training)
        dayofyear = dt.dayofyear
        doy_sin = np.sin(2 * np.pi * dayofyear / 365.25)
        doy_cos = np.cos(2 * np.pi * dayofyear / 365.25)
        
        # Create feature array in the same order as training
        features = np.array([[
            doy_sin,
            doy_cos,
            sunrise.hour,
            sunrise.minute,
            sunset.hour,
            sunset.minute,
            data.humidity,
            data.sealevelpressure,
            data.temp
        ]])
        
        # Impute and predict
        features_imputed = imputer.transform(features)
        prediction_encoded = model.predict(features_imputed)
        prediction = label_encoder.inverse_transform(prediction_encoded)[0]
        
        # Get confidence scores
        probabilities = model.predict_proba(features_imputed)[0]
        max_confidence = float(np.max(probabilities))
        
        # Create probability dictionary
        all_probabilities = {
            str(label): float(prob) 
            for label, prob in zip(label_encoder.classes_, probabilities)
        }
        
        # Sort by probability (highest first)
        all_probabilities = dict(sorted(all_probabilities.items(), key=lambda x: x[1], reverse=True))
        
        # Processed features for response
        processed_features = {
            "doy_sin": float(doy_sin),
            "doy_cos": float(doy_cos),
            "dayofyear": int(dayofyear),
            "sunrise_hour": int(sunrise.hour),
            "sunrise_minute": int(sunrise.minute),
            "sunset_hour": int(sunset.hour),
            "sunset_minute": int(sunset.minute),
            "humidity": float(data.humidity),
            "sealevelpressure": float(data.sealevelpressure),
            "temp": float(data.temp)
        }
        
        # ✅ RESPONSIBLE AI ASSESSMENT (Non-blocking)
        ethics_status = None
        if RESPONSIBLE_AI_AVAILABLE:
            try:
                # Prepare prediction data for ethics assessment
                prediction_data = [{
                    "datetime": data.datetime,
                    "predicted": prediction,
                    "confidence": max_confidence,
                    "temp": data.temp,
                    "humidity": data.humidity,
                    "sealevelpressure": data.sealevelpressure
                }]
                
                model_metadata = {
                    "name": "weather_prediction_model",
                    "version": "1.0",
                    "algorithm": "Random Forest",
                    "endpoint": "/api/weather/predict",
                    "timestamp": datetime.now().isoformat()
                }
                
                # Run ethics assessment (this logs to database but doesn't block)
                ethics_result = run_responsible_ai_assessment(
                    prediction_data, 
                    prediction_data,  # Using prediction as training data for basic check
                    model_metadata
                )
                ethics_data = json.loads(ethics_result)
                ethics_status = {
                    "ethics_level": ethics_data.get("ethics_level", "unknown"),
                    "transparency_score": ethics_data.get("transparency_score", 0),
                    "checked": True
                }
                logger.info(f"🤖 Ethics check: {ethics_status['ethics_level']}")
                
            except Exception as ethics_error:
                logger.warning(f"⚠️ Ethics assessment failed (non-critical): {ethics_error}")
                ethics_status = {"checked": False, "error": str(ethics_error)}
        else:
            ethics_status = {"checked": False, "reason": "framework_unavailable"}
        
        logger.info(f"✅ Prediction: {prediction} (Confidence: {max_confidence:.2%})")
        
        response = {
            "result": f"Predicted Weather Condition: {prediction}",
            "confidence": max_confidence,
            "all_probabilities": all_probabilities,
            "processed_features": processed_features
        }
        
        # Add ethics info if available (optional field, doesn't break existing clients)
        if ethics_status and ethics_status.get("checked"):
            response["ethics_assessment"] = ethics_status
        
        return response
        
    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=f"Validation error: {str(ve)}")
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@weather_router.post("/reload-models")
async def reload_models():
    """Reload weather prediction models (admin only)"""
    success = load_models()
    
    if success:
        return {
            "status": "success",
            "message": "Models reloaded successfully",
            "available_conditions": list(label_encoder.classes_) if label_encoder else []
        }
    else:
        raise HTTPException(
            status_code=503,
            detail="Failed to reload models. Check server logs for details."
        )