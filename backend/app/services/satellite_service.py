"""
Satellite service — integrates Google Earth Engine or falls back to simulation.
Provides NDVI, NDWI, and heatmap data for farm polygons.
"""
import uuid
import sys
import os
from datetime import datetime, timezone, date, timedelta
from typing import Optional, List
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.core.config import settings
from app.models.farm import Farm
from app.models.models import SatelliteData

logger = structlog.get_logger(__name__)


class SatelliteService:
    """Fetches, computes, and stores NDVI/NDWI satellite data for farms."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_latest_for_farm(self, farm: Farm) -> Optional[SatelliteData]:
        """Get the most recent satellite data for a farm."""
        result = await self.db.execute(
            select(SatelliteData)
            .where(SatelliteData.farm_id == farm.id)
            .order_by(desc(SatelliteData.scene_date))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_history_for_farm(self, farm: Farm, days: int = 30) -> List[SatelliteData]:
        """Get historical satellite records for a farm."""
        since = date.today() - timedelta(days=days)
        result = await self.db.execute(
            select(SatelliteData)
            .where(and_(SatelliteData.farm_id == farm.id, SatelliteData.scene_date >= since))
            .order_by(desc(SatelliteData.scene_date))
        )
        return list(result.scalars().all())

    async def fetch_and_store(self, farm: Farm) -> SatelliteData:
        """
        Fetch NDVI/NDWI from GEE or simulation, then store.
        GEE is used when credentials are configured; otherwise simulation is used.
        """
        if settings.gee_enabled:
            sat_data = await self._fetch_from_gee(farm)
        else:
            sat_data = self._simulate_satellite(farm)

        self.db.add(sat_data)
        await self.db.flush()
        await self.db.refresh(sat_data)
        return sat_data

    async def _fetch_from_gee(self, farm: Farm) -> SatelliteData:
        """
        Fetch Sentinel-2 imagery and compute NDVI/NDWI using Google Earth Engine.
        Falls back to simulation on any error.
        """
        try:
            import ee
            # Authenticate with service account
            credentials = ee.ServiceAccountCredentials(
                settings.GEE_SERVICE_ACCOUNT_EMAIL,
                settings.GEE_CREDENTIALS_PATH,
            )
            ee.Initialize(credentials, project=settings.GEE_PROJECT_ID)

            # Build farm boundary as EE geometry
            from geoalchemy2.functions import ST_AsGeoJSON
            from sqlalchemy import select as sa_select
            # Get boundary from DB
            lat = float(farm.latitude) if farm.latitude else 0
            lon = float(farm.longitude) if farm.longitude else 0

            # Define date range (last 30 days, cloud cover < 20%)
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            geometry = ee.Geometry.Point([lon, lat]).buffer(1000)  # 1km buffer

            # Sentinel-2 Surface Reflectance collection
            collection = (
                ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                .filterBounds(geometry)
                .filterDate(str(start_date), str(end_date))
                .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
                .sort("CLOUDY_PIXEL_PERCENTAGE")
            )

            if collection.size().getInfo() == 0:
                logger.warning("no_gee_scenes_found", farm_id=str(farm.id))
                return self._simulate_satellite(farm)

            image = collection.first()
            scene_id = image.id().getInfo()

            # Calculate NDVI = (NIR - Red) / (NIR + Red)
            nir = image.select("B8")
            red = image.select("B4")
            green = image.select("B3")
            ndvi = nir.subtract(red).divide(nir.add(red)).rename("NDVI")

            # Calculate NDWI = (Green - NIR) / (Green + NIR)
            ndwi = green.subtract(nir).divide(green.add(nir)).rename("NDWI")

            # Compute statistics
            ndvi_stats = ndvi.reduceRegion(
                reducer=ee.Reducer.mean().combine(ee.Reducer.minMax()).combine(ee.Reducer.stdDev()),
                geometry=geometry,
                scale=10,
                maxPixels=1e9,
            ).getInfo()

            ndwi_stats = ndwi.reduceRegion(
                reducer=ee.Reducer.mean().combine(ee.Reducer.minMax()),
                geometry=geometry,
                scale=10,
                maxPixels=1e9,
            ).getInfo()

            # Get scene date
            scene_date_ms = image.get("system:time_start").getInfo()
            scene_date_dt = datetime.fromtimestamp(scene_date_ms / 1000, tz=timezone.utc).date()

            return SatelliteData(
                farm_id=farm.id,
                ndvi=round(ndvi_stats.get("NDVI_mean", 0), 4),
                ndvi_min=round(ndvi_stats.get("NDVI_min", 0), 4),
                ndvi_max=round(ndvi_stats.get("NDVI_max", 0), 4),
                ndvi_std=round(ndvi_stats.get("NDVI_stdDev", 0), 4),
                ndwi=round(ndwi_stats.get("NDWI_mean", 0), 4),
                ndwi_min=round(ndwi_stats.get("NDWI_min", 0), 4),
                ndwi_max=round(ndwi_stats.get("NDWI_max", 0), 4),
                satellite="Sentinel-2",
                scene_id=scene_id,
                cloud_coverage=0,
                resolution=10.0,
                is_simulated=False,
                scene_date=scene_date_dt,
            )
        except Exception as e:
            logger.warning("gee_fetch_failed", error=str(e), farm_id=str(farm.id))
            return self._simulate_satellite(farm)

    def _simulate_satellite(self, farm: Farm) -> SatelliteData:
        """
        Generate realistic simulated NDVI/NDWI data as fallback.
        Uses farm properties (crop type, season) to create plausible values.
        """
        import random
        import math

        # NDVI ranges by crop type (typical healthy ranges)
        ndvi_ranges = {
            "corn": (0.55, 0.85),
            "wheat": (0.45, 0.75),
            "soybeans": (0.60, 0.88),
            "rice": (0.50, 0.80),
            "cotton": (0.40, 0.70),
            "other": (0.35, 0.75),
        }
        crop = farm.crop_type or "other"
        ndvi_min_base, ndvi_max_base = ndvi_ranges.get(crop, (0.35, 0.75))

        # Seasonal variation based on current month
        month = datetime.now().month
        season_factor = 0.7 + 0.3 * math.sin(math.pi * (month - 3) / 6)

        ndvi_mean = round(random.uniform(ndvi_min_base, ndvi_max_base) * season_factor, 4)
        ndvi_std = round(random.uniform(0.05, 0.15), 4)
        ndvi_min = round(max(-0.1, ndvi_mean - ndvi_std * 2), 4)
        ndvi_max = round(min(0.95, ndvi_mean + ndvi_std * 2), 4)

        # NDWI is correlated with NDVI but offset (water stress indicator)
        ndwi_mean = round(ndvi_mean * 0.6 - 0.1, 4)
        ndwi_min = round(ndwi_mean - 0.15, 4)
        ndwi_max = round(ndwi_mean + 0.15, 4)

        # Generate heatmap pixel data (simplified grid)
        heatmap_size = 10  # 10x10 grid
        ndvi_heatmap = []
        ndwi_heatmap = []
        for i in range(heatmap_size):
            ndvi_row = []
            ndwi_row = []
            for j in range(heatmap_size):
                pixel_ndvi = round(ndvi_mean + random.gauss(0, ndvi_std * 0.5), 4)
                pixel_ndvi = max(-1, min(1, pixel_ndvi))
                ndvi_row.append(pixel_ndvi)
                ndwi_row.append(round(pixel_ndvi * 0.6 - 0.1 + random.gauss(0, 0.03), 4))
            ndvi_heatmap.append(ndvi_row)
            ndwi_heatmap.append(ndwi_row)

        return SatelliteData(
            farm_id=farm.id,
            ndvi=ndvi_mean,
            ndvi_min=ndvi_min,
            ndvi_max=ndvi_max,
            ndvi_std=ndvi_std,
            ndwi=ndwi_mean,
            ndwi_min=ndwi_min,
            ndwi_max=ndwi_max,
            ndvi_heatmap={"grid": ndvi_heatmap, "size": heatmap_size},
            ndwi_heatmap={"grid": ndwi_heatmap, "size": heatmap_size},
            satellite="Sentinel-2 (Simulated)",
            cloud_coverage=round(random.uniform(5, 25), 1),
            resolution=10.0,
            is_simulated=True,
            scene_date=date.today(),
        )
