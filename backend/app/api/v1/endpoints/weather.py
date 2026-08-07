"""
Weather endpoints — current conditions, history, and on-demand fetch.
"""
from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy import select, and_, desc

from app.core.dependencies import CurrentUser, DBSession
from app.services.farm_service import FarmService
from app.services.weather_service import WeatherService
from app.schemas.schemas import WeatherResponse, WeatherHistoryResponse

router = APIRouter()


def _weather_to_response(w) -> WeatherResponse:
    return WeatherResponse(
        id=str(w.id), farm_id=str(w.farm_id),
        temperature=float(w.temperature) if w.temperature else None,
        feels_like=float(w.feels_like) if w.feels_like else None,
        humidity=float(w.humidity) if w.humidity else None,
        pressure=float(w.pressure) if w.pressure else None,
        wind_speed=float(w.wind_speed) if w.wind_speed else None,
        wind_direction=float(w.wind_direction) if w.wind_direction else None,
        rainfall_1h=float(w.rainfall_1h) if w.rainfall_1h else 0,
        rainfall_24h=float(w.rainfall_24h) if w.rainfall_24h else 0,
        cloud_cover=float(w.cloud_cover) if w.cloud_cover else None,
        weather_main=w.weather_main,
        weather_desc=w.weather_desc,
        weather_icon=w.weather_icon,
        source=w.source,
        is_forecast=w.is_forecast,
        observed_at=w.observed_at,
        fetched_at=w.fetched_at,
    )


@router.get(
    "/{farm_id}",
    response_model=WeatherResponse,
    summary="Get current weather for a farm",
)
async def get_current_weather(farm_id: str, current_user: CurrentUser, db: DBSession):
    """
    Fetch and return the most recent weather data for a farm.
    If no recent data exists, fetches fresh data from OpenWeather (or simulation).
    """
    farm_service = FarmService(db)
    farm = await farm_service.get_by_id(farm_id, str(current_user.id))
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")

    weather_service = WeatherService(db)
    weather = await weather_service.get_current_for_farm(farm)

    if not weather:
        # No data yet — fetch fresh
        weather = await weather_service.fetch_and_store(farm)

    return _weather_to_response(weather)


@router.post(
    "/{farm_id}/refresh",
    response_model=WeatherResponse,
    summary="Force-refresh weather data for a farm",
)
async def refresh_weather(farm_id: str, current_user: CurrentUser, db: DBSession):
    """Trigger a fresh weather data fetch from OpenWeather API."""
    farm_service = FarmService(db)
    farm = await farm_service.get_by_id(farm_id, str(current_user.id))
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")

    weather_service = WeatherService(db)
    weather = await weather_service.fetch_and_store(farm)
    return _weather_to_response(weather)


@router.get(
    "/{farm_id}/history",
    response_model=WeatherHistoryResponse,
    summary="Get historical weather data for a farm",
)
async def get_weather_history(
    farm_id: str,
    current_user: CurrentUser,
    db: DBSession,
    days: int = Query(7, ge=1, le=90, description="Number of days to look back"),
):
    """Return historical weather readings for a farm (up to 90 days)."""
    farm_service = FarmService(db)
    farm = await farm_service.get_by_id(farm_id, str(current_user.id))
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")

    weather_service = WeatherService(db)
    history = await weather_service.get_history_for_farm(farm, days=days)

    return WeatherHistoryResponse(
        items=[_weather_to_response(w) for w in history],
        total=len(history),
        farm_id=farm_id,
    )
