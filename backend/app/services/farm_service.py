"""
Farm service — CRUD for farms with PostGIS polygon handling.
Converts between GeoJSON and serialized JSON for portable storage.
"""
import json
import uuid
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
import structlog

from app.models.farm import Farm
from app.schemas.farm import FarmCreateRequest, FarmUpdateRequest

logger = structlog.get_logger(__name__)


def geojson_to_wkt(geojson_polygon: dict) -> str:
    """
    Convert a GeoJSON Polygon dict to serialized JSON for storage.
    """
    return json.dumps(geojson_polygon, separators=(",", ":"))


class FarmService:
    """Business logic for farm management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, farm_id: str, user_id: str) -> Optional[Farm]:
        """Get a farm by ID, scoped to the authenticated user."""
        result = await self.db.execute(
            select(Farm).where(
                and_(
                    Farm.id == uuid.UUID(farm_id),
                    Farm.user_id == uuid.UUID(user_id),
                    Farm.is_active == True,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_all_for_user(
        self, user_id: str, page: int = 1, page_size: int = 20
    ) -> tuple[List[Farm], int]:
        """Get paginated list of farms for a user."""
        base_query = select(Farm).where(
            and_(Farm.user_id == uuid.UUID(user_id), Farm.is_active == True)
        )
        # Count
        count_result = await self.db.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total = count_result.scalar_one()
        # Paginated results
        result = await self.db.execute(
            base_query.offset((page - 1) * page_size).limit(page_size)
        )
        farms = result.scalars().all()
        return list(farms), total

    async def create(self, data: FarmCreateRequest, user_id: str) -> Farm:
        """Create a new farm with serialized GeoJSON boundary."""
        boundary_json = geojson_to_wkt(data.boundary.model_dump())
        farm = Farm(
            user_id=uuid.UUID(user_id),
            name=data.name,
            description=data.description,
            crop_type=data.crop_type,
            soil_type=data.soil_type,
            planting_date=data.planting_date,
            harvest_date=data.harvest_date,
            boundary=boundary_json,
        )
        self.db.add(farm)
        await self.db.flush()
        await self.db.refresh(farm)
        logger.info("farm_created", farm_id=str(farm.id), user_id=user_id)
        return farm

    async def update(self, farm: Farm, data: FarmUpdateRequest) -> Farm:
        """Update farm fields (partial update)."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "boundary" and value is not None:
                farm.boundary = geojson_to_wkt(value)
            else:
                setattr(farm, field, value)
        await self.db.flush()
        await self.db.refresh(farm)
        logger.info("farm_updated", farm_id=str(farm.id))
        return farm

    async def delete(self, farm: Farm) -> None:
        """Soft-delete a farm (set is_active=False)."""
        farm.is_active = False
        await self.db.flush()
        logger.info("farm_deleted", farm_id=str(farm.id))

    async def get_boundary_geojson(self, farm: Farm) -> Optional[dict]:
        """Return farm boundary as GeoJSON dict."""
        if farm.boundary is None:
            return None
        if isinstance(farm.boundary, dict):
            return farm.boundary
        if isinstance(farm.boundary, str):
            try:
                return json.loads(farm.boundary)
            except json.JSONDecodeError:
                return None
        return None
