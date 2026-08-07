"""
Pydantic schemas for Farm CRUD operations.
Supports GeoJSON polygon input/output.
"""
from datetime import datetime, date
from typing import Optional, List, Any
from pydantic import BaseModel, Field, field_validator
import json


class PolygonGeometry(BaseModel):
    """GeoJSON Polygon geometry."""
    type: str = Field("Polygon", pattern="^Polygon$")
    coordinates: List[List[List[float]]] = Field(
        ..., description="GeoJSON coordinates: [[[lon, lat], ...]]"
    )

    @field_validator("coordinates")
    @classmethod
    def validate_polygon(cls, v: list) -> list:
        if not v or not v[0]:
            raise ValueError("Polygon must have at least one ring")
        ring = v[0]
        if len(ring) < 4:
            raise ValueError("Polygon ring must have at least 4 points (first = last)")
        first, last = ring[0], ring[-1]
        if first != last:
            raise ValueError("Polygon ring must be closed (first point = last point)")
        for point in ring:
            if len(point) != 2:
                raise ValueError("Each coordinate must be [longitude, latitude]")
            lon, lat = point
            if not (-180 <= lon <= 180):
                raise ValueError(f"Longitude {lon} out of range [-180, 180]")
            if not (-90 <= lat <= 90):
                raise ValueError(f"Latitude {lat} out of range [-90, 90]")
        return v


class FarmCreateRequest(BaseModel):
    """Request body to create a new farm."""
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    crop_type: str = Field("other", description="Crop type enum")
    soil_type: str = Field("other", description="Soil type enum")
    planting_date: Optional[date] = None
    harvest_date: Optional[date] = None
    boundary: PolygonGeometry = Field(..., description="GeoJSON Polygon for farm boundary")

    @field_validator("crop_type")
    @classmethod
    def validate_crop_type(cls, v: str) -> str:
        valid = {"corn", "wheat", "soybeans", "rice", "cotton", "sugarcane", "barley", "sorghum", "other"}
        if v not in valid:
            raise ValueError(f"crop_type must be one of: {valid}")
        return v

    @field_validator("soil_type")
    @classmethod
    def validate_soil_type(cls, v: str) -> str:
        valid = {"clay_loam", "sandy_loam", "silt", "loam", "sandy_clay", "silty_clay", "other"}
        if v not in valid:
            raise ValueError(f"soil_type must be one of: {valid}")
        return v


class FarmUpdateRequest(BaseModel):
    """Request body to partially update a farm."""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    crop_type: Optional[str] = None
    soil_type: Optional[str] = None
    planting_date: Optional[date] = None
    harvest_date: Optional[date] = None
    boundary: Optional[PolygonGeometry] = None


class FarmResponse(BaseModel):
    """Farm response with computed fields."""
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    crop_type: str
    soil_type: str
    planting_date: Optional[date] = None
    harvest_date: Optional[date] = None
    boundary: Any  # GeoJSON dict
    area_hectares: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    country: Optional[str] = None
    region: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FarmListResponse(BaseModel):
    """Paginated list of farms."""
    items: List[FarmResponse]
    total: int
    page: int
    page_size: int
