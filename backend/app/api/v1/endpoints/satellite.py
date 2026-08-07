"""
Satellite data endpoints — NDVI/NDWI retrieval and GEE fetch trigger.
"""
from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy import select, desc

from app.core.dependencies import CurrentUser, DBSession
from app.services.farm_service import FarmService
from app.services.satellite_service import SatelliteService
from app.schemas.schemas import SatelliteDataResponse

router = APIRouter()


def _sat_to_response(s) -> SatelliteDataResponse:
    return SatelliteDataResponse(
        id=str(s.id), farm_id=str(s.farm_id),
        ndvi=float(s.ndvi) if s.ndvi else None,
        ndvi_min=float(s.ndvi_min) if s.ndvi_min else None,
        ndvi_max=float(s.ndvi_max) if s.ndvi_max else None,
        ndwi=float(s.ndwi) if s.ndwi else None,
        ndwi_min=float(s.ndwi_min) if s.ndwi_min else None,
        ndwi_max=float(s.ndwi_max) if s.ndwi_max else None,
        ndvi_heatmap=s.ndvi_heatmap,
        ndwi_heatmap=s.ndwi_heatmap,
        satellite=s.satellite,
        scene_id=s.scene_id,
        cloud_coverage=float(s.cloud_coverage) if s.cloud_coverage else None,
        is_simulated=s.is_simulated,
        scene_date=s.scene_date,
        fetched_at=s.fetched_at,
    )


@router.get(
    "/{farm_id}",
    response_model=SatelliteDataResponse,
    summary="Get the latest satellite NDVI/NDWI data for a farm",
)
async def get_satellite_data(farm_id: str, current_user: CurrentUser, db: DBSession):
    """
    Return the most recent satellite data for a farm.
    If no data exists, triggers a fetch from GEE or simulation.
    """
    farm_service = FarmService(db)
    farm = await farm_service.get_by_id(farm_id, str(current_user.id))
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")

    sat_service = SatelliteService(db)
    data = await sat_service.get_latest_for_farm(farm)

    if not data:
        data = await sat_service.fetch_and_store(farm)

    return _sat_to_response(data)


@router.post(
    "/{farm_id}/fetch",
    response_model=SatelliteDataResponse,
    summary="Trigger a fresh satellite data fetch for a farm",
)
async def fetch_satellite_data(farm_id: str, current_user: CurrentUser, db: DBSession):
    """
    Force a new satellite data fetch from Google Earth Engine.
    Falls back to simulated data if GEE credentials are not configured.
    """
    farm_service = FarmService(db)
    farm = await farm_service.get_by_id(farm_id, str(current_user.id))
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")

    sat_service = SatelliteService(db)
    data = await sat_service.fetch_and_store(farm)
    return _sat_to_response(data)
