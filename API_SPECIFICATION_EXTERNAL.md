# XTrillion Core Bond Calculation Engine API Specification

**Date:** July 29, 2025  
**Version:** 10.0.0  
**Status:** ✅ Examples Tested & Verified  
**Base URL:** https://api.x-trillion.ai/api/v1

## ⚡ **Performance** (Verified Benchmarks)
- **Bond Analysis**: 80-500ms (comprehensive analytics with 13+ metrics)
- **Portfolio Processing**: 100-150ms per bond
- **Production Optimized**: Embedded databases for consistent performance
- **Scalability**: Linear scaling with portfolio size

*Note: Processing times measured at server. Total response time will include network latency based on your location.*

## 1. Overview

XTrillion's bond analytics engine delivers institutional-grade calculations with a focus on clarity, accuracy, and Bloomberg compatibility. Our philosophy is to offer the essential, high-value metrics used in trading, portfolio management, and risk systems—without the burden of low-utility complexity.

**Key Differentiator**: Our portfolio analysis provides both individual bond analytics AND aggregated portfolio statistics in a single API call, enabling comprehensive risk management and performance monitoring.

This document outlines the technical foundation, calculation suite, authentication requirements, and design principles of our API, which provides programmatic access to XTrillion Core.

### 1.1 What is XTrillion Core?

XTrillion Core is the calculation engine and smart bond parser that powers all XTrillion software. It is designed to be the "brain" of modern fixed income infrastructure.

**Product Structure:**
- **XTrillion Core**: The standalone API product for integration into client systems.
- **XTrillion Platform**: A full-stack fund management solution built on XTrillion Core.

Licensing XTrillion Core gives clients access to the validated engine behind the entire XTrillion ecosystem.

---

## 2. Technical Foundation

### 2.1 QuantLib-Based Professional Engine

- Built on QuantLib, the industry-standard fixed income library.
- Extensively validated to match Bloomberg outputs for US Treasuries and other instruments.
- Solves for day counts, calendars, and business day conventions across markets.

### 2.2 Smart Bond Parser

- **ISIN Recognition**: Auto-identifies bonds and fetches conventions from our database.
- **Description Parsing**: Accurately extracts bond features from text-based input.
- **Convention Mapping**: Maps to correct QuantLib parameters without manual intervention.

#### 2.2.1 Description Parsing Examples

The Smart Bond Parser can identify bonds from various text formats without requiring an ISIN:

**Treasury Shorthand Example:**
```
Input: "T 3 15/08/52"
```

**Parsed Result:**
- Issuer: US Treasury
- Coupon: 3.0%
- Maturity: August 15, 2052
- Frequency: Semi-annual

**Additional Supported Formats:**
- `"UST 3% 08/15/52"` - US Treasury with US date format
- `"TREASURY 3.0 15/08/52"` - Treasury with European date format
- `"US TREASURY N/B, 3%, 15-Aug-2052"` - Full Bloomberg-style description
- `"T 3 15-Aug-52"` - Ticker based notation

---

## 3. Core Calculation Suite

The engine provides comprehensive analytics with accurate compounding basis handling. Field descriptions are provided in a separate `field_descriptions` object for documentation purposes.

### Tier 1: Essential Metrics

| Calculation | API Field | Purpose | Basis |
|-------------|-----------|---------|--------|
| Yield to Maturity | `ytm` | Internal rate of return | Bond convention |
| Modified Duration | `duration` | Price sensitivity to yield | Bond convention |
| Accrued Interest | `accrued_interest` | Days of coupon earned | Bond convention |
| Clean Price | `clean_price` | Price excluding accrued | Market standard |
| Dirty Price | `dirty_price` | Price including accrued | Settlement value |

### Tier 2: Risk & Enhanced Analytics

| Calculation | API Field | Purpose | Basis |
|-------------|-----------|---------|--------|
| Macaulay Duration | `macaulay_duration` | Time-weighted average maturity | Invariant* |
| Annual Modified Duration | `duration_annual` | Annual basis duration | Annual |
| Annual Yield | `ytm_annual` | Annual equivalent yield | Annual |
| Convexity | `convexity` | Duration sensitivity measure | Bond convention |
| Price Value of a Basis Point | `pvbp` | Dollar duration per $1M | Bond convention |

**\* Macaulay Duration Note:** Macaulay duration is invariant to compounding frequency. Both `macaulay_duration` and `annual_macaulay_duration` return the same value, as this represents the weighted-average time to receive cash flows.

