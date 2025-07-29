# XTrillion Core Bond Calculation Engine API Specification

**Date:** July 29, 2025  
**Status:** Production Version - Bloomberg-Compatible Contexts

## 1. Overview

XTrillion's bond analytics engine delivers institutional-grade calculations with a focus on clarity, accuracy, and Bloomberg compatibility. Our philosophy is to offer the essential, high-value metrics used in trading, portfolio management, and risk systems—without the burden of low-utility complexity.

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
- `"UST 3% 08/15/52"` - US Treasury with explicit formatting US date format
- `"TREASURY 3 15/08/2052"` - Treasury with year-only maturity
- `"US TREASURY N/B, 3%, 15-Aug-2052"` - Full Bloomberg-style description
- `"T 3 15-Aug-52"` - Ticker based notation

---

## 3. Core Calculation Suite

The engine provides three tiers of analytics. The API field names follow a consistent naming convention explained in Section 3.1.

### Tier 1: Essential Metrics

| Calculation | API Field | Purpose |
|-------------|-----------|---------|
| Yield to Maturity | `ytm` | Internal rate of return |
| Modified Duration | `duration` | Price sensitivity to yield |
| Accrued Interest | `accrued_interest` | Days of coupon earned |
| Clean Price | `clean_price` | Price excluding accrued |
| Dirty Price | `dirty_price` | Price including accrued |

### Tier 2: Risk & Option-Adjusted Analytics

| Calculation | API Field | Purpose |
|-------------|-----------|---------|
| Macaulay Duration | `macaulay_duration` | Time-weighted average maturity |
| Convexity | `convexity` | Duration sensitivity measure |
| Price Value of a Basis Point | `pvbp` | Dollar duration per $1M |

### Tier 3: Spread Analytics (Curve Dependent)

| Calculation | API Field | Purpose |
|-------------|-----------|---------|
| G-Spread | `g_spread` | Spread over government curve |
| Z-Spread | `z_spread` | Zero-volatility spread |

### Debugging & Schedule Information

| Calculation | API Field | Purpose |
|-------------|-----------|---------|
| Last Coupon Date | `last_coupon_date` | Previous coupon payment date (QuantLib) |
| Next Coupon Date | `next_coupon_date` | Upcoming coupon payment date (QuantLib) |
| Issue Date | `issue_date` | Bond issue date (QuantLib calculated) |

### 3.1 Compounding Basis and API Naming Convention

Many fixed income metrics, particularly measures of yield and risk, vary depending on the yield's compounding frequency (the basis). For example, a bond with a semi-annual yield of 4.90% has an equivalent annual yield of 4.958%. To ensure clarity and prevent aggregation errors, XTrillion follows a consistent naming pattern.

**Our Convention:**
- **Default/Base Field**: The API field name without a suffix (e.g., `ytm`, `duration`) returns the value calculated using the bond's native payment frequency. For most US and UK bonds, this is a semi-annual basis. This aligns with the default display on Bloomberg terminals.
- **Explicit Basis Suffixes**: To get a specific basis, use the `_[basis]` suffix.
  - `_annual`: Returns the value on an annually-compounded basis. This is crucial for portfolio-level aggregation.
  - `_semi`: Explicitly requests the semi-annual basis.

**Affected Metrics:** The following metrics are dependent on the compounding basis and are available with `_annual` and `_semi` suffixes upon request:
- `ytm` (Yield to Maturity)
- `ytw` (Yield to Worst)
- `duration` (Modified Duration)
- `macaulay_duration` (Macaulay Duration)
- `convexity`
- `pvbp`

---

## 4. API Design: Bloomberg-Compatible Contexts

✅ **IMPLEMENTED** - Bloomberg-style context codes for familiar institutional user experience.

XTrillion Core provides Bloomberg terminal page equivalents, giving institutional users immediate familiarity with the API response structure.

### 4.1 Available Bloomberg Contexts

#### **BXT (Bond Analysis) - Default**
```json
{
  "description": "T 3 15/08/52",
  "price": 99.2920,
  "context": "BXT"
}
```
**Returns**: Complete bond analytics (yield, duration, convexity, spreads, coupon dates)  
**Bloomberg Equivalent**: BXT page - comprehensive bond analysis  
**Accrued Interest**: Returns percentage unless nominal amount specified, then returns dollar amount  
**Fields**: `ytm`, `duration`, `convexity`, `accrued_interest`, `pvbp`, `spread`, `clean_price`, `dirty_price`, `settlement_date`

