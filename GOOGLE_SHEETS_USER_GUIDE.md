# XTrillion Bond Analytics for Google Sheets - User Guide
## Version 6.0 - Multi-Environment Support with Full Precision

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Environment Support](#environment-support)
4. [Core Functions](#core-functions)
5. [Array Functions (Recommended)](#array-functions-recommended)
6. [Individual Bond Functions](#individual-bond-functions)
7. [Portfolio Analysis](#portfolio-analysis)
8. [Environment Management](#environment-management)
9. [Real-World Examples](#real-world-examples)
10. [Performance Optimization](#performance-optimization)
11. [Troubleshooting](#troubleshooting)
12. [Best Practices](#best-practices)
13. [Deployment Workflow](#deployment-workflow)

---

## Introduction

XTrillion Bond Analytics for Google Sheets provides institutional-grade bond analysis directly in your spreadsheets. Our custom functions integrate with the GA10 calculation engine to deliver:

- **Yield-to-Maturity (YTM)** calculations
- **Duration** and **Convexity** metrics
- **Spread** analysis
- **Portfolio-level** aggregations
- **Cash flow** projections
- **Real-time** bond analytics

### Key Benefits
- ⚡ **30x faster** than individual API calls
- 📊 Process **entire portfolios** with one formula
- 🎯 **Bloomberg-grade** accuracy (±0.01 per million)
- 🔄 **Auto-updating** with live market data
- 💾 **Smart caching** for optimal performance
- 🌐 **Multi-environment** support (testing → maia_dev → production)
- 📏 **Full precision** values (6+ decimal places)
- 🛠️ **Three-tier deployment** workflow

---

## Installation

### Step 1: Open Google Sheets
1. Navigate to [Google Sheets](https://sheets.google.com)
2. Open your existing spreadsheet or create a new one
3. Name your sheet (e.g., "Bond Portfolio Analysis")

### Step 2: Install the XTrillion Script
1. In your Google Sheet, click **Extensions → Apps Script**
2. Delete any existing code in the editor
3. Copy the entire contents of `xt_functions_complete_multi_env.gs`
4. Paste the code into the Apps Script editor
5. Click **Save** (💾 icon)
6. Name your project: "XTrillion Bond Analytics v6.0"
6. Name the project: "XTrillion Bond Analytics"

### Step 3: Authorize the Script
1. Click **Run** (▶️ icon) to execute any function
2. When prompted, click **Review permissions**
3. Choose your Google account
4. Click **Advanced** → **Go to XTrillion Bond Analytics (unsafe)**
5. Click **Allow** to grant necessary permissions

### Step 4: Verify Installation
Test the installation by entering this formula in any cell:
```excel
=XT_VERSION()
```
You should see: "XTrillion v5.0 - Complete"

---

## Core Functions

### Function Categories

| Category | Purpose | Best For |
|----------|---------|----------|
| **Array Functions** | Process multiple bonds at once | Portfolio analysis, bulk calculations |
| **Individual Functions** | Calculate single bond metrics | Specific bond analysis, custom formulas |
| **Portfolio Functions** | Aggregate portfolio statistics | Risk management, performance tracking |
| **Cash Flow Functions** | Project future cash flows | Income planning, duration matching |
| **Utility Functions** | Cache management, diagnostics | Troubleshooting, optimization |

---

## Array Functions (Recommended)

### 🌟 `XT_AUTO` - Most User-Friendly (NEW!)
Works exactly like native Google Sheets functions - **highly recommended for new users**.

**Syntax:**
```excel
=XT_AUTO(bond_range, price_range, [settlement_date])
```

**Why Use XT_AUTO:**
- ✅ Works like `SUM()`, `AVERAGE()` - separate ranges
- ✅ Handles full columns: `=XT_AUTO(A:A, B:B)`
- ✅ Auto-detects where data ends
- ✅ Most flexible and intuitive

**Examples:**
```excel
=XT_AUTO(A2:A100, B2:B100)           // Process specific range
=XT_AUTO(A:A, B:B)                   // Process entire columns
=XT_AUTO(A2:A, B2:B, "2025-01-15")   // With settlement date
```

**Returns:** 
A table with columns: Bond, YTM (%), Duration, Spread (bps)

---

### `XT_ARRAY` - Process Multiple Bonds
The original powerful function for portfolio analysis.

**Syntax:**
```excel
=XT_ARRAY(bond_descriptions, prices, [settlement_date])
```

**Parameters:**
- `bond_descriptions`: Range of bond descriptions (e.g., A2:A100)
- `prices`: Range of bond prices (e.g., B2:B100)
- `settlement_date`: Optional settlement date (default: prior month-end)

**Example:**
```excel
=XT_ARRAY(A2:A51, B2:B51, "2025-01-15")
```

**Returns:** 
A table with columns: Bond, YTM (%), Duration, Spread (bps)

> **💡 Tip**: For maximum flexibility, consider using `XT_AUTO(A2:A51, B2:B51, "2025-01-15")` instead - it works more like native Google Sheets functions!

### `XT_ARRAY_CUSTOM` - Select Specific Metrics
Choose exactly which metrics you need.

**Syntax:**
```excel
=XT_ARRAY_CUSTOM(bonds, prices, metrics, [settlement_date])
```

**Available Metrics:**
- `ytm` - Yield to Maturity
- `duration` - Modified Duration
- `convexity` - Convexity
- `pvbp` - Price Value of Basis Point
- `spread` - G-Spread
- `macaulay` - Macaulay Duration
- `clean_price` - Clean Price
- `dirty_price` - Dirty Price
- `accrued` - Accrued Interest

**Example:**
```excel
=XT_ARRAY_CUSTOM(A2:A10, B2:B10, "ytm,duration,convexity,pvbp")
```

### `XT_DYNAMIC` - Auto-Detect Range  
Automatically processes all bonds from a multi-column range.

**Syntax:**
```excel
=XT_DYNAMIC(range_with_bonds_and_prices)
```

**Example:**
```excel
=XT_DYNAMIC(A2:B100)
```

This processes bonds in column A with prices in column B, stopping at first empty bond.

### `XT_AUTO` - Most Flexible (Recommended)
Works like native Google Sheets functions with separate ranges.

**Syntax:**
```excel
=XT_AUTO(bond_range, price_range, [settlement_date])
```

**Examples:**
```excel
=XT_AUTO(A2:A100, B2:B100)        // Specific ranges
=XT_AUTO(A:A, B:B)                // Full columns (auto-detect)
=XT_AUTO(A2:A, B2:B, "2025-01-15") // With settlement date
```

This is the most user-friendly function - works exactly like SUM(), AVERAGE(), etc.

---

## Individual Bond Functions

### Basic Analysis Functions

#### `XT_YTM` - Yield to Maturity
```excel
=XT_YTM(bond_description, price, [settlement_date])
```

**Example:**
```excel
=XT_YTM("T 4.125 15/11/32", 98.5, "2025-01-15")
```

#### `XT_DURATION` - Modified Duration
```excel
=XT_DURATION(bond_description, price, [settlement_date])
```

#### `XT_CONVEXITY` - Bond Convexity
```excel
=XT_CONVEXITY(bond_description, price, [settlement_date])
```

#### `XT_SPREAD` - G-Spread
```excel
=XT_SPREAD(bond_description, price, [settlement_date])
```

### Advanced Analysis Functions

#### `XT_PVBP` - Price Value of Basis Point
```excel
=XT_PVBP(bond_description, price, [settlement_date])
```

#### `XT_MACAULAY` - Macaulay Duration
```excel
=XT_MACAULAY(bond_description, price, [settlement_date])
```

#### `XT_DV01` - Dollar Value of 01
```excel
=XT_DV01(bond_description, price, [settlement_date])
```

### Pricing Functions

#### `XT_CLEAN_PRICE` - Clean Price from YTM
```excel
=XT_CLEAN_PRICE(bond_description, ytm, [settlement_date])
```

#### `XT_DIRTY_PRICE` - Dirty Price (with accrued)
```excel
=XT_DIRTY_PRICE(bond_description, ytm, [settlement_date])
```

#### `XT_ACCRUED` - Accrued Interest
```excel
=XT_ACCRUED(bond_description, [settlement_date])
```

---

## Portfolio Analysis

### Portfolio-Wide Metrics

#### `XT_PORTFOLIO_SUMMARY` - Complete Portfolio Analysis
```excel
=XT_PORTFOLIO_SUMMARY(bonds, prices, weights, [settlement_date])
```

**Returns:**
- Weighted Average YTM
- Portfolio Duration
- Portfolio Convexity
- Total Market Value
- Individual bond contributions

**Example:**
```excel
=XT_PORTFOLIO_SUMMARY(A2:A51, B2:B51, C2:C51)
```

#### `XT_PORTFOLIO_RISK` - Risk Metrics
```excel
=XT_PORTFOLIO_RISK(bonds, prices, weights)
```

**Returns:**
- Duration risk
- Convexity adjustment
- Key rate durations
- Scenario analysis

---

## Cash Flow Analysis

### `XT_CASHFLOWS` - Project Future Cash Flows
```excel
=XT_CASHFLOWS(bond_description, face_value, [settlement_date])
```

**Returns:** Table of future cash flows with dates and amounts

### `XT_CASHFLOW_SCHEDULE` - Detailed Payment Schedule
```excel
=XT_CASHFLOW_SCHEDULE(bonds_range, face_values_range)
```

**Returns:** Consolidated cash flow schedule for entire portfolio

---

## Real-World Examples

### Example 1: Treasury Portfolio Analysis

**Setup:**
```
A1: Bond Description    B1: Price    C1: Face Value
A2: T 2.75 15/02/28    B2: 95.5     C2: 1000000
A3: T 3.125 15/11/29   B3: 97.25    C3: 500000
A4: T 4.0 15/02/33     B4: 101.75   C4: 750000
```

**Array Formula (in D1):**
```excel
=XT_ARRAY(A2:A4, B2:B4)
```

**Individual Metrics:**
```excel
E2: =XT_YTM(A2, B2) * C2/SUM(C:C)  // Weighted YTM contribution
```

### Example 2: Corporate Bond Screening

**Find High-Yield Opportunities:**
```excel
=QUERY(XT_ARRAY(A:A, B:B), 
       "SELECT * WHERE Col2 > 6 ORDER BY Col2 DESC LIMIT 10", 1)
```

This shows the top 10 highest-yielding bonds.

### Example 3: Duration Matching

**Match Portfolio Duration to Target:**
```excel
Target Duration: 7.5
Current Duration: =SUMPRODUCT(XT_ARRAY(A2:A10,B2:B10)[3],C2:C10)/SUM(C2:C10)
```

### Example 4: Monthly Rebalancing

**Track Changes:**
```excel
=XT_ARRAY(A2:A50, B2:B50, TODAY()) - XT_ARRAY(A2:A50, B2:B50, EOMONTH(TODAY(),-1))
```

Shows month-over-month changes in YTM and duration.

---

## Performance Optimization

### Caching Strategy

The script implements smart caching to minimize API calls:

1. **Session Cache**: Results cached for current session
2. **Persistent Cache**: Results stored in document properties
3. **TTL (Time-to-Live)**: 5-minute cache expiration

### Clear Cache When Needed
```excel
=XT_CLEAR_CACHE()
```

### Best Practices for Large Portfolios

#### For 50-200 Bonds:
Use single array formula:
```excel
=XT_ARRAY(A2:A201, B2:B201)
```

#### For 200-500 Bonds:
Split into batches:
```excel
=XT_ARRAY(A2:A101, B2:B101)
=XT_ARRAY(A102:A201, B102:B201)
```

#### For 500+ Bonds:
Use batch processing function:
```excel
=XT_BATCH_PROCESS(A2:A1001, B2:B1001, 100)
```

---

## Troubleshooting

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| `#ERROR!` | Invalid bond format | Check bond description format |
| `#NAME?` | Function not recognized | Re-save Apps Script project |
| `Service unavailable` | API rate limit | Wait 30 seconds, use cache |
| `No data` | Network timeout | Increase timeout in script |
| `Wrong values` | Stale cache | Use `XT_CLEAR_CACHE()` |
| `Slow performance` | Individual formulas | Switch to array formulas |

### Debug Mode

Enable detailed logging:
```excel
=XT_DEBUG("T 4.125 15/11/32", 98.5)
```

Returns detailed API response and processing information.

### API Health Check
```excel
=XT_HEALTH_CHECK()
```

Verifies API connectivity and database status.

---

## Best Practices

### 1. Data Organization

**Recommended Layout:**
```
Column A: Bond descriptions or ISINs
Column B: Prices
Column C: Face values or weights
Column D: Settlement dates (if individual)
Column E-G: Results from XT_ARRAY
```

### 2. Formula Optimization

**DO:**
- ✅ Use array formulas for multiple bonds
- ✅ Cache results when possible
- ✅ Process bonds in batches
- ✅ Use consistent date formats (YYYY-MM-DD)

**DON'T:**
- ❌ Copy individual formulas down columns
- ❌ Make unnecessary API calls
- ❌ Clear cache too frequently
- ❌ Mix date formats

### 3. Error Handling

Add validation:
```excel
=IF(ISERROR(XT_YTM(A2,B2)), "Check bond format", XT_YTM(A2,B2))
```

### 4. Automatic Updates

Set up triggers for real-time updates:
1. Apps Script Editor → Triggers
2. Add trigger → Time-driven → Every hour
3. Function: `updateAllBonds`

### 5. Performance Monitoring

Track API usage:
```excel
=XT_API_STATS()
```

Shows:
- Total API calls today
- Cache hit rate
- Average response time
- Error count

---

## Advanced Features

### Custom Metrics

Create custom calculations:
```excel
// Risk-adjusted return
=XT_YTM(A2,B2) / XT_DURATION(A2,B2)

// Convexity-adjusted duration
=XT_DURATION(A2,B2) - 0.5 * XT_CONVEXITY(A2,B2) * 0.01
```

### Conditional Formatting

Highlight opportunities:
1. Select YTM column
2. Format → Conditional formatting
3. Color scale: Green (high) to Red (low)

### Data Validation

Compare with benchmarks:
```excel
=ABS(XT_YTM(A2,B2) - D2) < 0.001  // Within 0.1% of Bloomberg
```

### Scenario Analysis

Test rate changes:
```excel
// 100bp rate increase impact
=B2 * (1 - XT_DURATION(A2,B2) * 0.01)
```

---

## Appendix

### Supported Bond Formats

**Treasury:**
- `T 4.125 15/11/32`
- `UST 2.75 02/15/28`
- `US912810TJ79` (ISIN)

**Corporate:**
- `AAPL 3.45 05/06/29`
- `US037833CG37` (ISIN)

### API Limits
- **Rate Limit**: 60 requests/minute
- **Batch Size**: 500 bonds maximum
- **Cache Duration**: 5 minutes
- **Timeout**: 30 seconds

### Support Resources
- **API Health**: `https://future-footing-414610.uc.r.appspot.com/health`
- **Documentation**: Internal team resources
- **Test Data**: `test_portfolio_data.csv`

---

## Quick Reference Card

| Function | Purpose | Example |
|----------|---------|---------|
| **`XT_AUTO`** | **Most flexible processing** | **`=XT_AUTO(A:A, B:B)`** |
| `XT_ARRAY` | Process multiple bonds | `=XT_ARRAY(A2:A100, B2:B100)` |
| `XT_DYNAMIC` | Auto-detect from range | `=XT_DYNAMIC(A2:B100)` |
| `XT_YTM` | Single bond YTM | `=XT_YTM("T 4.125 15/11/32", 98.5)` |
| `XT_DURATION` | Modified duration | `=XT_DURATION(A2, B2)` |
| `XT_SPREAD` | G-Spread | `=XT_SPREAD(A2, B2)` |
| `XT_CLEAR_CACHE` | Clear cached results | `=XT_CLEAR_CACHE()` |
| `XT_PORTFOLIO_SUMMARY` | Portfolio analytics | `=XT_PORTFOLIO_SUMMARY(A:A, B:B, C:C)` |

---

*Last Updated: January 2025 | Version 5.0*