### Tier 3: Spread Analytics (Curve Dependent)

| Calculation | API Field | Purpose | Portfolio Aggregation |
|-------------|-----------|---------|----------------------|
| G-Spread | `spread` | Spread over government curve | Weighted average |
| Z-Spread | `z_spread` | Zero-volatility spread | Weighted average |

**Note:** Portfolio analysis provides `portfolio_spread` as a weighted average across all bonds.

---

## 4. API Endpoints & Examples

### 4.0 Quick Reference

| Endpoint | Method | Purpose | Key Features |
|----------|---------|---------|-------------|
| `/health` | GET | System status | Health check, capabilities |
| `/bond/analysis` | POST | Individual bond | Full analytics, risk metrics |
| `/portfolio/analysis` | POST | Portfolio analysis | Individual + aggregated metrics |
| `/bond/analysis/flexible` | POST | Flexible input | Array format with auto-detection |
| `/bond/cashflow` | POST | Cash flow analysis | All, next, or period filtering |
| `/bond/cashflow/next` | POST | Next cash flow | Convenience endpoint |
| `/bond/cashflow/period/<days>` | POST | Period cash flows | Cash flows within N days |

### 4.1 Base URL & Authentication

**Base URL:** `https://api.x-trillion.ai/api/v1`

**Authentication Header:**
```http
X-API-Key: your_api_key_here
```

### 4.2 System Health Check

**Endpoint:** `GET /health`

**Request:**
```bash
curl -s "https://api.x-trillion.ai/api/v1/health" | jq '.'
```

**Response:**
```json
{
  "status": "healthy",
  "version": "10.0.0",
  "service": "XTrillion Core Bond Analytics API",
  "timestamp": "2025-07-29T10:30:00.123456Z",
  "api_status": "operational",
  "capabilities": [
    "Professional bond calculation engine powered by QuantLib",
    "Universal bond parser supporting ISIN and text descriptions",
    "Real-time yield, duration, and accrued interest calculations",
    "Individual bond analytics with institutional-grade precision",
    "Portfolio analysis with weighted-average risk metrics",
    "Multi-database bond lookup with automatic fallback",
    "Comprehensive bond reference database with 4,471+ validated bonds",
    "Automatic Treasury bond detection and parsing",
    "Smart bond description parsing for bonds without ISIN",
    "Enhanced metrics including Macaulay duration, convexity, and PVBP",
    "Bloomberg-compatible calculation accuracy",
    "Validated bond market conventions for institutional use",
    "Portfolio-level risk aggregation and reporting"
  ]
}
```

### 4.3 Individual Bond Analysis

**Endpoint:** `POST /bond/analysis`

#### 4.3a Flexible Input Analysis (NEW)

**Endpoint:** `POST /bond/analysis/flexible`

Accept inputs in any order - automatically detects parameter types:

```bash
# Array format - any order works
curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis/flexible" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '["T 3 15/08/52", 71.66, "2025-07-31"]'

# Or price first
curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis/flexible" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '[71.66, "T 3 15/08/52", "2025-07-31"]'
```

**Standard Bond Calculation:**

**Request:**
```bash
curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "description": "T 3 15/08/52",
    "price": 71.66,
    "settlement_date": "2025-07-30"
  }' | jq '.'
```

**Request with Parameter Overrides:**
```bash
# Scenario analysis with modified coupon rate
curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "description": "AAPL 3.45 02/09/2029",
    "price": 97.25,
    "overrides": {
      "coupon": 3.75
    }
  }' | jq '.'

# Override bond conventions for precise calculations
curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "isin": "XS1234567890",
    "price": 98.50,
    "overrides": {
      "day_count": "ActualActual.Bond",
      "frequency": "Annual",
      "business_convention": "ModifiedFollowing"
    }
  }' | jq '.'
```

