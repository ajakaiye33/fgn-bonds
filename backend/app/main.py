"""
FGN Savings Bond API - FastAPI Backend

REST API for Federal Government of Nigeria Savings Bond subscription
form submission, PDF generation, and admin dashboard.

Author: Hedgar Ajakaiye
License: MIT
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import init_db
from .logging_config import configure_logging
from .middleware import RequestLoggingMiddleware
from .routers import admin, applications, auth

settings = get_settings()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    configure_logging(
        json_format=settings.log_json or settings.is_production,
        log_level=settings.log_level,
    )
    logger.info(
        "Starting application",
        app_name=settings.app_name,
        environment=settings.environment,
    )

    # Initialize database
    init_db()
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info("Shutting down application")


app = FastAPI(
    title=settings.app_name,
    description="API for FGN Savings Bond Subscription Application",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs" if not settings.is_production else None,
    redoc_url="/api/redoc" if not settings.is_production else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Include routers
app.include_router(applications.router, prefix="/api", tags=["Applications"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {"status": "healthy", "app": settings.app_name}


@app.get("/api/constants")
async def get_constants():
    """Return form constants (banks, categories, tenors, titles)."""
    from .utils.constants import (
        BANKS,
        INVESTOR_CATEGORIES,
        MONTHS,
        TENORS,
        TITLES,
    )

    return {
        "banks": BANKS,
        "investor_categories": INVESTOR_CATEGORIES,
        "months": MONTHS,
        "tenors": TENORS,
        "titles": TITLES,
    }
