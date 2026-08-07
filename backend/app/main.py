"""
AgriNova Backend - Application Entry Point
FastAPI application with all middleware, routes, and lifecycle events.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import structlog

from app.core.config import settings
from app.core.logging import setup_logging
from app.db import session as db_session
from app.api.v1 import router as api_v1_router
import app.models  # noqa: F401  # ensure all ORM models are registered on Base.metadata

# Setup structured logging
setup_logging()
logger = structlog.get_logger(__name__)

# Rate limiter instance
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    logger.info("AgriNova API starting up", version=settings.APP_VERSION, env=settings.APP_ENV)
    # Create database tables if they don't exist (migrations handle this in prod).
    # If PostgreSQL is unavailable, switch to the local SQLite fallback so the app still runs.
    try:
        active_engine = await db_session.ensure_active_database()
        async with active_engine.begin() as conn:
            await conn.run_sync(db_session.Base.metadata.create_all)
        logger.info("Database connection established", database_url=str(active_engine.url))
    except Exception as exc:
        logger.warning("Database unavailable during startup; running in degraded mode", error=str(exc))
    yield
    # Shutdown
    await db_session.engine.dispose()
    logger.info("AgriNova API shutting down")


def create_application() -> FastAPI:
    """Factory function to create the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        description="AI-powered precision agriculture platform. Smarter Farming from Space.",
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ---- Middleware ----
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # GZip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # ---- Request logging middleware ----
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else "unknown",
        )
        response = await call_next(request)
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
        )
        return response

    # ---- Routes ----
    app.include_router(api_v1_router, prefix="/api/v1")

    # ---- Health check ----
    @app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
        }

    @app.get("/", tags=["Root"])
    async def root():
        return {
            "message": f"Welcome to {settings.APP_NAME} API",
            "tagline": "Smarter Farming from Space",
            "docs": "/docs",
            "health": "/health",
        }

    return app


app = create_application()
