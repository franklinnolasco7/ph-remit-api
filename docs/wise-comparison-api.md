# Wise Comparison API Documentation

## Overview

The comparison API can be used to request price and speed information about various money transfer providers. This includes not only Wise but other providers in the market.

**Base URL**: `https://api.wise.com`
**Endpoint**: `GET /v4/comparisons`

---

## Price Estimation

The quotes (price and speed) provided by this API are based off of real quotes collected from 3rd party websites. We collect both the advertised exchange rate and fee for each provider for various amounts. When a comparison is requested, we calculate the markup percentage of the collected exchange rate on the mid-market rate at the time of collection. We then apply this markup to the current mid-market rate to provide a realistic estimate of what each provider offers. We collect data for all providers around once per hour to ensure we provide as accurate and up-to-date information as possible.

**Note**: Today, we only provide estimations for FX transactions with a Bank Transfer pay-in and pay-out option. This is important to stress as many providers offer significantly different fees and exchange rates when used debit/credit card, cash etc.

For more details on the data collection process please see the following page: [https://wise.com/gb/compare/disclaimer](https://wise.com/gb/compare/disclaimer)

If you have questions or suspect any data to be inaccurate or incomplete please contact us at: [comparison@wise.com](mailto:comparison@wise.com)

---

## Delivery Estimation

Similar to price, we collect speed data for most (if not all) providers which we have price information for. Many providers display speed estimates to their customers in a number of different ways.

Some examples:
- "The transfer should be complete within 2-5 days"
- "The money should arrive in your account within 48 hours"
- "Should arrive by 26th Aug"
- "Could take up to 4 working days"

The below API intends to model these in a consistent format by providing a minimum and maximum range for all delivery estimations. An estimate that states "up to X" will have "max" set to a duration but "min" as null; "from X" will have "min" set to a duration and "max" as null. Finally, for those providers who offer a specific, point in time estimation (like Wise), the API will surface a duration where "min" and "max" are equal.

---

## Quotes Structure

In order to provide the most flexible and accurate data for clients, we surface a denormalized list of quotes per provider where each quote represents a unique collection of comparison "dimensions".

A single given provider may expose multiple quotes for the same currency route. The most common example is where a provider offers different pricing for two different countries which use the same currency, e.g.:

Provider X:
- GBP EUR 1000 [GB -> ES] fee: 10, rate: 1.5
- GBP EUR 1000 [GB -> DE] fee: 8, rate: 1.5
- GBP EUR 1000 [GB -> FR] fee: 10, rate: 1.35

The same principle applies for speed, i.e. a provider may have different speed estimates for different target countries. Hence, we expose these as discrete quotes, where a quote is a unique combination of route, country, speed and price factors.

A client may choose to reduce this set of quotes down to a single or several quotes in order to display a relevant quote to a given user.

---

## Request Parameters

### Required Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| sourceCurrency | string | ISO 4217 source currency code (e.g., "GBP") |
| targetCurrency | string | ISO 4217 target currency code (e.g., "EUR") |
| sendAmount OR recipientGetsAmount | number | Amount to send OR amount to be received (provide one, not both) |

### Optional Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| sourceCountry | string | Filter by source country (ISO 3166-1 Alpha-2 code) |
| targetCountry | string | Filter by target country (ISO 3166-1 Alpha-2 code) |
| providerCountry | string | Filter by provider country (ISO 3166-1 Alpha-2 code) |
| providerTypes | array | Filter by provider type: "bank", "moneyTransferProvider", "travelMoney" |
| filter | string | Filter by most popular competitors: "POPULAR" |
| numberOfProviders | integer | Number of popular competitors to return (default: 4) |
| providers | string | Filter by specific provider aliases |
| excludePartners | boolean | Exclude Wise's partner banks (default: true) |
| includeWise | boolean | Include Wise data even if exclusionary filters applied |
| payInMethod | string | Change pay-in method for Wise quote only |
| midMarketRate | number | Current mid-market rate between the source and target currency |
| wiseFee | number | Wise's fee, if the Wise quote is known |
| wiseEstimatedDelivery | string | Wise's estimated delivery timestamp |
| wiseQuoteCreatedTime | string | Timestamp when the Wise quote was created |

### Example Request
```
GET https://api.wise.com/v4/comparisons?sourceCurrency=GBP&targetCurrency=EUR&sendAmount=10000
```

---

## Response Structure

```json
{
  "sourceCurrency": "GBP",
  "targetCurrency": "EUR",
  "sourceCountry": null,
  "targetCountry": null,
  "providerCountry": null,
  "providerTypes": ["bank", "moneyTransferProvider"],
  "amount": 10000,
  "amountType": "SEND",
  "providers": [
    {
      "id": 39,
      "alias": "wise",
      "name": "Wise",
      "logos": {
        "normal": {
          "pngUrl": "https://example.com/logo.png",
          "svgUrl": "https://example.com/logo.svg"
        }
      },
      "type": "moneyTransferProvider",
      "partner": false,
      "quotes": [
        {
          "rate": 1.15976,
          "fee": 3.88,
          "receivedAmount": 1155.26,
          "markup": 0.0,
          "deliveryEstimation": {
            "duration": {
              "min": "PT14H",
              "max": "PT14H"
            },
            "providerGivesEstimate": true
          }
        }
      ]
    }
  ]
}
```

### Response Fields
| Field | Type | Description |
|-------|------|-------------|
| sourceCurrency | string | ISO 4217 source currency code |
| targetCurrency | string | ISO 4217 target currency code |
| amount | number | The comparison amount |
| amountType | string | "SEND" or "RECIPIENT_GETS" |
| providerTypes | array | List of provider types included |
| providers | array | List of providers with their estimated quotes |

### Provider Object
| Field | Type | Description |
|-------|------|-------------|
| id | integer | Provider ID |
| alias | string | Provider slug identifier (lowercase) |
| name | string | Provider display name |
| logos | object | URLs to provider logos (svg, png) |
| type | string | "bank", "moneyTransferProvider", or "travelMoney" |
| partner | boolean | Whether provider is a Wise partner |
| quotes | array | Array of estimated quotes |

### Quote Object
| Field | Type | Description |
|-------|------|-------------|
| rate | number | Exchange rate (target per source unit) |
| fee | number | Transfer fee in source currency |
| receivedAmount | number | Total amount recipient receives |
| markup | number | Markup percentage vs mid-market rate |
| deliveryEstimation | object | Delivery time information |

### Delivery Estimation Object
| Field | Type | Description |
|-------|------|-------------|
| duration | object | Contains min/max delivery time (ISO 8601 duration format) |
| duration.min | string | Minimum delivery time (e.g., "PT14H" = 14 hours) |
| duration.max | string | Maximum delivery time |
| providerGivesEstimate | boolean | Whether provider shows estimate on their website |

---

## Data Collection Notes

- Data is collected approximately once per hour from 3rd party websites
- Estimates are based on Bank Transfer pay-in and pay-out options
- Not all providers have delivery time data available
- Some providers may have multiple quotes for the same currency route (different target countries)
- Markup is calculated as: `(collected_rate - mid_market_rate) / mid_market_rate * 100`

---

## References

- API Documentation: [https://docs.wise.com/api-reference/comparison](https://docs.wise.com/api-reference/comparison)
- Comparison Demo: [https://wise.com/gb/compare/?sourceCurrency=GBP&targetCurrency=EUR&sendAmount=1000](https://wise.com/gb/compare/?sourceCurrency=GBP&targetCurrency=EUR&sendAmount=1000)
- Data Collection Disclaimer: [https://wise.com/gb/compare/disclaimer](https://wise.com/gb/compare/disclaimer)