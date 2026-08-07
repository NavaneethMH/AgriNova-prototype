"""
Model training script for AgriNova moisture stress classifier.
Trains a RandomForest model on synthetic agricultural data.
Run this script once to generate the model artifact:
    python train_model.py
"""
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import structlog

logger = structlog.get_logger(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "agrinova_model.joblib")


def generate_training_data(n_samples: int = 5000) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate synthetic training data based on agronomic research.
    
    Features: [ndvi, ndwi, temperature, humidity, rainfall]
    Labels: 0=healthy, 1=moderate, 2=critical
    
    Rules are based on published agronomic thresholds:
    - NDVI < 0.35 indicates stressed vegetation
    - NDWI < -0.2 indicates water deficit
    - Temperature > 35°C causes heat stress
    - Low humidity + no rainfall = increased stress
    """
    np.random.seed(42)
    X = []
    y = []

    # Generate HEALTHY samples (label 0)
    n_healthy = n_samples // 3
    for _ in range(n_healthy):
        ndvi = np.random.uniform(0.55, 0.95)
        ndwi = np.random.uniform(-0.05, 0.4)
        temperature = np.random.uniform(15, 30)
        humidity = np.random.uniform(55, 90)
        rainfall = np.random.uniform(0, 25)
        X.append([ndvi, ndwi, temperature, humidity, rainfall])
        y.append(0)

    # Generate MODERATE STRESS samples (label 1)
    n_moderate = n_samples // 3
    for _ in range(n_moderate):
        ndvi = np.random.uniform(0.35, 0.60)
        ndwi = np.random.uniform(-0.25, 0.05)
        temperature = np.random.uniform(28, 38)
        humidity = np.random.uniform(35, 65)
        rainfall = np.random.uniform(0, 8)
        X.append([ndvi, ndwi, temperature, humidity, rainfall])
        y.append(1)

    # Generate CRITICAL STRESS samples (label 2)
    n_critical = n_samples - n_healthy - n_moderate
    for _ in range(n_critical):
        ndvi = np.random.uniform(0.05, 0.40)
        ndwi = np.random.uniform(-0.60, -0.15)
        temperature = np.random.uniform(33, 45)
        humidity = np.random.uniform(15, 45)
        rainfall = np.random.uniform(0, 3)
        X.append([ndvi, ndwi, temperature, humidity, rainfall])
        y.append(2)

    # Add noise to simulate real-world variability
    X_arr = np.array(X)
    X_arr += np.random.normal(0, 0.02, X_arr.shape)
    # Clip to valid ranges
    X_arr[:, 0] = np.clip(X_arr[:, 0], -1, 1)   # ndvi
    X_arr[:, 1] = np.clip(X_arr[:, 1], -1, 1)   # ndwi
    X_arr[:, 2] = np.clip(X_arr[:, 2], -10, 55) # temperature
    X_arr[:, 3] = np.clip(X_arr[:, 3], 0, 100)  # humidity
    X_arr[:, 4] = np.clip(X_arr[:, 4], 0, 100)  # rainfall

    return X_arr, np.array(y)


def train_and_save():
    """Train the RandomForest model and save to disk."""
    print("AgriNova AI Engine — Model Training")
    print("=" * 50)

    print("Generating synthetic training data...")
    X, y = generate_training_data(n_samples=10000)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Feature scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train RandomForest
    print("Training RandomForestClassifier...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train_scaled, y_train)

    # Evaluate
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nModel Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print("\nClassification Report:")
    print(classification_report(
        y_test, y_pred,
        target_names=["Healthy", "Moderate", "Critical"]
    ))

    # Feature importance
    feature_names = ["NDVI", "NDWI", "Temperature", "Humidity", "Rainfall"]
    importance = model.feature_importances_
    print("\nFeature Importances:")
    for name, imp in sorted(zip(feature_names, importance), key=lambda x: -x[1]):
        print(f"  {name:15s}: {imp:.4f} ({imp*100:.1f}%)")

    # Save model + scaler
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    artifacts = {"model": model, "scaler": scaler, "accuracy": accuracy}
    joblib.dump(artifacts, MODEL_PATH)
    print(f"\n✅ Model saved to: {MODEL_PATH}")
    return accuracy


if __name__ == "__main__":
    train_and_save()
