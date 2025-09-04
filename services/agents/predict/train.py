# train_model.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report
import joblib
import numpy as np

# 1. Load dataset
df = pd.read_csv("preprocessed_climate_dataset5.csv")

print("Dataset Preview:")
print(df.head())

#Drops irrelevant columns (name, icon).
#Removes rows where the target label (conditions) is missing.
# Drop irrelevant columns (keep datetime, sunrise, sunset)
drop_cols = ["name", "icon"]
df = df.drop(columns=drop_cols, errors="ignore")

# Drop rows where target is missing
df = df.dropna(subset=["conditions"])

# ---- Feature Engineering ----
#Converts date string → datetime object.
# Parse datetime (date only)
df["datetime"] = pd.to_datetime(df["datetime"], format="%m/%d/%Y", errors="coerce")

# Parse sunrise/sunset (time only)
# Convert sunrise/sunset strings → datetime objects (time only)
df["sunrise"] = pd.to_datetime(df["sunrise"], format="%I:%M:%S %p", errors="coerce")
df["sunset"] = pd.to_datetime(df["sunset"], format="%I:%M:%S %p", errors="coerce")

# Extract features from datetime
# Extract "day of year" from datetime (1–365)
df["dayofyear"] = df["datetime"].dt.dayofyear

# Cyclical encodings
# Encode "day of year" as sine/cosine (cyclical encoding)
# → Helps ML model understand yearly seasonality
df["doy_sin"] = np.sin(2*np.pi*df["dayofyear"]/365.25)
df["doy_cos"] = np.cos(2*np.pi*df["dayofyear"]/365.25)

# Extract features from sunrise/sunset
df["sunrise_hour"] = df["sunrise"].dt.hour
df["sunrise_minute"] = df["sunrise"].dt.minute
df["sunset_hour"] = df["sunset"].dt.hour
df["sunset_minute"] = df["sunset"].dt.minute

# ---- Select final features ----
feature_cols = [
    "doy_sin", "doy_cos",
    "sunrise_hour", "sunrise_minute",
    "sunset_hour", "sunset_minute",
    "humidity", "sealevelpressure", "temp"
]

X = df[feature_cols]
y = df["conditions"].astype(str)

# Handle missing values
# Replace missing numeric values with the median of that column
imputer = SimpleImputer(strategy="median")
X_imputed = imputer.fit_transform(X)

# Encode target labels
# Convert text labels (e.g. "Cloudy") → numeric values
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Show class balance
# Show class balance (percentage of each condition)
print("\n📊 Class Distribution:")
print(pd.Series(y).value_counts(normalize=True) * 100)

# 2. Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X_imputed, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

# 3. Train classifier
model = RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

print("\n✅ Model Test Accuracy:", model.score(X_test, y_test))

# 📊 Classification Report
# Detailed classification report (precision, recall, f1-score)
print("\n📊 Classification Report:")
print(classification_report(
    y_test,
    model.predict(X_test),
    target_names=label_encoder.classes_.astype(str),
    zero_division=0
))

# 4. Save trained model + encoder + imputer
# Save model, encoder, and imputer for later use in prediction API
joblib.dump(model, "climate_condition_model.pkl")
joblib.dump(label_encoder, "label_encoder.pkl")
joblib.dump(imputer, "feature_imputer.pkl")
print("\n✅ Model, LabelEncoder, and Imputer saved!")
