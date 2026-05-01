import asyncio
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

from app.config import settings


class SimpleCache:
    """Simple in-memory cache with TTL support."""

    def __init__(self, default_ttl: int | None = None):
        """
        Initialize the cache.

        Args:
            default_ttl: Default time-to-live in seconds. Defaults to config setting.
        """
        self._cache: dict[str, tuple[Any, datetime]] = {}
        self._default_ttl = default_ttl if default_ttl is not None else settings.cache_ttl_seconds
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Any | None:
        """
        Get a value from cache if it exists and hasn't expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        async with self._lock:
            if key not in self._cache:
                return None

            value, expires_at = self._cache[key]

            if datetime.now(UTC) > expires_at:
                del self._cache[key]
                return None

            return value

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """
        Set a value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds. Defaults to default TTL.
        """
        ttl = ttl or self._default_ttl
        expires_at = datetime.now(UTC) + timedelta(seconds=ttl)
        async with self._lock:
            self._cache[key] = (value, expires_at)

    async def delete(self, key: str) -> None:
        """Delete a key from cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]

    async def clear(self) -> None:
        """Clear all cached values."""
        async with self._lock:
            self._cache.clear()

    async def get_or_set(self, key: str, factory: Callable[[], Any], ttl: int | None = None) -> Any:
        """Get value from cache or compute and cache it."""
        cached = await self.get(key)
        if cached is not None:
            return cached

        value = factory()
        await self.set(key, value, ttl)
        return value


cache = SimpleCache()


def generate_cache_key(
    source: str,
    target: str,
    amount: float,
    source_country: str | None = None,
    target_country: str | None = None,
) -> str:
    """Generate a cache key for rate requests."""
    parts = [source.upper(), target.upper(), str(amount)]
    if source_country:
        parts.append(source_country.upper())
    if target_country:
        parts.append(target_country.upper())
    return ":".join(parts)
