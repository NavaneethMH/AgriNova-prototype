"""Models package — import all models here for Alembic to discover."""
from app.models.user import User
from app.models.farm import Farm
from app.models.models import WeatherData, SatelliteData, Prediction, Notification, RefreshToken

__all__ = ["User", "Farm", "WeatherData", "SatelliteData", "Prediction", "Notification", "RefreshToken"]