**Response:**
```json
{
  "status": "success",
  "bond": {
    "description": "T 3 15/08/52",
    "isin": null,
    "conventions": {
      "fixed_frequency": "Semiannual",
      "day_count": "ActualActual_Bond",
      "business_day_convention": "Following",
      "end_of_month": true
    },
    "route_used": "universal_parser"
  },
  "analytics": {
    "ytm": 4.8991,
    "duration": 16.35,
    "accrued_interest": 1.112,
    "clean_price": 71.66,
    "dirty_price": 72.772,
    "macaulay_duration": 16.75,
    "duration_annual": 15.96,
    "ytm_annual": 4.9591,
    "convexity": 370.21,
    "pvbp": 0.1172,
    "settlement_date": "2025-07-30",
    "spread": null,
    "z_spread": null
  },
  "calculations": {
    "basis": "Semi-annual compounding",
    "day_count": "ActualActual_Bond",
    "business_day_convention": "Following"
  },
  "field_descriptions": {
    "ytm": "Yield to maturity (bond native convention, %)",
    "duration": "Modified duration (years, bond native convention)",
    "accrued_interest": "Accrued interest (%)",
    "clean_price": "Price excluding accrued interest",
    "dirty_price": "Price including accrued interest (settlement value)",
    "macaulay_duration": "Macaulay duration (years)",
    "duration_annual": "Modified duration (years, annual convention)",
    "ytm_annual": "Yield to maturity (annual equivalent, %)",
    "convexity": "Price convexity",
    "pvbp": "Price Value of a Basis Point (per 1M notional)",
    "settlement_date": "Settlement date used for calculations",
    "spread": "G-spread over government curve (bps)",
    "z_spread": "Z-spread over treasury curve (bps)"
  },
  "metadata": {
    "api_version": "10.0.0",
    "calculation_engine": "xtrillion_core_quantlib_engine"
  }
}
```

### 4.4 Portfolio Analysis

**Endpoint:** `POST /portfolio/analysis`

**Returns both individual bond analytics AND aggregated portfolio statistics.**

**Request:**
```bash
curl -X POST "https://api.x-trillion.ai/api/v1/portfolio/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "data": [
      {
        "description": "T 3 15/08/52",   // Bond description (recommended)
        "CLOSING PRICE": 71.66,          // Bond price
        "WEIGHTING": 50.0                 // Portfolio weight (%)
      },
      {
        "description": "T 4.1 02/15/28", // Treasury description format
        "CLOSING PRICE": 99.5,
        "WEIGHTING": 50.0
      }
    ]
  }' | jq '.'
```

**Alternative - ISIN Approach:**
```bash
# For clients using ISIN codes
curl -X POST "https://api.x-trillion.ai/api/v1/portfolio/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "data": [
      {
        "ISIN": "US00131MAB90",       // ISIN code
        "CLOSING PRICE": 71.66,
        "WEIGHTING": 50.0
      }
    ]
  }' | jq '.'
```

**Field Notes:**

- `ISIN: ISIN code

- `description`: Bond descriptions 

  

**Response:**

```json
{
  "status": "success",
  "portfolio_metrics": {
    "portfolio_yield": 5.87,
    "portfolio_duration": 15.26,
    "portfolio_spread": 126.4,
    "total_bonds": 2,
    "success_rate": "100.0%"
  },
  "bond_data": [
    {
      "status": "success",
      "description": "T 3 15/08/52",
      "yas": {
        "yield": "4.90%",
        "duration": "16.4 years"
      },
      "analytics": {
        "ytm": 4.8991,
        "duration": 16.35,
        "price": 71.66,
        "spread": 0
      }
    },
    {
      "status": "success", 
      "description": "PANAMA 3.87 23/07/60",
      "yas": {
        "yield": "7.33%",
        "duration": "13.6 years"
      },
      "analytics": {
        "ytm": 7.3315,
        "duration": 13.63,
        "price": 56.60,
        "spread": 315.9
      }
    }
  ],
  "metadata": {
    "api_version": "10.0.0",
    "processing_type": "portfolio_optimized",
    "response_format": "Optimized + Full"
  }
}
```

### 4.5 Cash Flow Analysis

**Endpoint:** `POST /bond/cashflow`

Calculate future cash flows for bonds with advanced filtering options.

**Request:**
```bash
# Get all future cash flows
curl -X POST "https://api.x-trillion.ai/api/v1/bond/cashflow" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "bonds": [
      {
        "description": "T 3 15/08/52",
        "nominal": 1000000
      }
    ],
    "filter": "all",
    "context": "portfolio",
    "settlement_date": "2025-07-30"
  }' | jq '.'
```

**Filter Options:**
- `"filter": "all"` - Returns all future cash flows (default)
- `"filter": "next"` - Returns only the next cash flow
- `"filter": "period"` with `"days": 90` - Returns cash flows within specified days

**Response:**
```json
{
  "status": "success",
  "portfolio_cash_flows": [
    {
      "date": "2025-12-31",
      "amount": 4164.38,
      "days_from_settlement": 152
    },
    {
      "date": "2026-06-30",
      "amount": 4958.90,
      "days_from_settlement": 333
    }
  ],
  "metadata": {
    "total_cash_flows": 2,
    "total_nominal": 1000000,
    "settlement_date": "July 30th, 2025"
  }
}
```

#### 4.5a Next Cash Flow Only

**Endpoint:** `POST /bond/cashflow/next`

Convenience endpoint to get only the next cash flow.

```bash
curl -X POST "https://api.x-trillion.ai/api/v1/bond/cashflow/next" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "bonds": [
      {
        "description": "T 3 15/08/52",
        "nominal": 1000000
      }
    ]
  }' | jq '.'
