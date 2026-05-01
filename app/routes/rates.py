import logging
from datetime import datetime
from typing import Any, cast

from fastapi import APIRouter, HTTPException, Query

from app.models.response import BestDeal, ErrorResponse, Provider, RateResponse
from app.services.wise import WiseAPIError, fetch_rates
from app.utils.cache import cache, generate_cache_key

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/rates",
    response_model=RateResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request parameters"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
        503: {"model": ErrorResponse, "description": "External API unavailable"},
    },
    summary="Get remittance rates",
    description="""
    Fetch current exchange rates from multiple remittance providers for a corridor.

    Returns providers sorted by best deal (highest received amount first).
    Results are cached for 5 minutes.
    """,
)
async def get_rates(
    source: str = Query(..., min_length=3, max_length=3, description="Source currency (e.g., USD)"),
    target: str = Query(..., min_length=3, max_length=3, description="Target currency (e.g., PHP)"),
    amount: float = Query(default=100.0, gt=0, description="Amount to send"),
    source_country: str | None = Query(default=None, min_length=2, max_length=2, description="Source country (e.g., US)"),
    target_country: str | None = Query(default=None, min_length=2, max_length=2, description="Target country (e.g., PH)"),
) -> RateResponse:
    """Get remittance rates for a currency corridor."""
    source = source.upper()
    target = target.upper()
    source_country = source_country.upper() if source_country else None
    target_country = target_country.upper() if target_country else None

    cache_key = generate_cache_key(source, target, amount, source_country, target_country)
    cached = await cache.get(cache_key)

    if cached:
        providers = cached.get("providers", [])
        if providers:
            return _build_response(
                source, target, amount,
                providers,
                cached.get("mid_market_rate", 0),
                cached.get("timestamp"),
            )
        await cache.delete(cache_key)

    data = await _fetch_rate_data(source, target, amount, source_country, target_country)
    await cache.set(cache_key, data)

    return _build_response(
        source, target, amount,
        data["providers"],
        data["mid_market_rate"],
        data["timestamp"],
    )


async def _fetch_rate_data(
    source: str,
    target: str,
    amount: float,
    source_country: str | None,
    target_country: str | None,
) -> dict[str, Any]:
    """Fetch rate data from Wise API with proper error handling."""
    try:
        return await fetch_rates(
            source_currency=source,
            target_currency=target,
            amount=amount,
            source_country=source_country,
            target_country=target_country,
        )
    except WiseAPIError as e:
        logger.error(f"Wise API error: {e.message}")
        status = 502 if e.status_code != 503 else 503
        error = "External service unavailable" if status == 503 else "Failed to fetch rates"
        detail = "The Wise API is currently unavailable." if status == 503 else "Failed to fetch exchange rates"
        raise HTTPException(status_code=status, detail={"success": False, "error": error, "detail": detail})
    except Exception:
        logger.exception("Unexpected error fetching rates")
        raise HTTPException(status_code=500, detail={"success": False, "error": "Internal server error", "detail": "An unexpected error occurred"})


def _build_response(
    source: str,
    target: str,
    amount: float,
    providers: list[Provider],
    mid_market_rate: float,
    timestamp: datetime,
) -> RateResponse:
    """Build the rate response."""
    return RateResponse(
        success=True,
        timestamp=timestamp,
        source_currency=source,
        target_currency=target,
        amount=amount,
        mid_market_rate=mid_market_rate,
        providers=providers,
        best_deal=_calculate_best_deal(providers),
    )


def _calculate_best_deal(providers: list[Provider]) -> BestDeal:
    """Calculate the best deal from providers list."""
    available: list[Provider] = [p for p in providers if p.available and p.received_amount is not None]

    if not available:
        return BestDeal(provider="N/A", received_amount=0, savings_vs_worst=0)

    best = available[0]
    worst = available[-1]
    best_received = cast(float, best.received_amount)
    worst_received = cast(float, worst.received_amount)
    return BestDeal(
        provider=best.name,
        received_amount=best_received,
        savings_vs_worst=best_received - worst_received,
    )
