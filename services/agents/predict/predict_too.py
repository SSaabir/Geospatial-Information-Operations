# app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
import os
from typing import Dict, Optional

app = FastAPI(
    title="Weather Prediction API",
    description="AI-powered weather condition prediction based on atmospheric data",
    version="1.0.0"
)

# CORS middleware to allow requests from React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (you can restrict this in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the path where pickle files are saved
MODEL_PATH = "C:/Users/abdul/OneDrive/Desktop/Y3.S1.DS.WE.01.01_IT23336322/New folder/Geospatial-Information-Operations/services/agents/predict"

# Load models once when the app starts
print("=" * 60)
print("🚀 Starting Weather Prediction API...")
print("=" * 60)
print(f"📁 Loading models from: {MODEL_PATH}")

try:
    model_file = os.path.join(MODEL_PATH, "climate_condition_model.pkl")
    encoder_file = os.path.join(MODEL_PATH, "label_encoder.pkl")
    imputer_file = os.path.join(MODEL_PATH, "feature_imputer.pkl")
    
    model = joblib.load(model_file)
    label_encoder = joblib.load(encoder_file)
    imputer = joblib.load(imputer_file)
    
    print(f"✅ Model loaded: {model_file}")
    print(f"✅ Label Encoder loaded: {encoder_file}")
    print(f"✅ Feature Imputer loaded: {imputer_file}")
    print(f"\n📊 Available weather conditions: {list(label_encoder.classes_)}")
    print(f"📊 Total conditions: {len(label_encoder.classes_)}")
    print("=" * 60)
    
except FileNotFoundError as e:
    print(f"❌ Error loading models: {e}")
    print(f"Looking in directory: {MODEL_PATH}")
    print("\n⚠️  Please run train_model.py first to generate the model files!")
    print("=" * 60)
    model = None
    label_encoder = None
    imputer = None

class WeatherInput(BaseModel):
    datetime: str = Field(..., description="Date in MM/DD/YYYY format", example="3/15/2020")
    sunrise: str = Field(..., description="Sunrise time in hh:mm:ss AM/PM format", example="6:30:15 AM")
    sunset: str = Field(..., description="Sunset time in hh:mm:ss AM/PM format", example="6:45:20 PM")
    humidity: float = Field(..., ge=0, le=100, description="Humidity percentage (0-100)", example=68.0)
    sealevelpressure: float = Field(..., ge=900, le=1100, description="Sea level pressure in hPa", example=1015.2)
    temp: float = Field(..., ge=-50, le=60, description="Temperature in Celsius", example=18.5)
    
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

@app.get("/")
async def root():
    """Root endpoint - API status"""
    if model is None:
        return {
            "status": "error",
            "message": "Models not loaded. Please run train_model.py first!",
            "model_path": MODEL_PATH
        }
    return {
        "status": "running",
        "message": "Weather Prediction API is running!",
        "version": "1.0.0",
        "model_path": MODEL_PATH,
        "available_conditions": list(label_encoder.classes_),
        "endpoints": {
            "predict": "/predict (POST)",
            "health": "/health (GET)",
            "conditions": "/conditions (GET)",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    models_loaded = all([model is not None, label_encoder is not None, imputer is not None])
    return {
        "status": "healthy" if models_loaded else "unhealthy",
        "models_loaded": models_loaded,
        "model_path": MODEL_PATH,
        "available_conditions": list(label_encoder.classes_) if label_encoder else []
    }

@app.post("/predict")
async def predict(data: WeatherInput):
    """
    Predict weather condition based on input parameters
    """
    if model is None or label_encoder is None or imputer is None:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Models not loaded. Please run train_model.py first!",
                "model_path": MODEL_PATH,
                "instructions": "Run: python train_model.py"
            }
        )
    
    try:
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
        
        # Store processed features for response
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
        
        # Sort probabilities by value (highest first)
        all_probabilities = dict(sorted(all_probabilities.items(), key=lambda x: x[1], reverse=True))
        
        print(f"\n🔮 Prediction: {prediction} | Confidence: {max_confidence:.2%}")
        
        return PredictionResponse(
            result=f"Predicted Weather Condition: {prediction}",
            confidence=max_confidence,
            all_probabilities=all_probabilities,
            processed_features=processed_features
        )
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(ve)}")
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/conditions")
async def get_conditions():
    """Get all available weather conditions that can be predicted"""
    if label_encoder is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    return {
        "conditions": list(label_encoder.classes_),
        "total": len(label_encoder.classes_)
    }

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {
        "status": "ok",
        "message": "API is working!",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": all([model is not None, label_encoder is not None, imputer is not None])
    }

if __name__ == "__main__":
    import uvicorn
    print("\n🌐 Starting server on http://localhost:8000")
    print("📚 API documentation: http://localhost:8000/docs")
    print("🔧 Alternative docs: http://localhost:8000/redoc")
    print("\nPress CTRL+C to stop the server\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)