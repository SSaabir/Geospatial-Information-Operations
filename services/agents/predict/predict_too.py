import joblib
import pandas as pd
import numpy as np
from datetime import datetime

# 1. Load Trained Artifacts
MODEL_PATH = r"C:\Users\abdul\OneDrive\Desktop\auto2\FDM_NEW\IRWA\Geospatial-Information-Operations\climate_condition_model.pkl"
LABEL_ENCODER_PATH = r"C:\Users\abdul\OneDrive\Desktop\auto2\FDM_NEW\IRWA\Geospatial-Information-Operations\label_encoder.pkl"
IMPUTER_PATH = r"C:\Users\abdul\OneDrive\Desktop\auto2\FDM_NEW\IRWA\Geospatial-Information-Operations\feature_imputer.pkl"
model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(LABEL_ENCODER_PATH)
imputer = joblib.load(IMPUTER_PATH)

feature_cols = [
    "doy_sin", "doy_cos",
    "sunrise_hour", "sunrise_minute",
    "sunset_hour", "sunset_minute",
    "humidity", "sealevelpressure", "temp"
]

# 2. Preprocess Inputs
def preprocess_inputs(data: dict) -> dict:
    features = {}
    if "datetime" in data:
        dt = pd.to_datetime(data["datetime"], format="%m/%d/%Y")
        day_of_year = dt.timetuple().tm_yday
        features["doy_sin"] = np.sin(2 * np.pi * day_of_year / 365)
        features["doy_cos"] = np.cos(2 * np.pi * day_of_year / 365)

    if "sunrise" in data:
        sunrise = datetime.strptime(data["sunrise"], "%I:%M:%S %p")
        features["sunrise_hour"] = sunrise.hour
        features["sunrise_minute"] = sunrise.minute

    if "sunset" in data:
        sunset = datetime.strptime(data["sunset"], "%I:%M:%S %p")
        features["sunset_hour"] = sunset.hour
        features["sunset_minute"] = sunset.minute

    for col in ["humidity", "sealevelpressure", "temp"]:
        if col in data:
            features[col] = float(data[col])

    return features

# 3. Predict Weather Condition
def predict_condition(inputs: dict) -> str:
    processed = preprocess_inputs(inputs)
    user_features = [processed.get(col, None) for col in feature_cols]
    X = pd.DataFrame([user_features], columns=feature_cols)
    X_imputed = imputer.transform(X)
    pred_idx = model.predict(X_imputed)[0]
    pred_label = label_encoder.inverse_transform([pred_idx])[0]
    return pred_label

# ✅ 4. Connector Function for orchestrator.py
def run_predict_agent(raw_input: str) -> str:
    """
    This function is the bridge between orchastrator.py and predict_tool.py.
    It receives a JSON string from the workflow, parses it, 
    and returns the predicted weather condition.
    """
    import json
    try:
        user_data = json.loads(raw_input)  # Expecting JSON input from orchestrator
        prediction = predict_condition(user_data)
        return f"Predicted Weather Condition: {prediction}"
    except Exception as e:
        return f"Prediction Error: {e}"