#### **YAS (Yield Analysis)**
```json
{
  "description": "T 3 15/08/52",
  "price": 99.2920,
  "context": "YAS"
}
```
**Returns**: Yield-focused metrics for yield curve analysis  
**Bloomberg Equivalent**: YAS page - yield analytics and scenarios  
**Fields**: `ytm`, `ytm_annual`, `spread`, `g_spread`, `z_spread`, `clean_price`, `settlement_date`  
**Note**: YTC (Yield to Call) not yet implemented

#### **DUR (Duration & Risk)**
```json
{
  "description": "T 3 15/08/52",
  "price": 99.2920,
  "context": "DUR"
}
```
**Returns**: Risk metrics for portfolio risk management  
**Bloomberg Equivalent**: Duration and risk analytics across Bloomberg pages  
**Fields**: `duration`, `duration_annual`, `macaulay_duration`, `convexity`, `pvbp`, `settlement_date`

#### **DES (Description & Identifiers)**
```json
{
  "description": "T 3 15/08/52",
  "price": 99.2920,
  "context": "DES"
}
```
**Returns**: Bond identifiers, issue details, and payment schedule  
**Bloomberg Equivalent**: DES page - security description  
**Fields**: `description`, `isin`, `issuer`, `maturity`, `coupon`, `issue_date`, `last_coupon_date`, `next_coupon_date`

### 4.2 Context Usage Examples

**Bloomberg Bond Analysis (Most Common):**
```json
{
  "description": "T 3 15/08/52",
  "price": 99.2920,
  "context": "BXT"
}
```

**Yield-Focused Trading Analysis:**
```json
{
  "description": "T 3 15/08/52",
  "price": 99.2920,
  "context": "YAS"
}
```

**Portfolio Risk Assessment:**
```json
{
  "description": "T 3 15/08/52",
  "price": 99.2920,
  "context": "DUR"
}
```

---

## 5. API Endpoints & Examples

### 5.1 Base URL & Authentication

**Base URL:** `https://api.x-trillion.ai`

**Authentication Header:**
```http
X-API-Key: your_api_key_here
```

**Available API Keys:**

| Environment | API Key | Usage |
|-------------|---------|-------|
| **Demo** | `gax10_demo_3j5h8m9k2p6r4t7w1q` | Public demonstrations |
| **Development** | `gax10_dev_4n8s6k2x7p9v5m8p1z` | Development testing |
| **Testing** | `gax10_test_9r4t7w2k5m8p1z6x3v` | Internal testing |

### 5.2 Health Check Endpoint

**Endpoint:** `GET /health`

**Test Command:**
```bash
curl -s "https://api.x-trillion.ai/health" | jq '.'
```

**Response:**
```json
{
  "capabilities": [
    "Professional bond analytics engine with 6,863+ validated bonds",
    "Parse bonds from text descriptions or ISIN codes",
    "Bloomberg-compatible yield, duration, and risk calculations",
    "RESTful API with Bloomberg-style contexts (BXT, YAS, DUR, DES)"
  ],
  "dual_database_system": {
    "coverage_strategy": "Primary → Secondary → CSV parsing fallback",
    "primary_database": {
      "description": "Comprehensive bond data with enrichment",
      "name": "bonds_data.db",
      "path": "./bonds_data.db",
      "size_mb": 155.7,
      "status": "connected"
    },
    "secondary_database": {
      "description": "Bloomberg reference bond data",
      "name": "bloomberg_index.db",
      "path": "./bloomberg_index.db",
      "size_mb": 46.5,
      "status": "connected"
    },
    "total_active_databases": 2
  },
  "environment": "production",
  "service": "Google Analysis 10 - XTrillion Core API with Bloomberg Contexts",
  "status": "healthy",
  "timestamp": "2025-07-29T23:35:03.485954",
  "universal_parser": {
    "available": true,
    "initialized": true,
    "status": "working",
    "test_passed": true
  },
  "validated_conventions": {
    "enhancement_level": "validated_conventions",
    "path": "./validated_quantlib_bonds.db",
    "size_mb": 2.6,
    "status": "connected"
  },
  "version": "10.0.0"
}
```

### 5.3 Individual Bond Analysis

**Endpoint:** `POST /api/v1/bond/parse-and-calculate`

