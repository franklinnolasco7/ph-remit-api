from datetime import UTC, datetime
from typing import Any, cast

import httpx

from app.config import settings
from app.models.response import Provider


class WiseAPIError(Exception):
    """Exception raised for Wise API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class WiseClient:
    """Client for interacting with Wise Comparison API."""

    def __init__(self) -> None:
        self.base_url = settings.wise_api_base_url
        self.endpoint = "/v4/comparisons"

    def _build_params(
        self,
        source_currency: str,
        target_currency: str,
        amount: float,
        source_country: str | None = None,
        target_country: str | None = None,
    ) -> dict[str, Any]:
        """Build query parameters for Wise API."""
        params: dict[str, Any] = {
            "sourceCurrency": source_currency.upper(),
            "targetCurrency": target_currency.upper(),
            "sendAmount": amount,
        }
        if source_country:
            params["sourceCountry"] = source_country.upper()
        if target_country:
            params["targetCountry"] = target_country.upper()
        return params

    async def get_comparison(
        self,
        source_currency: str,
        target_currency: str,
        amount: float,
        source_country: str | None = None,
        target_country: str | None = None,
    ) -> dict[str, Any]:
        """Fetch comparison data from Wise API."""
        params = self._build_params(
            source_currency, target_currency, amount, source_country, target_country
        )

        headers: dict[str, str] = {}
        if settings.wise_api_key:
            headers["Authorization"] = f"Bearer {settings.wise_api_key}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.base_url}{self.endpoint}",
                    params=params,
                    headers=headers,
                )
                response.raise_for_status()
                return cast(dict[str, Any], response.json())
            except httpx.HTTPStatusError as e:
                raise WiseAPIError(
                    f"Wise API returned {e.response.status_code}: {e.response.text}",
                    status_code=e.response.status_code,
                ) from e
            except httpx.RequestError as e:
                raise WiseAPIError(f"Failed to connect to Wise API: {str(e)}") from e

    def _extract_logo_url(self, provider_data: dict[str, Any]) -> str | None:
        """Extract logo URL from provider data."""
        logos = provider_data.get("logos", {})
        normal_logos = cast(dict[str, str], logos.get("normal", {}))
        return normal_logos.get("pngUrl") or normal_logos.get("svgUrl")

    def _create_provider(self, provider_data: dict[str, Any]) -> Provider | None:
        """Create Provider object from raw provider data."""
        quotes = provider_data.get("quotes", [])
        if not quotes:
            return None

        quote = cast(dict[str, Any], quotes[0])
        return Provider(
            name=provider_data.get("name", "Unknown"),
            alias=provider_data.get("alias", "unknown"),
            rate=quote.get("rate", 0),
            fee=quote.get("fee", 0),
            received_amount=quote.get("receivedAmount", 0),
            markup_percent=quote.get("markup", 0),
            delivery_time=self._parse_delivery(quote),
            logo_url=self._extract_logo_url(provider_data),
        )

    def parse_providers(self, data: dict[str, Any]) -> list[Provider]:
        """Parse Wise API response into Provider objects."""
        providers: list[Provider] = []

        if data and data.get("providers"):
            for p in data["providers"]:
                provider = self._create_provider(p)
                if provider:
                    providers.append(provider)

        providers.sort(key=lambda p: p.received_amount or 0, reverse=True)
        return providers

    def _find_mid_market_quote(self, data: dict[str, Any]) -> dict[str, Any] | None:
        """Find the mid-market rate quote from raw data."""
        providers = data.get("providers", [])
        for provider in providers:
            quotes = provider.get("quotes", [])
            for quote in quotes:
                if quote.get("isConsideredMidMarketRate"):
                    return cast(dict[str, Any], quote)
        return None

    def _calculate_mid_market_from_best(self, data: dict[str, Any]) -> float:
        """Calculate mid-market rate from best available rate."""
        try:
            providers = data.get("providers", [])
            if not providers or not providers[0].get("quotes"):
                return 0
            quote = cast(dict[str, Any], providers[0]["quotes"][0])
            rate: float = quote.get("rate", 0)
            markup: float = quote.get("markup", 0)
            return rate / (1 + markup / 100) if markup > 0 else rate
        except (IndexError, TypeError):
            return 0

    def get_mid_market_rate(self, data: dict[str, Any]) -> float:
        """Extract mid-market rate from Wise API response."""
        if not data:
            return 0

        quote = self._find_mid_market_quote(data)
        if quote:
            return cast(float, quote.get("rate", 0))

        return self._calculate_mid_market_from_best(data)

    @staticmethod
    def _parse_delivery(quote: dict[str, Any]) -> str | None:
        """Parse delivery time from quote."""
        delivery = quote.get("deliveryEstimation", {})
        duration = delivery.get("duration")

        if not duration:
            return "Varies by provider"

        min_time = duration.get("min")
        max_time = duration.get("max")

        if min_time and max_time:
            def format_time(t: str) -> str:
                return t.replace("PT", "").lower()
            return format_time(min_time) if min_time == max_time else f"{format_time(min_time)} to {format_time(max_time)}"
        elif min_time:
            return f"From {min_time.replace('PT', '').lower()}"
        elif max_time:
            return f"Up to {max_time.replace('PT', '').lower()}"

        return "Varies by provider"


async def fetch_rates(
    source_currency: str,
    target_currency: str,
    amount: float,
    source_country: str | None = None,
    target_country: str | None = None,
) -> dict[str, Any]:
    """Fetch and parse rates from Wise API."""
    client = WiseClient()
    data = await client.get_comparison(
        source_currency=source_currency,
        target_currency=target_currency,
        amount=amount,
        source_country=source_country,
        target_country=target_country,
    )

    return {
        "providers": client.parse_providers(data),
        "mid_market_rate": client.get_mid_market_rate(data),
        "timestamp": datetime.now(UTC),
    }
