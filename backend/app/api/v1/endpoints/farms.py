"""
Farm management endpoints — full CRUD with PostGIS polygon support.
"""
from fastapi import APIRouter, HTTPException, status, Query

from app.core.dependencies import CurrentUser, DBSession
from app.services.farm_service import FarmService
from app.schemas.farm import (
    FarmCreateRequest, FarmUpdateRequest, FarmResponse, FarmListResponse
)

router = APIRouter()


def _farm_to_response(farm, boundary_geojson: dict = None) -> FarmResponse:
    """Convert Farm ORM model to FarmResponse schema."""
    return FarmResponse(
        id=str(farm.id),
        user_id=str(farm.user_id),
        name=farm.name,
        description=farm.description,
        crop_type=farm.crop_type,
        soil_type=farm.soil_type,
        planting_date=farm.planting_date,
        harvest_date=farm.harvest_date,
        boundary=boundary_geojson,
        area_hectares=float(farm.area_hectares) if farm.area_hectares else None,
        latitude=float(farm.latitude) if farm.latitude else None,
        longitude=float(farm.longitude) if farm.longitude else None,
        country=farm.country,
        region=farm.region,
        is_active=farm.is_active,
        created_at=farm.created_at,
        updated_at=farm.updated_at,
    )


@router.post(
    "/",
    response_model=FarmResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new farm with boundary polygon",
)
async def create_farm(
    data: FarmCreateRequest,
    current_user: CurrentUser,
    db: DBSession,
):
    """
    Create a new farm.
    - boundary must be a valid GeoJSON Polygon
    - Area is automatically calculated from the polygon
    - Centroid lat/lon is extracted automatically
    """
    farm_service = FarmService(db)
    farm = await farm_service.create(data, str(current_user.id))
    boundary = await farm_service.get_boundary_geojson(farm)
    return _farm_to_response(farm, boundary)


@router.get(
    "/",
    response_model=FarmListResponse,
    summary="List all farms for the current user",
)
async def list_farms(
    current_user: CurrentUser,
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Return paginated list of farms owned by the current user."""
    farm_service = FarmService(db)
    farms, total = await farm_service.get_all_for_user(
        str(current_user.id), page=page, page_size=page_size
    )
    items = []
    for farm in farms:
        boundary = await farm_service.get_boundary_geojson(farm)
        items.append(_farm_to_response(farm, boundary))

    return FarmListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get(
    "/{farm_id}",
    response_model=FarmResponse,
    summary="Get a specific farm by ID",
)
async def get_farm(farm_id: str, current_user: CurrentUser, db: DBSession):
    """Retrieve a farm by UUID. Only accessible by the farm owner."""
    farm_service = FarmService(db)
    farm = await farm_service.get_by_id(farm_id, str(current_user.id))
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")
    boundary = await farm_service.get_boundary_geojson(farm)
    return _farm_to_response(farm, boundary)


@router.put(
    "/{farm_id}",
    response_model=FarmResponse,
    summary="Update a farm",
)
async def update_farm(
    farm_id: str,
    data: FarmUpdateRequest,
    current_user: CurrentUser,
    db: DBSession,
):
    """
    Partially update a farm's details or boundary.
    Only the owner can update their farm.
    """
    farm_service = FarmService(db)
    farm = await farm_service.get_by_id(farm_id, str(current_user.id))
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")

    farm = await farm_service.update(farm, data)
    boundary = await farm_service.get_boundary_geojson(farm)
    return _farm_to_response(farm, boundary)


@router.delete(
    "/{farm_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a farm (soft delete)",
)
async def delete_farm(farm_id: str, current_user: CurrentUser, db: DBSession):
    """
    Soft-delete a farm (marks as inactive, data is preserved).
    Only the owner can delete their farm.
    """
    farm_service = FarmService(db)
    farm = await farm_service.get_by_id(farm_id, str(current_user.id))
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")
    await farm_service.delete(farm)
