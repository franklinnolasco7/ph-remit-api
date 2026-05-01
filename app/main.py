import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.config import settings
from app.routes.rates import router as rates_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Application lifespan handler for startup/shutdown events."""
    yield
    # Cleanup on shutdown


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    PH Remittance Rates API provides real-time exchange rates from multiple
    remittance providers for the Philippines corridor.

    ## Features
    - Live rates from 8+ remittance providers
    - Sorted by best deal (highest received amount)
    - Includes fees and markup percentages
    - 5-minute caching for performance
    - OpenAPI documentation

    ## Use Cases
    - Build OFW-focused fintech applications
    - Research remittance pricing
    - Compare provider rates programmatically

    ## Data Source
    Powered by Wise Comparison API (updated hourly).
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rates_router, prefix=settings.api_prefix)


@app.get("/", tags=["Root"])
async def root() -> dict[str, Any]:
    """Root endpoint returning API info."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "endpoints": {
            "rates": f"{settings.api_prefix}/rates",
        },
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.app_version}


@app.get("/favicon.ico", tags=["Static"])
async def favicon() -> Response:
    """Favicon placeholder."""
    return Response(status_code=204)
