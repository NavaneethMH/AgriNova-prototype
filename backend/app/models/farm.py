"""
Farm ORM model with portable boundary storage.
"""
import uuid
from datetime import datetime, timezone, date
from sqlalchemy import String, Boolean, Enum, DateTime, Text, Numeric, Date, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Farm(Base):
    """Represents a farm with a PostGIS polygon boundary."""
    __tablename__ = "farms"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    crop_type: Mapped[str] = mapped_column(
        Enum("corn", "wheat", "soybeans", "rice", "cotton",
             "sugarcane", "barley", "sorghum", "other", name="crop_type"),
        nullable=False, default="other",
    )
    soil_type: Mapped[str] = mapped_column(
        Enum("clay_loam", "sandy_loam", "silt", "loam",
             "sandy_clay", "silty_clay", "other", name="soil_type"),
        nullable=False, default="other",
    )
    planting_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    harvest_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    # GeoJSON polygon serialized as JSON text for backend portability.
    boundary: Mapped[str] = mapped_column(Text, nullable=False)
    area_hectares: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="farms")
    weather_data: Mapped[list["WeatherData"]] = relationship("WeatherData", back_populates="farm", lazy="select")
    satellite_data: Mapped[list["SatelliteData"]] = relationship("SatelliteData", back_populates="farm", lazy="select")
    predictions: Mapped[list["Prediction"]] = relationship("Prediction", back_populates="farm", lazy="select")
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="farm", lazy="select")

    def __repr__(self) -> str:
        return f"<Farm id={self.id} name={self.name}>"
