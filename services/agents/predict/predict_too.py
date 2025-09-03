import joblib
import pandas as pd
import numpy as np
from datetime import datetime

# Load trained artifacts
model = joblib.load("climate_condition_model.pkl")
label_encoder = joblib.load("label_encoder.pkl")
imputer = joblib.load("feature_imputer.pkl")

feature_cols = [
    "doy_sin", "doy_cos",
    "sunrise_hour", "sunrise_minute",
    "sunset_hour", "sunset_minute",
    "humidity", "sealevelpressure", "temp"
]

def preprocess_inputs(data: dict) -> dict:
    """
    Convert raw inputs (datetime, sunrise, sunset) into ML features.
    """
    features = {}

    # ---- 1. Convert datetime to day-of-year (sin & cos) ----
    if "datetime" in data:
        dt = pd.to_datetime(data["datetime"], format="%m/%d/%Y")
        day_of_year = dt.timetuple().tm_yday
        features["doy_sin"] = np.sin(2 * np.pi * day_of_year / 365)
        features["doy_cos"] = np.cos(2 * np.pi * day_of_year / 365)

    # ---- 2. Parse sunrise time ----
    if "sunrise" in data:
        sunrise = datetime.strptime(data["sunrise"], "%I:%M:%S %p")
        features["sunrise_hour"] = sunrise.hour
        features["sunrise_minute"] = sunrise.minute

    # ---- 3. Parse sunset time ----
    if "sunset" in data:
        sunset = datetime.strptime(data["sunset"], "%I:%M:%S %p")
        features["sunset_hour"] = sunset.hour
        features["sunset_minute"] = sunset.minute

    # ---- 4. Keep numeric values directly ----
    for col in ["humidity", "sealevelpressure", "temp"]:
        if col in data:
            features[col] = float(data[col])

    return features

def predict_condition(inputs: dict) -> str:
    """Take raw user input -> preprocess -> predict condition label"""
    processed = preprocess_inputs(inputs)

    user_features = [processed.get(col, None) for col in feature_cols]
    X = pd.DataFrame([user_features], columns=feature_cols)
    X_imputed = imputer.transform(X)
    pred_idx = model.predict(X_imputed)[0]
    pred_label = label_encoder.inverse_transform([pred_idx])[0]
    return pred_label
