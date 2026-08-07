"""
API v1 router — aggregates all route modules.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, farms, dashboard, weather, satellite, predictions, analytics, notifications

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(farms.router, prefix="/farms", tags=["Farm Management"])
router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
router.include_router(weather.router, prefix="/weather", tags=["Weather"])
router.include_router(satellite.router, prefix="/satellite", tags=["Satellite"])
router.include_router(predictions.router, prefix="/predict", tags=["AI Predictions"])
router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
