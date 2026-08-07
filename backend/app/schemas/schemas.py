"""
Pydantic schemas for weather, satellite, predictions, analytics, and notifications.
"""
from datetime import datetime, date
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field


# ================================================================
# WEATHER SCHEMAS
# ================================================================

class WeatherResponse(BaseModel):
    """Current weather conditions."""
    id: str
    farm_id: str
    temperature: Optional[float] = None
    feels_like: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[float] = None
    rainfall_1h: float = 0
    rainfall_24h: float = 0
    cloud_cover: Optional[float] = None
    weather_main: Optional[str] = None
    weather_desc: Optional[str] = None
    weather_icon: Optional[str] = None
    source: str
    is_forecast: bool = False
    observed_at: datetime
    fetched_at: datetime

    model_config = {"from_attributes": True}


class WeatherHistoryResponse(BaseModel):
    """Historical weather data list."""
    items: List[WeatherResponse]
    total: int
    farm_id: str


# ================================================================
# SATELLITE SCHEMAS
# ================================================================

class SatelliteDataResponse(BaseModel):
    """Satellite imagery indices response."""
    id: str
    farm_id: str
    ndvi: Optional[float] = None
    ndvi_min: Optional[float] = None
    ndvi_max: Optional[float] = None
    ndwi: Optional[float] = None
    ndwi_min: Optional[float] = None
    ndwi_max: Optional[float] = None
    ndvi_heatmap: Optional[Any] = None
    ndwi_heatmap: Optional[Any] = None
    satellite: str = "Sentinel-2"
    scene_id: Optional[str] = None
    cloud_coverage: Optional[float] = None
    is_simulated: bool = False
    scene_date: date
    fetched_at: datetime

    model_config = {"from_attributes": True}


# ================================================================
# PREDICTION SCHEMAS
# ================================================================

class PredictRequest(BaseModel):
    """Request to run an AI moisture stress prediction."""
    farm_id: str = Field(..., description="Farm UUID")
    ndvi: Optional[float] = Field(None, ge=-1.0, le=1.0)
    ndwi: Optional[float] = Field(None, ge=-1.0, le=1.0)
    temperature: Optional[float] = Field(None, ge=-50, le=60)
    humidity: Optional[float] = Field(None, ge=0, le=100)
    rainfall: Optional[float] = Field(None, ge=0)


class PredictionResponse(BaseModel):
    """AI prediction result."""
    id: str
    farm_id: str
    stress_level: str  # "healthy" | "moderate" | "critical"
    stress_score: float  # 0-100
    confidence: float  # 0-100
    recommendation: str
    detailed_analysis: Optional[Dict[str, Any]] = None
    healthy_pct: Optional[float] = None
    moderate_pct: Optional[float] = None
    critical_pct: Optional[float] = None
    model_version: str
    ndvi: Optional[float] = None
    ndwi: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    rainfall: Optional[float] = None
    predicted_at: datetime

    model_config = {"from_attributes": True}


class RecommendationResponse(BaseModel):
    """AI-driven irrigation/management recommendations."""
    farm_id: str
    farm_name: str
    stress_level: str
    stress_score: float
    confidence: float
    primary_recommendation: str
    secondary_recommendations: List[str]
    urgency: str  # "immediate" | "within_48h" | "monitor" | "none"
    estimated_water_need: Optional[float] = None  # liters per hectare
    next_prediction_due: str
    predicted_at: datetime


# ================================================================
# ANALYTICS SCHEMAS
# ================================================================

class AnalyticsDataPoint(BaseModel):
    """Single analytics chart data point."""
    date: str
    ndvi: Optional[float] = None
    ndwi: Optional[float] = None
    stress_score: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    rainfall: Optional[float] = None


class AnalyticsResponse(BaseModel):
    """Historical analytics for charts."""
    farm_id: str
    farm_name: str
    period: str  # "weekly" | "monthly" | "all"
    data_points: List[AnalyticsDataPoint]
    summary: Dict[str, Any]


# ================================================================
# DASHBOARD SCHEMA
# ================================================================

class DashboardKPI(BaseModel):
    """A single KPI metric for the dashboard."""
    label: str
    value: Any
    unit: Optional[str] = None
    trend: Optional[str] = None  # "+2.4% vs last cycle"
    trend_direction: Optional[str] = None  # "up" | "down" | "stable"


class DashboardResponse(BaseModel):
    """Aggregated dashboard data."""
    user_name: str
    total_farms: int
    total_area_hectares: float
    kpis: List[DashboardKPI]
    latest_prediction: Optional[PredictionResponse] = None
    latest_weather: Optional[WeatherResponse] = None
    latest_satellite: Optional[SatelliteDataResponse] = None
    recent_notifications: List["NotificationResponse"]
    farms_summary: List[Dict[str, Any]]


# ================================================================
# NOTIFICATION SCHEMAS
# ================================================================

class NotificationResponse(BaseModel):
    """Notification response."""
    id: str
    user_id: str
    farm_id: Optional[str] = None
    title: str
    message: str
    type: str
    priority: str
    action_label: Optional[str] = None
    action_url: Optional[str] = None
    data: Dict[str, Any] = {}
    is_read: bool
    read_at: Optional[datetime] = None
    is_dismissed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    """List of notifications with unread count."""
    items: List[NotificationResponse]
    total: int
    unread_count: int


# Update forward reference
DashboardResponse.model_rebuild()
