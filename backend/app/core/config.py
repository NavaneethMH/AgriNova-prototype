"""
AgriNova Application Configuration
Centralized settings management using Pydantic Settings.
All values are loaded from environment variables or .env file.
"""
from typing import List
from pydantic import field_validator, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- Application ----
    APP_NAME: str = "AgriNova"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # ---- Security ----
    SECRET_KEY: str = "change-this-in-production-must-be-at-least-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ---- Database ----
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "agrinova"
    DB_USER: str = "agrinova_user"
    DB_PASSWORD: str = "agrinova_password"
    DATABASE_URL: str = "postgresql+asyncpg://agrinova_user:agrinova_password@localhost:5432/agrinova"
    LOCAL_DATABASE_URL: str = "sqlite+aiosqlite:///./agrinova.db"

    # ---- CORS ----
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:80",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # ---- OpenWeather ----
    OPENWEATHER_API_KEY: str = ""
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5"

    # ---- Google Earth Engine ----
    GEE_SERVICE_ACCOUNT_EMAIL: str = ""
    GEE_CREDENTIALS_PATH: str = "./earth-engine/gee_credentials.json"
    GEE_PROJECT_ID: str = ""
    GEE_USE_SIMULATION: bool = True

    # ---- Redis ----
    REDIS_URL: str = "redis://localhost:6379/0"

    # ---- Rate Limiting ----
    RATE_LIMIT_PER_MINUTE: int = 60

    # ---- Logging ----
    LOG_LEVEL: str = "INFO"

    # ---- Backend ----
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def gee_enabled(self) -> bool:
        """Returns True if GEE credentials are configured and simulation is disabled."""
        return (
            bool(self.GEE_SERVICE_ACCOUNT_EMAIL)
            and bool(self.GEE_CREDENTIALS_PATH)
            and not self.GEE_USE_SIMULATION
        )

    @property
    def weather_enabled(self) -> bool:
        """Returns True if OpenWeather API key is configured."""
        return bool(self.OPENWEATHER_API_KEY)


# Singleton instance
settings = Settings()
