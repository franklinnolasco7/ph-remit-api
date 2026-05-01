# PH Remit API Roadmap

## Project Overview
Free public API for comparing remittance rates to the Philippines. Uses Wise Comparison API as data source.

## Current Status

### Done ✅
- [x] Project scaffolding with FastAPI
- [x] Basic `/rates` endpoint (supports multiple corridors)
- [x] In-memory caching (5 min TTL) with async-safety
- [x] Test suite (13 tests passing)
- [x] Code quality improvements (ruff + mypy passing)
- [x] Health check endpoint (`/health`)
- [x] API documentation (`/docs`, `/redoc`)
- [x] CI/CD with GitHub Actions
- [x] Render.com deployment config
- [x] Error handling with logging (production-ready)
- [x] Type hints on all functions
- [x] Wise API key support (for authenticated access)

### Known Limitation ⚠️
- Wise public Comparison API returns only 6-8 providers
- Wise website shows 17 providers (authenticated/business API)

---

## Roadmap

### Done ✅
- [x] Deploy config ready (render.yaml with correct API URL)
- [x] Health check endpoint (`/health`)
- [x] API docs (`/docs`, `/redoc`)
- [x] CI/CD pipeline (GitHub Actions)
- [x] 13 tests passing
- [x] Code quality (ruff + mypy passing)
- [x] Error handling with logging
- [x] Multiple corridors via query params

### In Progress
- [ ] **Investigate Wise Platform API** for more providers

### Backlog
- [ ] Add Redis caching (replace in-memory for multi-instance)
- [ ] Add rate limiting
- [ ] Add request logging/monitoring
- [ ] Add request ID tracking
- [ ] OpenAPI spec generation
- [ ] Add fallback provider APIs if available
- [ ] Document provider sources in API response
- [ ] Add webhooks for rate alerts
- [ ] Add historical rate data endpoint
- [ ] Add sender location detection
- [ ] Mobile app or Telegram bot integration
- [ ] Sponsor/API funding model (if costs arise)

---

## Technical Debt

### Done
- [x] Fix remaining deprecation warnings in test file
- [x] Add type hints to all functions

### Backlog
- [ ] Extract cache to dependency injection (for testing)
- [ ] Add integration tests with real API calls
- [ ] Document all API response fields in OpenAPI

---

## Open Questions

1. **Provider count**: Pursue authenticated Wise API for 17 providers?
2. **Caching**: Is in-memory sufficient or need Redis from start?
3. **Monetization**: If costs arise, what's the funding model?

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload

# Run tests
pytest tests/ -v

# Run linting
ruff check .

# Type check
mypy app/

# Deploy to Render
git push main  # CI runs automatically
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/docs` | GET | OpenAPI docs |
| `/redoc` | GET | ReDoc docs |
| `/api/v1/rates` | GET | Get rates (source, target, amount, source_country, target_country) |

### Rate Endpoint Parameters

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `source` | Yes | Source currency (3-letter code) | `USD` |
| `target` | Yes | Target currency (3-letter code) | `PHP` |
| `amount` | No | Amount to send (default: 100) | `500` |
| `source_country` | No | ISO country code | `US` |
| `target_country` | No | ISO country code | `PH` |

### Response Fields

- `success`: Request success status
- `timestamp`: Response timestamp
- `source_currency`: Source currency code
- `target_currency`: Target currency code
- `amount`: Amount sent
- `mid_market_rate`: Mid-market exchange rate
- `providers`: List of providers sorted by best deal
- `best_deal`: Best deal information

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `WISE_API_KEY` | No | - | API key for authenticated Wise API access |
| `CACHE_TTL_SECONDS` | No | `300` | Cache time-to-live in seconds |
| `CORS_ORIGINS` | No | `["*"]` | Allowed CORS origins |

---

## References
- [Wise Comparison API Docs](https://docs.wise.com/api-reference/comparison)
- [Wise Platform API](https://docs.wise.com/api-reference)
- [Render.com Deploy](https://render.com/docs)