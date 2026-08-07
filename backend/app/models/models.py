"""
Weather data, Satellite data, Prediction, Notification, and RefreshToken ORM models.
"""
import uuid
from datetime import datetime, timezone, date
from sqlalchemy import (
    String, Boolean, Enum, DateTime, Text, Numeric,
    Date, ForeignKey, Integer, BigInteger, Uuid, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class WeatherData(Base):
    """Stores historical and current weather readings for farms."""
    __tablename__ = "weather_data"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True
    )
    temperature: Mapped[float | None] = mapped_column(Numeric(6, 2))
    feels_like: Mapped[float | None] = mapped_column(Numeric(6, 2))
    humidity: Mapped[float | None] = mapped_column(Numeric(5, 2))
    pressure: Mapped[float | None] = mapped_column(Numeric(8, 2))
    wind_speed: Mapped[float | None] = mapped_column(Numeric(7, 2))
    wind_direction: Mapped[float | None] = mapped_column(Numeric(5, 1))
    rainfall_1h: Mapped[float] = mapped_column(Numeric(8, 2), default=0)
    rainfall_24h: Mapped[float] = mapped_column(Numeric(8, 2), default=0)
    cloud_cover: Mapped[float | None] = mapped_column(Numeric(5, 2))
    visibility: Mapped[float | None] = mapped_column(Numeric(10, 2))
    uv_index: Mapped[float | None] = mapped_column(Numeric(4, 1))
    weather_code: Mapped[int | None] = mapped_column(Integer)
    weather_main: Mapped[str | None] = mapped_column(String(100))
    weather_desc: Mapped[str | None] = mapped_column(String(255))
    weather_icon: Mapped[str | None] = mapped_column(String(20))
    source: Mapped[str] = mapped_column(String(50), default="openweather")
    is_forecast: Mapped[bool] = mapped_column(Boolean, default=False)
    forecast_hours: Mapped[int | None] = mapped_column(Integer)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    farm: Mapped["Farm"] = relationship("Farm", back_populates="weather_data")


class SatelliteData(Base):
    """Stores NDVI, NDWI, and raw band data from satellite imagery."""
    __tablename__ = "satellite_data"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ndvi: Mapped[float | None] = mapped_column(Numeric(6, 4))
    ndvi_min: Mapped[float | None] = mapped_column(Numeric(6, 4))
    ndvi_max: Mapped[float | None] = mapped_column(Numeric(6, 4))
    ndvi_std: Mapped[float | None] = mapped_column(Numeric(6, 4))
    ndwi: Mapped[float | None] = mapped_column(Numeric(6, 4))
    ndwi_min: Mapped[float | None] = mapped_column(Numeric(6, 4))
    ndwi_max: Mapped[float | None] = mapped_column(Numeric(6, 4))
    band_red: Mapped[float | None] = mapped_column(Numeric(8, 4))
    band_nir: Mapped[float | None] = mapped_column(Numeric(8, 4))
    band_green: Mapped[float | None] = mapped_column(Numeric(8, 4))
    band_swir: Mapped[float | None] = mapped_column(Numeric(8, 4))
    ndvi_heatmap: Mapped[dict | None] = mapped_column(JSON)
    ndwi_heatmap: Mapped[dict | None] = mapped_column(JSON)
    satellite: Mapped[str] = mapped_column(String(50), default="Sentinel-2")
    scene_id: Mapped[str | None] = mapped_column(String(255))
    cloud_coverage: Mapped[float | None] = mapped_column(Numeric(5, 2))
    resolution: Mapped[float | None] = mapped_column(Numeric(6, 1))
    is_simulated: Mapped[bool] = mapped_column(Boolean, default=False)
    scene_date: Mapped[date] = mapped_column(Date, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    farm: Mapped["Farm"] = relationship("Farm", back_populates="satellite_data")


class Prediction(Base):
    """Stores AI moisture stress predictions with input features and outputs."""
    __tablename__ = "predictions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Input features
    ndvi: Mapped[float | None] = mapped_column(Numeric(6, 4))
    ndwi: Mapped[float | None] = mapped_column(Numeric(6, 4))
    temperature: Mapped[float | None] = mapped_column(Numeric(6, 2))
    humidity: Mapped[float | None] = mapped_column(Numeric(5, 2))
    rainfall: Mapped[float | None] = mapped_column(Numeric(8, 2))
    # Outputs
    stress_level: Mapped[str] = mapped_column(
        Enum("healthy", "moderate", "critical", name="stress_level"), nullable=False
    )
    stress_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    confidence: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    detailed_analysis: Mapped[dict | None] = mapped_column(JSON)
    healthy_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))
    moderate_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))
    critical_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))
    model_version: Mapped[str] = mapped_column(String(50), default="v1.0")
    model_type: Mapped[str] = mapped_column(String(100), default="RandomForestClassifier")
    predicted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    farm: Mapped["Farm"] = relationship("Farm", back_populates="predictions")
    user: Mapped["User"] = relationship("User", back_populates="predictions")


class Notification(Base):
    """In-app notifications for users."""
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    farm_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("farms.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(
        Enum("moisture_stress", "weather_alert", "irrigation_due",
             "satellite_update", "ai_recommendation", "system",
             name="notification_type"),
        nullable=False, default="system",
    )
    priority: Mapped[str] = mapped_column(
        Enum("low", "medium", "high", "critical", name="notification_priority"),
        nullable=False, default="medium",
    )
    action_label: Mapped[str | None] = mapped_column(String(100))
    action_url: Mapped[str | None] = mapped_column(String(500))
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_dismissed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    dismissed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship("User", back_populates="notifications")
    farm: Mapped["Farm"] = relationship("Farm", back_populates="notifications")


class RefreshToken(Base):
    """Stores refresh tokens for JWT token rotation."""
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")
