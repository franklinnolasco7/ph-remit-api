# PH Remittance Rates API

Free API for comparing live remittance rates to the Philippines. Get real-time exchange rates from 6-8 providers. Sort by best deal, view fees and delivery times.

## Features

- 6-8 remittance providers sorted by best deal
- Shows exchange rates, fees, markup %, delivery times
- 5-minute caching
- REST API with JSON responses
- Type-checked and linted

## Quick Start

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for interactive API docs.

## API Endpoint

```
GET /api/v1/rates?source=USD&target=PHP&amount=500
```

### Query Parameters

| Parameter      | Type   | Required | Description                               |
| -------------- | ------ | -------- | ----------------------------------------- |
| source         | string | Yes      | Source currency code (e.g., "USD", "GBP") |
| target         | string | Yes      | Target currency code (e.g., "PHP", "EUR") |
| amount         | float  | No       | Amount to send (default: 100)             |
| source_country | string | No       | ISO 3166-1 Alpha-2 source country code    |
| target_country | string | No       | ISO 3166-1 Alpha-2 target country code    |

### Response Example

```json
{
  "success": true,
  "timestamp": "2025-05-01T12:00:00Z",
  "source_currency": "USD",
  "target_currency": "PHP",
  "amount": 500,
  "mid_market_rate": 61.33,
  "providers": [
    {
      "name": "Instarem",
      "alias": "instarem",
      "rate": 60.681,
      "fee": 0.0,
      "received_amount": 30340.5,
      "markup_percent": 1.06,
      "delivery_time": "Varies by provider",
      "logo_url": "https://..."
    },
    {
      "name": "Moneygram",
      "alias": "moneygram",
      "rate": 60.76,
      "fee": 0.0,
      "received_amount": 30259.34,
      "markup_percent": 0.93,
      "delivery_time": "Varies by provider",
      "logo_url": "https://..."
    },
    {
      "name": "Wise",
      "alias": "wise",
      "rate": 61.286,
      "fee": 4.99,
      "received_amount": 30041.54,
      "markup_percent": 0.07,
      "delivery_time": "14h3m24s",
      "logo_url": "https://..."
    }
  ],
  "best_deal": {
    "provider": "Instarem",
    "received_amount": 30340.5,
    "savings_vs_worst": 1316.08
  }
}
```

## Environment Variables

| Variable          | Default                      | Required | Description                      |
| ----------------- | ---------------------------- | -------- | -------------------------------- |
| WISE_API_BASE_URL | https://api.transferwise.com | No       | Wise API base URL                |
| WISE_API_KEY      | -                            | No       | API key for authenticated access |
| CACHE_TTL_SECONDS | 300                          | No       | Cache TTL in seconds             |
| CORS_ORIGINS      | \*                           | No       | Allowed CORS origins             |

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run linter
ruff check .

# Run type checker
mypy app/

# Run tests
pytest tests/ -v
```

## Related Documentation

- [Wise Comparison API Docs](docs/wise-comparison-api.md) - Data source details

## License

MIT
