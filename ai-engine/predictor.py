"""
AgriNova AI Engine — Main Prediction Interface
Scikit-Learn RandomForest-based moisture stress prediction.
Isolated module that can be replaced with a fully trained model.
"""
import os
import numpy as np
import joblib
import structlog
from typing import Optional

logger = structlog.get_logger(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "agrinova_model.joblib")

# Stress level thresholds
STRESS_THRESHOLDS = {
    "healthy": (0, 30),
    "moderate": (30, 65),
    "critical": (65, 100),
}


class AgriNovaPredictor:
    """
    Main prediction interface for moisture stress analysis.
    
    Loads a pre-trained RandomForest model and exposes a single `predict()` method.
    The model is trained on 5 features:
        [ndvi, ndwi, temperature, humidity, rainfall]
    
    This class is designed as a clean interface:
    - Swap out the model file to upgrade to a production-trained model
    - All business logic (recommendations, confidence) lives here
    - No database dependencies — pure prediction logic
    """

    def __init__(self):
        self.model = None
        self.scaler = None
        self._load_model()

    def _load_model(self):
        """Load the pre-trained model and scaler from disk."""
        if os.path.exists(MODEL_PATH):
            try:
                artifacts = joblib.load(MODEL_PATH)
                self.model = artifacts.get("model")
                self.scaler = artifacts.get("scaler")
                logger.info("ai_model_loaded", path=MODEL_PATH)
            except Exception as e:
                logger.warning("ai_model_load_failed", error=str(e))
                self.model = None
        else:
            logger.info("ai_model_not_found", path=MODEL_PATH, fallback="rule_based")

    def predict(
        self,
        ndvi: float,
        ndwi: float,
        temperature: float,
        humidity: float,
        rainfall: float,
        crop_type: str = "other",
    ) -> dict:
        """
        Run a moisture stress prediction.
        
        Args:
            ndvi: Normalized Difference Vegetation Index (-1 to 1)
            ndwi: Normalized Difference Water Index (-1 to 1)
            temperature: Temperature in Celsius
            humidity: Relative humidity percentage (0-100)
            rainfall: Rainfall in mm (recent 24h)
            crop_type: Crop type for contextual recommendation
        
        Returns:
            dict with keys: stress_level, stress_score, confidence, recommendation, analysis
        """
        if self.model and self.scaler:
            return self._ml_predict(ndvi, ndwi, temperature, humidity, rainfall, crop_type)
        else:
            return self._rule_based_predict(ndvi, ndwi, temperature, humidity, rainfall, crop_type)

    def _ml_predict(
        self, ndvi: float, ndwi: float, temperature: float,
        humidity: float, rainfall: float, crop_type: str
    ) -> dict:
        """ML-based prediction using RandomForest."""
        try:
            features = np.array([[ndvi, ndwi, temperature, humidity, rainfall]])
            features_scaled = self.scaler.transform(features)

            # Model predicts class (0=healthy, 1=moderate, 2=critical)
            prediction_class = self.model.predict(features_scaled)[0]
            probabilities = self.model.predict_proba(features_scaled)[0]
            confidence = round(float(np.max(probabilities)) * 100, 1)

            # Map class to stress score
            class_to_score = {0: 15.0, 1: 50.0, 2: 82.0}
            stress_score = class_to_score[prediction_class]
            # Add variance based on probability
            stress_score += (0.5 - probabilities[prediction_class]) * 20
            stress_score = round(max(0, min(100, stress_score)), 2)

            level_map = {0: "healthy", 1: "moderate", 2: "critical"}
            stress_level = level_map[prediction_class]

            recommendation = self._generate_recommendation(
                stress_level, stress_score, ndvi, ndwi, temperature, rainfall, crop_type
            )

            return {
                "stress_level": stress_level,
                "stress_score": stress_score,
                "confidence": confidence,
                "recommendation": recommendation,
                "analysis": {
                    "model_type": "RandomForestClassifier",
                    "probabilities": {
                        "healthy": round(float(probabilities[0]) * 100, 1),
                        "moderate": round(float(probabilities[1]) * 100, 1),
                        "critical": round(float(probabilities[2]) * 100, 1),
                    },
                    "features": {
                        "ndvi": ndvi, "ndwi": ndwi,
                        "temperature": temperature, "humidity": humidity,
                        "rainfall": rainfall,
                    },
                },
            }
        except Exception as e:
            logger.error("ml_prediction_failed", error=str(e))
            return self._rule_based_predict(ndvi, ndwi, temperature, humidity, rainfall, crop_type)

    def _rule_based_predict(
        self, ndvi: float, ndwi: float, temperature: float,
        humidity: float, rainfall: float, crop_type: str
    ) -> dict:
        """Scientifically-grounded rule-based prediction as fallback."""
        score = 0.0

        # NDVI contribution (40% weight)
        if ndvi < 0.2:
            score += 40
        elif ndvi < 0.35:
            score += 30
        elif ndvi < 0.5:
            score += 15
        elif ndvi < 0.65:
            score += 5

        # NDWI contribution (30% weight)
        if ndwi < -0.4:
            score += 30
        elif ndwi < -0.2:
            score += 20
        elif ndwi < 0.0:
            score += 10
        elif ndwi < 0.1:
            score += 5

        # Temperature heat stress (20% weight)
        if temperature > 40:
            score += 20
        elif temperature > 35:
            score += 12
        elif temperature > 30:
            score += 6

        # Humidity (5% weight)
        if humidity < 25:
            score += 5
        elif humidity < 40:
            score += 3

        # Rainfall benefit (negative contribution)
        if rainfall > 15:
            score = max(0, score - 20)
        elif rainfall > 8:
            score = max(0, score - 12)
        elif rainfall > 3:
            score = max(0, score - 6)

        score = round(min(100, max(0, score)), 2)
        confidence = round(75.0 + (50 - abs(score - 50)) * 0.2, 1)

        if score < 30:
            stress_level = "healthy"
        elif score < 65:
            stress_level = "moderate"
        else:
            stress_level = "critical"

        recommendation = self._generate_recommendation(
            stress_level, score, ndvi, ndwi, temperature, rainfall, crop_type
        )

        return {
            "stress_level": stress_level,
            "stress_score": score,
            "confidence": min(95, confidence),
            "recommendation": recommendation,
            "analysis": {
                "model_type": "RuleBasedFallback",
                "ndvi_status": "good" if ndvi >= 0.55 else ("moderate" if ndvi >= 0.4 else "poor"),
                "ndwi_status": "adequate" if ndwi >= 0 else ("low" if ndwi >= -0.2 else "critical"),
                "features": {
                    "ndvi": ndvi, "ndwi": ndwi,
                    "temperature": temperature, "humidity": humidity,
                    "rainfall": rainfall,
                },
            },
        }

    def _generate_recommendation(
        self, stress_level: str, score: float, ndvi: float,
        ndwi: float, temperature: float, rainfall: float, crop_type: str
    ) -> str:
        """Generate actionable, specific recommendation text."""
        crop = crop_type.replace("_", " ").title()

        if stress_level == "critical":
            if temperature > 35:
                return (
                    f"⚠️ CRITICAL: {crop} experiencing severe heat and water stress "
                    f"(score {score:.0f}/100, temp {temperature:.1f}°C). "
                    "Irrigate immediately — 50-60mm within 24 hours. Monitor soil temperature."
                )
            return (
                f"⚠️ CRITICAL: Severe moisture deficit in {crop} field "
                f"(NDWI: {ndwi:.2f}, NDVI: {ndvi:.2f}). "
                "Emergency irrigation required within 24 hours to prevent crop loss."
            )

        elif stress_level == "moderate":
            if rainfall > 5:
                return (
                    f"⚠️ MODERATE: Recent rainfall ({rainfall:.1f}mm) provides partial relief for {crop}. "
                    "Plan supplemental irrigation within 48 hours if no additional rain forecast."
                )
            return (
                f"⚠️ MODERATE: {crop} showing moisture stress (NDVI: {ndvi:.2f}). "
                "Schedule irrigation within 48 hours — focus on lower NDVI sectors."
            )

        else:
            return (
                f"✅ HEALTHY: {crop} field conditions optimal "
                f"(NDVI: {ndvi:.2f}, score: {score:.0f}/100). "
                "Maintain current management. Next analysis recommended in 7 days."
            )
