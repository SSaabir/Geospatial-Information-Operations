# train_model.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report
import joblib
import numpy as np
import os

# Define paths
DATA_PATH = "C:/Users/abdul/OneDrive/Desktop/Y3.S1.DS.WE.01.01_IT23336322/New folder/Geospatial-Information-Operations/services/agents/preprocessed_climate_dataset5.csv"
MODEL_SAVE_PATH = "C:/Users/abdul/OneDrive/Desktop/Y3.S1.DS.WE.01.01_IT23336322/New folder/Geospatial-Information-Operations/services/agents/predict"

# Create the directory if it doesn't exist
os.makedirs(MODEL_SAVE_PATH, exist_ok=True)
print(f"📁 Model save directory: {MODEL_SAVE_PATH}")

# 1. Load dataset
df = pd.read_csv(DATA_PATH)

print("\nDataset Preview:")
print(df.head())
print(f"Dataset shape: {df.shape}")

# Drop irrelevant columns (keep datetime, sunrise, sunset)
drop_cols = ["name", "icon"]
df = df.drop(columns=drop_cols, errors="ignore")

# Drop rows where target is missing
initial_rows = len(df)
df = df.dropna(subset=["conditions"])
print(f"\nDropped {initial_rows - len(df)} rows with missing target")

# ---- Feature Engineering ----
print("\n⚙️  Feature Engineering...")

# Parse datetime (date only)
df["datetime"] = pd.to_datetime(df["datetime"], format="%m/%d/%Y", errors="coerce")

# Parse sunrise/sunset (time only)
df["sunrise"] = pd.to_datetime(df["sunrise"], format="%I:%M:%S %p", errors="coerce")
df["sunset"] = pd.to_datetime(df["sunset"], format="%I:%M:%S %p", errors="coerce")

# Extract day of year
df["dayofyear"] = df["datetime"].dt.dayofyear

# Cyclical encodings for seasonality
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
print("\n🔧 Handling missing values...")
imputer = SimpleImputer(strategy="median")
X_imputed = imputer.fit_transform(X)

# Encode target labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Show class balance
print("\n📊 Class Distribution (%):")
class_dist = pd.Series(y).value_counts(normalize=True) * 100
for condition, percentage in class_dist.items():
    print(f"  {condition:20s}: {percentage:6.2f}%")

# 2. Train/test split
print("\n🔀 Splitting data (80% train, 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(
    X_imputed, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)
print(f"Training samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")

# 3. Train classifier
print("\n🤖 Training Random Forest Classifier...")
model = RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

train_accuracy = model.score(X_train, y_train)
test_accuracy = model.score(X_test, y_test)

print(f"\n✅ Model Training Accuracy: {train_accuracy:.4f} ({train_accuracy*100:.2f}%)")
print(f"✅ Model Test Accuracy: {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")

# Classification Report
print("\n📊 Classification Report:")
print(classification_report(
    y_test,
    model.predict(X_test),
    target_names=label_encoder.classes_.astype(str),
    zero_division=0
))

# 4. Save trained model + encoder + imputer to specified path
print(f"\n💾 Saving models to: {MODEL_SAVE_PATH}")

model_file = os.path.join(MODEL_SAVE_PATH, "climate_condition_model.pkl")
encoder_file = os.path.join(MODEL_SAVE_PATH, "label_encoder.pkl")
imputer_file = os.path.join(MODEL_SAVE_PATH, "feature_imputer.pkl")

joblib.dump(model, model_file)
joblib.dump(label_encoder, encoder_file)
joblib.dump(imputer, imputer_file)

print(f"✅ Model saved to: {model_file}")
print(f"✅ Label Encoder saved to: {encoder_file}")
print(f"✅ Feature Imputer saved to: {imputer_file}")

# Verify saved files
print("\n🔍 Verifying saved files...")
if os.path.exists(model_file):
    print(f"✅ {os.path.basename(model_file)} - {os.path.getsize(model_file) / 1024:.2f} KB")
if os.path.exists(encoder_file):
    print(f"✅ {os.path.basename(encoder_file)} - {os.path.getsize(encoder_file) / 1024:.2f} KB")
if os.path.exists(imputer_file):
    print(f"✅ {os.path.basename(imputer_file)} - {os.path.getsize(imputer_file) / 1024:.2f} KB")

print("\n" + "="*60)
print("✅ TRAINING COMPLETE!")
print("="*60)
print(f"\nAll files saved successfully in:")
print(f"{MODEL_SAVE_PATH}")
print("\nYou can now load these files in your prediction API.")