**Bloomberg Bond Analysis (BXT):**
```bash
curl -s -X POST "https://api.x-trillion.ai/api/v1/bond/parse-and-calculate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_demo_3j5h8m9k2p6r4t7w1q" \
  -d '{
    "description": "T 3 15/08/52",
    "price": 99.2920,
    "context": "BXT"
  }' | jq '.'
```

**Response Structure (BXT Context):**
```json
{
  "status": "success",
  "analytics": {
    "ytm": 4.899163246154785,
    "duration": 9.69461158207455,
    "convexity": 3.5748862366416416,
    "accrued_interest": 1.0849315068493182,
    "pvbp": 0.0006947158659714622,
    "spread": null,
    "clean_price": 99.2920,
    "dirty_price": 100.376932,
    "settlement_date": "2025-06-30"
  },
  "bond": {
    "description": "T 3 15/08/52",
    "isin": null,
    "issuer": "US Treasury",
    "maturity": "2052-08-15"
  },
  "context": "BXT",
  "metadata": {
    "api_version": "v1.2",
    "calculation_engine": "xtrillion_core_quantlib_engine",
    "bloomberg_context": "Bond Analysis (BXT)"
  }
}
```

**Yield Analysis (YAS):**
```bash
curl -s -X POST "https://api.x-trillion.ai/api/v1/bond/parse-and-calculate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_demo_3j5h8m9k2p6r4t7w1q" \
  -d '{
    "description": "T 3 15/08/52",
    "price": 99.2920,
    "context": "YAS"
  }' | jq '.'
```

**Response Structure (YAS Context):**
```json
{
  "status": "success",
  "analytics": {
    "ytm": 4.899163246154785,
    "ytm_annual": 4.959168,
    "spread": null,
    "g_spread": null,
    "z_spread": null,
    "clean_price": 99.2920,
    "settlement_date": "2025-06-30"
  },
  "bond": {
    "description": "T 3 15/08/52"
  },
  "context": "YAS",
  "metadata": {
    "api_version": "v1.2",
    "calculation_engine": "xtrillion_core_quantlib_engine",
    "bloomberg_context": "Yield Analysis (YAS)"
  }
}
```

**Duration & Risk (DUR):**
```bash
curl -s -X POST "https://api.x-trillion.ai/api/v1/bond/parse-and-calculate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_demo_3j5h8m9k2p6r4t7w1q" \
  -d '{
    "description": "T 3 15/08/52",
    "price": 99.2920,
    "context": "DUR"
  }' | jq '.'
```

**Response Structure (DUR Context):**
```json
{
  "status": "success",
  "analytics": {
    "duration": 9.69461158207455,
    "duration_annual": 9.462812,
    "macaulay_duration": 9.932089,
    "convexity": 3.5748862366416416,
    "pvbp": 0.0006947158659714622,
    "settlement_date": "2025-06-30"
  },
  "bond": {
    "description": "T 3 15/08/52"
  },
  "context": "DUR",
  "metadata": {
    "api_version": "v1.2",
    "calculation_engine": "xtrillion_core_quantlib_engine",
    "bloomberg_context": "Duration & Risk (DUR)"
  }
}
```

**Description & Identifiers (DES):**
```bash
curl -s -X POST "https://api.x-trillion.ai/api/v1/bond/parse-and-calculate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_demo_3j5h8m9k2p6r4t7w1q" \
  -d '{
    "description": "T 3 15/08/52",
    "price": 99.2920,
    "context": "DES"
  }' | jq '.'
```

**Response Structure (DES Context):**
```json
{
  "status": "success",
  "analytics": {
    "description": "T 3 15/08/52",
    "isin": null,
    "issuer": "US Treasury",
    "maturity": "2052-08-15",
    "coupon": 3.0,
    "issue_date": "2022-08-15",
    "last_coupon_date": "2025-02-15",
    "next_coupon_date": "2025-08-15"
  },
  "bond": {
    "description": "T 3 15/08/52",
    "isin": null,
    "issuer": "US Treasury",
    "maturity": "2052-08-15"
  },
  "context": "DES",
  "metadata": {
    "api_version": "v1.2",
    "calculation_engine": "xtrillion_core_quantlib_engine",
    "bloomberg_context": "Description & Identifiers (DES)"
  }
}
```

**XTrillion Core Bond Calculation Engine**  
*Institutional-grade bond analytics with Bloomberg terminal compatibility*

*API specification last updated: July 29, 2025*  
*Production version - Bloomberg contexts implemented*