```

#### 4.5b Period-Based Cash Flows

**Endpoint:** `POST /bond/cashflow/period/<days>`

Get cash flows within a specific number of days.

```bash
# Get cash flows for next 180 days
curl -X POST "https://api.x-trillion.ai/api/v1/bond/cashflow/period/180" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
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
  }' | jq '.'
```

**Use Cases:**
- **Liquidity Management**: Track upcoming cash flows for portfolio liquidity
- **Reinvestment Planning**: Identify cash available for reinvestment
- **Cash Flow Matching**: Match assets to liabilities by payment dates

---

## 5. Enhanced JavaScript Integration

```javascript
/**
 * XTrillion Bond API Client
 */
class XTrillionBondAPI {
    constructor(apiKey = "your_api_key_here") {
        this.baseURL = "https://api.x-trillion.ai/api/v1";
        this.apiKey = apiKey;
        this.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': this.apiKey
        };
    }

    async analyzeBond({
        description = null,
        isin = null,
        price = 100.0,
        settlementDate = null
    }) {
        const payload = { price };
        if (description) payload.description = description;
        if (isin) payload.isin = isin;
        if (settlementDate) payload.settlement_date = settlementDate;

        const response = await fetch(`${this.baseURL}/bond/analysis`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(payload)
        });

        return await response.json();
    }

    async analyzePortfolio({ data, settlementDate = null }) {
        const payload = { data };
        if (settlementDate) payload.settlement_date = settlementDate;

        const response = await fetch(`${this.baseURL}/portfolio/analysis`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(payload)
        });

        return await response.json();
    }


    async checkHealth() {
        const response = await fetch(`${this.baseURL}/health`);
        return await response.json();
    }
}

// Usage Examples
const api = new XTrillionBondAPI();

// Test all endpoints
(async () => {
    try {
        // Health check
        console.log("=== Health Check ===");
        const health = await api.checkHealth();
        console.log(`API Status: ${health.status}`);
        console.log(`Version: ${health.version}`);

        // Individual bond analysis
        console.log("\n=== Bond Analysis ===");
        const bondResult = await api.analyzeBond({
            description: "T 3 15/08/52",
            price: 71.66,
            settlementDate: "2025-07-30"
        });
        console.log(`YTM: ${bondResult.analytics.ytm.toFixed(4)}%`);
        console.log(`Duration: ${bondResult.analytics.duration.toFixed(2)} years`);

        // Portfolio analysis
        console.log("\n=== Portfolio Analysis ===");
        const portfolioResult = await api.analyzePortfolio({
            data: [
                {
                    "description": "T 3 15/08/52",
                    "price": 71.66,
                    "weight": 60.0
                },
                {
                    "description": "PANAMA 3.87 23/07/60",
                    "price": 56.60,
                    "weight": 40.0
                }
            ],
            settlementDate: "2025-07-30"
        });
        console.log(`Portfolio Yield: ${portfolioResult.portfolio_metrics.portfolio_yield}%`);
        console.log(`Portfolio Duration: ${portfolioResult.portfolio_metrics.portfolio_duration} years`);


    } catch (error) {
        console.error("API Test Failed:", error);
    }
})();
```

---

## 6. Quality Assurance & Precision

### 6.1 Professional-Grade Accuracy

XTrillion Core delivers institutional-quality calculations that meet the stringent requirements of professional fixed income trading and portfolio management.

### 6.2 Validation Framework

Our calculation engine undergoes continuous validation against industry benchmarks to ensure reliable performance across diverse market conditions and bond types.

---

## 7. Context-Aware Responses

The API supports context-aware responses to optimize for different use cases. Add a `context` parameter to any bond analysis request.

### 7.1 Available Contexts

#### Portfolio Context
Simplified response optimized for portfolio aggregation (50% smaller):

```bash
curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "description": "T 3 15/08/52",
    "price": 71.66,
    "context": "portfolio"
  }' | jq '.'
