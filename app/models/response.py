from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Provider(BaseModel):
    """Individual provider rate data."""

    name: str = Field(..., description="Provider display name")
    alias: str = Field(..., description="Provider slug identifier")
    rate: float | None = Field(default=None, description="Exchange rate (target per source unit)")
    fee: float | None = Field(default=None, description="Transfer fee in source currency")
    received_amount: float | None = Field(default=None, description="Total amount recipient receives")
    markup_percent: float | None = Field(default=None, description="Markup percentage vs mid-market rate")
    delivery_time: str | None = Field(default=None, description="Estimated delivery time")
    logo_url: str | None = Field(default=None, description="Provider logo URL")
    available: bool = Field(default=True, description="Whether provider has live rate data")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Instarem",
                "alias": "instarem",
                "rate": 60.73,
                "fee": 0.00,
                "received_amount": 30363.26,
                "markup_percent": 1.06,
                "delivery_time": None,
                "logo_url": "https://dq8dwmysp7hk1.cloudfront.net/logos/instarem.svg"
            }
        }
    )


class BestDeal(BaseModel):
    """The best deal information."""

    provider: str = Field(..., description="Best provider name")
    received_amount: float = Field(..., description="Amount recipient receives")
    savings_vs_worst: float = Field(..., description="Savings compared to worst option")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "provider": "Instarem",
                "received_amount": 30363.26,
                "savings_vs_worst": 1158.26
            }
        }
    )


class RateResponse(BaseModel):
    """Response schema for /rates endpoint."""

    success: bool = Field(default=True, description="Request success status")
    timestamp: datetime = Field(..., description="Response timestamp")
    source_currency: str = Field(..., description="Source currency code")
    target_currency: str = Field(..., description="Target currency code")
    amount: float = Field(..., description="Amount sent")
    mid_market_rate: float = Field(..., description="Mid-market exchange rate")
    providers: list[Provider] = Field(..., description="List of providers sorted by best deal")
    best_deal: BestDeal = Field(..., description="Best deal information")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "timestamp": "2025-05-01T12:00:00Z",
                "source_currency": "USD",
                "target_currency": "PHP",
                "amount": 500,
                "mid_market_rate": 61.33,
                "providers": [],
                "best_deal": {
                    "provider": "Instarem",
                    "received_amount": 30363.26,
                    "savings_vs_worst": 1158.26
                }
            }
        }
    )


class ErrorResponse(BaseModel):
    """Error response schema."""

    success: bool = Field(default=False, description="Request success status")
    error: str = Field(..., description="Error message")
    detail: str | None = Field(default=None, description="Detailed error information")
