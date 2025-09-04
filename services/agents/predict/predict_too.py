import joblib
import pandas as pd
import numpy as np
from datetime import datetime

# 1. Load Trained Artifacts (saved from train.py)
model = joblib.load("climate_condition_model.pkl") # Trained Random Forest model
label_encoder = joblib.load("label_encoder.pkl")  # Encoder for target labels
imputer = joblib.load("feature_imputer.pkl")   # Imputer for missing values

# Feature order must match training
feature_cols = [
    "doy_sin", "doy_cos", # cyclical date features
    "sunrise_hour", "sunrise_minute", # sunrise features
    "sunset_hour", "sunset_minute",  # sunset features
    "humidity", "sealevelpressure", "temp" # numeric weather features
]

# 2. Preprocess User Inputs
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

    # ---- 2. Extract sunrise time (hour, minute) ----
    if "sunrise" in data:
        sunrise = datetime.strptime(data["sunrise"], "%I:%M:%S %p")
        features["sunrise_hour"] = sunrise.hour
        features["sunrise_minute"] = sunrise.minute

    # ---- 3. Extract sunset time (hour, minute) ----
    if "sunset" in data:
        sunset = datetime.strptime(data["sunset"], "%I:%M:%S %p")
        features["sunset_hour"] = sunset.hour
        features["sunset_minute"] = sunset.minute

    # ---- 4. Directly use numeric values (humidity, pressure, temp) ----
    for col in ["humidity", "sealevelpressure", "temp"]:
        if col in data:
            features[col] = float(data[col])

    return features

# 3. Predict Weather Condition
def predict_condition(inputs: dict) -> str:
    """Take raw user input -> preprocess -> predict condition label"""
    # Step 1: Preprocess user input → feature dictionary
    processed = preprocess_inputs(inputs)

    # Step 2: Arrange features in the correct column order
    user_features = [processed.get(col, None) for col in feature_cols]
    X = pd.DataFrame([user_features], columns=feature_cols)

    # Step 3: Handle missing values using imputer
    X_imputed = imputer.transform(X)
    # Step 4: Predict using trained model
    pred_idx = model.predict(X_imputed)[0]
    # Step 5: Convert numeric prediction back to label
    pred_label = label_encoder.inverse_transform([pred_idx])[0]
    return pred_label
