import os
import sys

# Ensure ai-engine folder is in Python path for import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../ai-engine')))

import pytest
from predictor import AgriNovaPredictor


def test_predictor_healthy():
    predictor = AgriNovaPredictor()
    result = predictor.predict(
        ndvi=0.75,
        ndwi=0.15,
        temperature=22.0,
        humidity=70.0,
        rainfall=10.0,
        crop_type="corn"
    )
    assert result["stress_level"] == "healthy"
    assert result["stress_score"] < 30
    assert "HEALTHY" in result["recommendation"]


def test_predictor_critical():
    predictor = AgriNovaPredictor()
    result = predictor.predict(
        ndvi=0.15,
        ndwi=-0.45,
        temperature=42.0,
        humidity=20.0,
        rainfall=0.0,
        crop_type="wheat"
    )
    assert result["stress_level"] == "critical"
    assert result["stress_score"] >= 65
    assert "CRITICAL" in result["recommendation"]
