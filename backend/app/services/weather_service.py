"""
Weather service — fetches current and historical weather from OpenWeather API.
Falls back to simulated data if API key is not configured.
"""
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List
import httpx
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.core.config import settings
from app.models.farm import Farm
from app.models.models import WeatherData

logger = structlog.get_logger(__name__)


class WeatherService:
    """Fetches, stores, and retrieves weather data for farms."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_current_for_farm(self, farm: Farm) -> Optional[WeatherData]:
        """Get the most recent weather reading for a farm."""
        result = await self.db.execute(
            select(WeatherData)
            .where(and_(WeatherData.farm_id == farm.id, WeatherData.is_forecast == False))
            .order_by(desc(WeatherData.observed_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_history_for_farm(
        self, farm: Farm, days: int = 7
    ) -> List[WeatherData]:
        """Get historical weather readings for a farm."""
        since = datetime.now(timezone.utc) - timedelta(days=days)
        result = await self.db.execute(
            select(WeatherData)
            .where(
                and_(
                    WeatherData.farm_id == farm.id,
                    WeatherData.is_forecast == False,
                    WeatherData.observed_at >= since,
                )
            )
            .order_by(desc(WeatherData.observed_at))
        )
        return list(result.scalars().all())

    async def fetch_and_store(self, farm: Farm) -> WeatherData:
        """
        Fetch current weather from OpenWeather and store in DB.
        Uses simulated data if API key is not configured.
        """
        if settings.weather_enabled and farm.latitude and farm.longitude:
            weather_data = await self._fetch_from_openweather(farm)
        else:
            weather_data = self._simulate_weather(farm)

        self.db.add(weather_data)
        await self.db.flush()
        await self.db.refresh(weather_data)
        return weather_data

    async def _fetch_from_openweather(self, farm: Farm) -> WeatherData:
        """Fetch real weather data from OpenWeather API."""
        url = f"{settings.OPENWEATHER_BASE_URL}/weather"
        params = {
            "lat": float(farm.latitude),
            "lon": float(farm.longitude),
            "appid": settings.OPENWEATHER_API_KEY,
            "units": "metric",
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

            rain = data.get("rain", {})
            return WeatherData(
                farm_id=farm.id,
                temperature=data["main"]["temp"],
                feels_like=data["main"]["feels_like"],
                humidity=data["main"]["humidity"],
                pressure=data["main"]["pressure"],
                wind_speed=data.get("wind", {}).get("speed"),
                wind_direction=data.get("wind", {}).get("deg"),
                rainfall_1h=rain.get("1h", 0),
                rainfall_24h=rain.get("3h", 0),  # approximation
                cloud_cover=data.get("clouds", {}).get("all"),
                visibility=data.get("visibility"),
                weather_code=data["weather"][0]["id"] if data.get("weather") else None,
                weather_main=data["weather"][0]["main"] if data.get("weather") else None,
                weather_desc=data["weather"][0]["description"] if data.get("weather") else None,
                weather_icon=data["weather"][0]["icon"] if data.get("weather") else None,
                source="openweather",
                observed_at=datetime.now(timezone.utc),
            )
        except Exception as e:
            logger.warning("openweather_fetch_failed", error=str(e), farm_id=str(farm.id))
            return self._simulate_weather(farm)

    def _simulate_weather(self, farm: Farm) -> WeatherData:
        """Generate realistic simulated weather data as fallback."""
        import random
        import math
        # Base temperature varies by latitude (tropical = warmer)
        lat = float(farm.latitude) if farm.latitude else 20.0
        base_temp = 28 - abs(lat) * 0.3
        hour = datetime.now().hour
        # Diurnal temperature variation
        temp = base_temp + 5 * math.sin(math.pi * (hour - 6) / 12)
        humidity = random.uniform(45, 85)
        rainfall = random.choices([0, 0, 0, random.uniform(1, 15)], weights=[7, 7, 7, 1])[0]

        return WeatherData(
            farm_id=farm.id,
            temperature=round(temp, 1),
            feels_like=round(temp - 2, 1),
            humidity=round(humidity, 1),
            pressure=round(random.uniform(1008, 1020), 1),
            wind_speed=round(random.uniform(1, 8), 1),
            wind_direction=round(random.uniform(0, 360), 1),
            rainfall_1h=round(rainfall / 24, 2),
            rainfall_24h=round(rainfall, 2),
            cloud_cover=round(random.uniform(10, 80), 1),
            visibility=round(random.uniform(8000, 15000)),
            weather_main="Partly Cloudy",
            weather_desc="partly cloudy skies",
            weather_icon="02d",
            source="simulation",
            observed_at=datetime.now(timezone.utc),
        )