```

**Portfolio Context Response:**
```json
{
  "status": "success",
  "analytics": {
    "yield_semi": 4.902780,
    "yield_annual": 4.962873,
    "duration_semi": 16.260414,
    "duration_annual": 15.871346,
    "macaulay_duration_semi": 16.65902,
    "macaulay_duration_annual": 16.65902,
    "convexity": 367.199951,
    "accrued_interest": 1.383978,
    "pvbp": 0.116522,
    "clean_price": 71.66,
    "dirty_price": 73.043978,
    "settlement_date": "2025-08-01"
  },
  "bond": {
    "description": "T 3 15/08/52",
    "isin": null
  },
  "context": "portfolio",
  "optimization": "Metrics optimized for portfolio aggregation with both annual/semi-annual basis",
  "metadata": {
    "api_version": "v1.2",
    "calculation_engine": "xtrillion_core_quantlib_engine",
    "context_applied": "portfolio"
  }
}
```

#### Technical Context
Enhanced response with debugging and parsing details:

```bash
curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "description": "T 3 15/08/52",
    "price": 71.66,
    "context": "technical"
  }' | jq '.'
```

Technical context adds:
- `debug_info` object with parsing route, engine details, and field counts
- Enhanced metadata for troubleshooting
- Complete convention details applied

### 7.2 Context Benefits

| Context | Response Size | Use Case | Key Features |
|---------|--------------|----------|--------------|
| `portfolio` | ~720 chars (50% smaller) | Portfolio aggregation | Dual annual/semi metrics, simplified structure |
| `technical` | ~1,900 chars | Debugging & development | Parsing details, debug info, full metadata |
| Default | ~1,500 chars | General use | Comprehensive metrics with field descriptions |

---

## 8. Parameter Overrides

The API supports overriding bond parameters to accommodate custom bond static data or scenario testing.

### 8.1 Supported Override Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `coupon` | float | Coupon rate (%) | 3.25 |
| `maturity` | string | Maturity date | "2052-08-15" |
| `day_count` | string | Day count convention | "ActualActual.Bond" |
| `frequency` | string | Payment frequency | "Semiannual" |
| `business_convention` | string | Business day convention | "Following" |
| `issuer` | string | Bond issuer | "US Treasury" |
| `currency` | string | Currency code | "USD" |
| `face_value` | float | Face value | 1000000 |
| `end_of_month` | bool | End of month rule | true |
| `first_coupon_date` | string | First coupon date | "2025-02-15" |
| `issue_date` | string | Issue date | "2022-08-15" |

### 8.2 Override Example

```bash
curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "description": "IBM 4.0 06/20/2042",
    "price": 85.75,
    "overrides": {
      "coupon": 4.25,
      "maturity": "2042-06-20",
      "day_count": "Thirty360.BondBasis",
      "frequency": "Semiannual",
      "issuer": "International Business Machines Corp"
    }
  }' | jq '.'
```

**Response includes override information:**
```json
{
  "analytics": {
    "ytm": 5.234,
    "duration": 12.87,
    "convexity": 245.6,
    "pvbp": 0.1102
    // ... other metrics
  },
  "overrides_applied": {
    "coupon": 4.25,
    "maturity": "2042-06-20",
    "day_count": "Thirty360.BondBasis",
    "frequency": "Semiannual",
    "issuer": "International Business Machines Corp"
  },
  "override_note": "Calculation performed with 5 parameter override(s)"
}
```

### 8.3 Use Cases

1. **External Static Data**: When you have bond reference data from external systems
2. **Scenario Analysis**: Test different coupon or maturity scenarios
3. **Custom Conventions**: Apply specific day count or business conventions
4. **Data Corrections**: Override a base bond with new characteristics

**Note**: Overrides are applied after database lookup but before calculation. The API will use the provided overrides in place of any database or parsed values.

---

## 9. Error Handling

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request (missing required fields)
- `401` - Unauthorized (invalid API key)
- `404` - Endpoint not found
- `500` - Internal server error

### Error Response Format
```json
{
  "status": "error",
  "code": 400,
  "message": "Field 'description' or 'isin' must be provided for each bond."
}
```

---

## 10. Contact & Support

**XTrillion Core Bond Calculation Engine**  
*Institutional-grade bond analytics with Bloomberg compatibility*

**API Base URL:** `https://api.x-trillion.ai/api/v1`  
**Request a Demo:** Contact us for API access

*API specification last updated: July 29, 2025*

---

**Production-ready institutional bond analytics platform with enhanced precision and comprehensive database coverage.**