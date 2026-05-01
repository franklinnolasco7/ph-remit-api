"""Tests for PH Remittance Rates API."""
from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.response import Provider

client = TestClient(app)


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_returns_api_info(self):
        """Root endpoint should return API information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self):
        """Health endpoint should return healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestRatesEndpoint:
    """Tests for /rates endpoint."""

    def test_rates_endpoint_exists(self):
        """The rates endpoint should exist."""
        response = client.get("/api/v1/rates?source=USD&target=PHP&amount=500")
        # Will fail until we mock the Wise API, but tests structure
        assert response.status_code in [200, 500, 502, 503]

    def test_rates_requires_source(self):
        """Rates endpoint should require source parameter."""
        response = client.get("/api/v1/rates?target=PHP")
        assert response.status_code == 422

    def test_rates_requires_target(self):
        """Rates endpoint should require target parameter."""
        response = client.get("/api/v1/rates?source=USD")
        assert response.status_code == 422

    def test_rates_validates_currency_codes(self):
        """Rates endpoint should validate currency codes."""
        response = client.get("/api/v1/rates?source=INVALID&target=PHP")
        assert response.status_code == 422

    def test_rates_validates_amount(self):
        """Rates endpoint should validate amount is positive."""
        response = client.get("/api/v1/rates?source=USD&target=PHP&amount=-100")
        assert response.status_code == 422

    @patch("app.routes.rates.fetch_rates")
    def test_rates_returns_providers(self, mock_fetch):
        """Rates endpoint should return providers."""
        mock_fetch.return_value = {
            "providers": [
                Provider(
                    name="Instarem",
                    alias="instarem",
                    rate=60.73,
                    fee=0.00,
                    received_amount=30363.26,
                    markup_percent=1.06,
                    delivery_time=None,
                    logo_url="https://example.com/logo.png",
                ),
                Provider(
                    name="Wise",
                    alias="wise",
                    rate=61.33,
                    fee=4.59,
                    received_amount=30383.50,
                    markup_percent=0.0,
                    delivery_time="PT1S",
                    logo_url="https://example.com/wise.png",
                ),
            ],
            "mid_market_rate": 61.33,
            "timestamp": datetime.now(UTC),
        }

        response = client.get("/api/v1/rates?source=USD&target=PHP&amount=500")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert "best_deal" in data
        assert data["source_currency"] == "USD"
        assert data["target_currency"] == "PHP"


class TestCache:
    """Tests for cache functionality."""

    @pytest.mark.asyncio
    async def test_cache_set_and_get(self):
        """Cache should store and retrieve values."""
        from app.utils.cache import SimpleCache

        cache = SimpleCache(default_ttl=60)
        await cache.set("test_key", "test_value")
        result = await cache.get("test_key")
        assert result == "test_value"

    @pytest.mark.asyncio
    async def test_cache_expiry(self):
        """Cache should expire values after TTL."""
        from app.utils.cache import SimpleCache

        cache = SimpleCache(default_ttl=0)  # Immediate expiry
        await cache.set("test_key", "test_value")
        result = await cache.get("test_key")
        assert result is None

    @pytest.mark.asyncio
    async def test_cache_delete(self):
        """Cache should delete values."""
        from app.utils.cache import SimpleCache

        cache = SimpleCache(default_ttl=60)
        await cache.set("test_key", "test_value")
        await cache.delete("test_key")
        result = await cache.get("test_key")
        assert result is None


class TestWiseClient:
    """Tests for Wise API client."""

    def test_parse_providers_sorts_by_received_amount(self):
        """Providers should be sorted by received amount (best first)."""
        from app.services.wise import WiseClient

        client = WiseClient()
        mock_data = {
            "providers": [
                {
                    "name": "Instarem",
                    "alias": "instarem",
                    "quotes": [{"receivedAmount": 1000, "rate": 1, "fee": 0, "markup": 5}],
                    "logos": {},
                },
                {
                    "name": "Remitly",
                    "alias": "remitly",
                    "quotes": [{"receivedAmount": 2000, "rate": 1, "fee": 0, "markup": 2}],
                    "logos": {},
                },
            ]
        }

        providers = client.parse_providers(mock_data)
        # Available providers sorted by received_amount descending
        assert providers[0].name == "Remitly"
        assert providers[1].name == "Instarem"
        assert providers[0].available is True
        assert providers[1].available is True

    def test_generate_cache_key(self):
        """Cache key should be consistent for same parameters."""
        from app.utils.cache import generate_cache_key

        key1 = generate_cache_key("USD", "PHP", 500, "US", "PH")
        key2 = generate_cache_key("USD", "PHP", 500, "US", "PH")
        key3 = generate_cache_key("eur", "php", 100, None, None)

        assert key1 == key2
        assert key1 != key3  # Different currencies should differ
