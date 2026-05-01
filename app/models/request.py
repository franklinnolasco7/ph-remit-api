from pydantic import BaseModel, Field


class RateRequest(BaseModel):
    """Request schema for /rates endpoint."""

    source: str = Field(..., min_length=3, max_length=3, description="Source currency code (e.g., USD)")
    target: str = Field(..., min_length=3, max_length=3, description="Target currency code (e.g., PHP)")
    amount: float = Field(default=100.0, gt=0, description="Amount to send")
    source_country: str | None = Field(default=None, min_length=2, max_length=2, description="ISO country code (e.g., US)")
    target_country: str | None = Field(default=None, min_length=2, max_length=2, description="ISO country code (e.g., PH)")

    class Config:
        json_schema_extra = {
            "example": {
                "source": "USD",
                "target": "PHP",
                "amount": 500,
                "source_country": "US",
                "target_country": "PH"
            }
        }
