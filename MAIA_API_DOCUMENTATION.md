# XTrillion Core API Quick Start Guide

## Authentication

All API requests require your API key in the header:

```http
X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x
```

## Base URLs

| Environment | URL | Purpose |
|-------------|-----|---------|
| **Production** | `https://api.x-trillion.ai` | Live bond analysis |
| **Development** | `https://api-dev.x-trillion.ai` | Testing and development |

## Available Endpoints

> **Note:** The examples below use `jq` for JSON formatting. Install it with:
> - macOS: `brew install jq`
> - Ubuntu/Debian: `sudo apt-get install jq`
> - Or remove `| jq` from commands for raw output

### 1. Bond Analysis
Analyze individual bonds with full metrics:

```bash
# Bond analysis with comprehensive metrics
curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" \
  -d '{
    "description": "T 3 15/08/52",
    "price": 71.66,
    "settlement_date": "2025-08-01"
  }' | jq

# Portfolio context (simplified field names)
curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" \
  -d '{
    "description": "T 3 15/08/52",
    "price": 71.66,
    "context": "portfolio"
  }' | jq

# Using ISIN
curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" \
  -d '{
    "isin": "US912810TJ79",
    "price": 71.66
  }' | jq

# With parameter overrides (e.g., corporate bond with custom conventions)
curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" \
  -d '{
    "description": "AAPL 3.45 02/09/2029",
    "price": 97.25,
    "overrides": {
      "day_count": "Thirty360.BondBasis",
      "business_convention": "ModifiedFollowing",
      "end_of_month": false
    }
  }' | jq
```

**Response:**
```json
{
  "analytics": {
    "ytm": 4.902780,
    "duration": 16.260414,
    "convexity": 367.199951,
    "spread": 9.277958,
    "z_spread": 3.755931,
    "clean_price": 71.66,
    "dirty_price": 73.043978,
    "accrued_interest": 1.383978,
    "pvbp": 0.116522,
    "macaulay_duration": 16.65902,
    "annual_duration": 15.871346,
    "ytm_annual": 4.962873
  },
  "bond": {
    "description": "T 3 15/08/52",
    "conventions": {
      "day_count": "ActualActual.Bond",
      "frequency": "Semiannual"
    }
  },
  "metadata": {
    "api_version": "v1.2",
    "calculation_engine": "xtrillion_core_quantlib_engine",
    "response_time_ms": 456
  }
}
```

**Tip:** Add `"context": "portfolio"` for a simplified response optimized for portfolio use (see main documentation)

### 2. Flexible Analysis (Array Format)
Simplified array format for quick calculations:

```bash
curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis/flexible" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" \
  -d '["T 3 15/08/52", 71.66, "2025-08-01"]' | jq
```

Array format accepts parameters in any order - automatically detects types

### 3. Portfolio Analysis
Analyze multiple bonds with weighted portfolio metrics:

```bash
# Portfolio analysis
curl -X POST "https://api.x-trillion.ai/api/v1/portfolio/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" \
  -d '{
    "settlement_date": "2025-08-01",
    "data": [
      {
        "description": "T 3 15/08/52",
        "CLOSING PRICE": 71.66,
        "WEIGHTING": 0.4
      },
      {
        "description": "PANAMA, 3.87%, 23-Jul-2060",
        "CLOSING PRICE": 56.60,
        "WEIGHTING": 0.3
      },
      {
        "description": "INDONESIA, 3.85%, 15-Oct-2030",
        "CLOSING PRICE": 90.21,
        "WEIGHTING": 0.3
      }
    ]
  }' | jq
```

**Response includes:**
- Individual bond analytics for each position
- Aggregated portfolio metrics (weighted averages)

### 4. Bond Analysis with Overrides
Override bond parameters for custom calculations:

```bash
# Scenario analysis with different coupon rate (eg a step up bond)
curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" \
  -d '{
    "description": "MSFT 2.4 08/08/2026",
    "price": 96.50,
    "overrides": {
      "coupon": 2.75
    }
  }' | jq

# Override conventions when your data differs from defaults (a variant instead of passing description)
curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" \
  -d '{
    "isin": "US912810TJ79",
    "price": 71.66,
    "overrides": {
      "coupon": 3.125,
      "maturity": "2052-08-15"
    }
  }' | jq
```

**Use cases for overrides:**
- What-if scenarios with different coupons or maturities
- Ensuringi database values with your reference data
- Testing different day count conventions
- Analyzing bonds with non-standard features

### 5. Cash Flow Analysis
Calculate bond cash flows with filtering options:

```bash
# Get all future cash flows
curl -X POST "https://api.x-trillion.ai/api/v1/bond/cashflow" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" \
  -d '{
    "bonds": [
      {
        "description": "T 3 15/08/52",
        "nominal": 1000000
      }
    ],
    "filter": "all",
    "settlement_date": "2025-08-01"
  }' | jq

# Get next cash flow only
curl -X POST "https://api.x-trillion.ai/api/v1/bond/cashflow/next" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" \
  -d '{
    "bonds": [
      {
        "description": "T 3 15/08/52",
        "nominal": 1000000
      }
    ]
  }' | jq

# Get cash flows for next 90 days
curl -X POST "https://api.x-trillion.ai/api/v1/bond/cashflow/period/90" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" \
  -d '{
    "bonds": [
      {
        "description": "T 3 15/08/52",
        "nominal": 1000000
      },
      {
        "description": "AAPL 3.45 02/09/29",
        "nominal": 500000
      }
    ]
  }' | jq
```

**Response includes:**
- Individual cash flows with dates and amounts
- Days from settlement for each cash flow
- Total cash flow summary

### 6. API Version
Get API version information:

```bash
curl "https://api.x-trillion.ai/api/v1/version" \
  -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" | jq
```

## Metrics Explained

| Metric | Field Name | Description |
|--------|------------|-------------|
| Yield to Maturity | `ytm` | Annual return if held to maturity |
| Modified Duration | `duration` | Price sensitivity to yield changes |
| Convexity | `convexity` | Rate of change of duration |
| Spread | `spread` | Basis points over treasury curve |
| Clean Price | `clean_price` | Price without accrued interest |
| Dirty Price | `dirty_price` | Price including accrued interest |
| Accrued Interest | `accrued_interest` | Interest earned since last coupon |
| PVBP | `pvbp` | Price change for 1bp yield change |
| Overrides | `overrides_applied` | Parameters that were overridden |

## Parameter Overrides

The API supports overriding bond parameters for custom calculations. This is useful when you have external bond data or need to test different scenarios.

### Supported Override Fields
- `coupon` - Bond coupon rate (%)
- `maturity` - Maturity date (YYYY-MM-DD format)
- `day_count` - Day count convention (e.g., "ActualActual.Bond", "Thirty360.BondBasis")
- `frequency` - Payment frequency ("Annual", "Semiannual", "Quarterly")
- `business_convention` - Business day convention ("Following", "Unadjusted", etc.)
- `issuer` - Bond issuer name
- `currency` - Currency code
- `face_value` - Face value amount
- `end_of_month` - End of month rule (true/false)
- `first_coupon_date` - First coupon date (YYYY-MM-DD)
- `issue_date` - Issue date (YYYY-MM-DD)

### Override Example
```bash
# Override conventions for a bond where ou might want to base ccls off another bond but with different characteristics.
curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" \
  -d '{
    "isin": "XS1234567890",
    "price": 98.50,
    "overrides": {
      "coupon": 4.125,
      "maturity": "2030-06-15",
      "day_count": "ActualActual.Bond",
      "frequency": "Annual"
    }
  }' | jq
```

The response will indicate which overrides were applied:
```json
{
  "overrides_applied": {
    "coupon": 4.125,
    "maturity": "2030-06-15",
    "day_count": "ActualActual.Bond",
    "frequency": "Annual"
  },
  "override_note": "Calculation performed with 4 parameter override(s)"
}
```

## Python Example

```python
import requests
import json

API_KEY = "gax10_maia_7k9d2m5p8w1e6r4t3y2x"
BASE_URL = "https://api.x-trillion.ai"

def analyze_bond(description, price, settlement_date=None, overrides=None):
    """Analyze a single bond with optional parameter overrides"""
    
    url = f"{BASE_URL}/api/v1/bond/analysis"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    data = {
        "description": description,
        "price": price
    }
    
    if settlement_date:
        data["settlement_date"] = settlement_date
    
    if overrides:
        data["overrides"] = overrides
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        analytics = result["analytics"]
        print(f"Bond: {description}")
        print(f"YTM: {analytics['ytm']:.2f}%")
        print(f"Duration: {analytics['duration']:.2f} years")
        print(f"Spread: {analytics['spread']:.0f} bps")
        
        # Show overrides if applied
        if result.get("overrides_applied"):
            print(f"Overrides: {result['overrides_applied']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())

# Example usage
analyze_bond("T 3 15/08/52", 71.66, "2025-08-01")

# Example with overrides - scenario analysis with different coupon
analyze_bond("AAPL 3.45 02/09/2029", 97.25, 
             overrides={"coupon": 3.75})  # What-if with higher coupon
```

## Performance

All responses include actual processing time in `metadata.response_time_ms`:

```json
{
  "metadata": {
    "response_time_ms": 312
  }
}
```

Typical API processing times:
- **Bond Analysis**: 80-500ms (comprehensive analytics)
- **Portfolio Analysis**: 100-150ms per bond (optimized response format)
- **Cold start**: Up to 8000ms (first request after idle)

## Error Handling

API returns standard HTTP status codes:
- `200` - Success
- `400` - Bad request (invalid parameters)
- `401` - Unauthorized (invalid API key)
- `500` - Server error

Error response format:
```json
{
  "status": "error",
  "code": 401,
  "message": "API key required in X-API-Key header"
}
```

