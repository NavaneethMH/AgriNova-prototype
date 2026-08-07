"""
AI Prediction and Recommendations endpoints.
"""
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, status, Query

from app.core.dependencies import CurrentUser, DBSession
from app.services.farm_service import FarmService
from app.services.prediction_service import PredictionService
from app.schemas.schemas import PredictRequest, PredictionResponse, RecommendationResponse

router = APIRouter()


def _pred_to_response(p) -> PredictionResponse:
    return PredictionResponse(
        id=str(p.id), farm_id=str(p.farm_id),
        stress_level=p.stress_level,
        stress_score=float(p.stress_score),
        confidence=float(p.confidence),
        recommendation=p.recommendation,
        detailed_analysis=p.detailed_analysis,
        healthy_pct=float(p.healthy_pct) if p.healthy_pct else None,
        moderate_pct=float(p.moderate_pct) if p.moderate_pct else None,
        critical_pct=float(p.critical_pct) if p.critical_pct else None,
        model_version=p.model_version,
        ndvi=float(p.ndvi) if p.ndvi else None,
        ndwi=float(p.ndwi) if p.ndwi else None,
        temperature=float(p.temperature) if p.temperature else None,
        humidity=float(p.humidity) if p.humidity else None,
        rainfall=float(p.rainfall) if p.rainfall else None,
        predicted_at=p.predicted_at,
    )


@router.post(
    "/",
    response_model=PredictionResponse,
    summary="Run an AI moisture stress prediction for a farm",
)
async def run_prediction(data: PredictRequest, current_user: CurrentUser, db: DBSession):
    """
    Run AI moisture stress prediction.
    
    - Accepts NDVI, NDWI, temperature, humidity, rainfall as optional inputs
    - Missing values are automatically populated from the farm's latest satellite/weather data
    - Returns stress level (healthy/moderate/critical), score (0-100), confidence (%), and recommendation
    """
    farm_service = FarmService(db)
    farm = await farm_service.get_by_id(data.farm_id, str(current_user.id))
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")

    pred_service = PredictionService(db)
    prediction = await pred_service.run_prediction(data, str(current_user.id), farm)
    return _pred_to_response(prediction)


@router.get(
    "/history/{farm_id}",
    response_model=list[PredictionResponse],
    summary="Get prediction history for a farm",
)
async def get_prediction_history(
    farm_id: str,
    current_user: CurrentUser,
    db: DBSession,
    limit: int = Query(10, ge=1, le=50),
):
    """Return the last N predictions for a farm."""
    farm_service = FarmService(db)
    farm = await farm_service.get_by_id(farm_id, str(current_user.id))
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")

    pred_service = PredictionService(db)
    predictions = await pred_service.get_history(farm_id, limit=limit)
    return [_pred_to_response(p) for p in predictions]


@router.get(
    "/recommendations/{farm_id}",
    response_model=RecommendationResponse,
    summary="Get AI-driven irrigation recommendations for a farm",
)
async def get_recommendations(farm_id: str, current_user: CurrentUser, db: DBSession):
    """
    Generate actionable recommendations based on the latest prediction.
    Includes urgency level, estimated water need, and secondary recommendations.
    """
    farm_service = FarmService(db)
    farm = await farm_service.get_by_id(farm_id, str(current_user.id))
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")

    pred_service = PredictionService(db)
    prediction = await pred_service.get_recommendations(farm, str(current_user.id))

    if not prediction:
        # No prediction yet — trigger one automatically
        from app.schemas.schemas import PredictRequest as PR
        req = PR(farm_id=farm_id)
        prediction = await pred_service.run_prediction(req, str(current_user.id), farm)

    # Determine urgency and secondary recommendations
    score = float(prediction.stress_score)
    level = prediction.stress_level

    if level == "critical":
        urgency = "immediate"
        water_need = float(farm.area_hectares or 1) * 55  # 55L per hectare for critical
        secondary = [
            "Inspect the north-east sector first — highest stress concentration likely.",
            "Check irrigation system for blockages or failures.",
            "Consider splitting irrigation into 2 sessions to maximize absorption.",
            "Monitor NDVI daily until stress returns to healthy range.",
        ]
    elif level == "moderate":
        urgency = "within_48h"
        water_need = float(farm.area_hectares or 1) * 30
        secondary = [
            "Rain forecast check recommended — delay if >5mm expected within 24h.",
            "Focus irrigation on the western sector showing lower NDVI readings.",
            "Schedule next satellite analysis in 3 days.",
            "Ensure drainage channels are clear to avoid waterlogging.",
        ]
    else:
        urgency = "monitor"
        water_need = float(farm.area_hectares or 1) * 10
        secondary = [
            "Maintain current irrigation schedule.",
            "Next full analysis recommended in 7 days.",
            "Consider reducing irrigation frequency if rainfall is forecast.",
            "Vegetation index is healthy — no immediate action required.",
        ]

    next_due = (datetime.now(timezone.utc) + timedelta(days=3)).strftime("%Y-%m-%d")

    return RecommendationResponse(
        farm_id=farm_id,
        farm_name=farm.name,
        stress_level=level,
        stress_score=score,
        confidence=float(prediction.confidence),
        primary_recommendation=prediction.recommendation,
        secondary_recommendations=secondary,
        urgency=urgency,
        estimated_water_need=round(water_need, 0),
        next_prediction_due=next_due,
        predicted_at=prediction.predicted_at,
    )
