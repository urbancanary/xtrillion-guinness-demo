# XTrillion Google Sheets Setup Guide
## Version 6.0 - Multi-Environment Support with Full Precision

---

## 🚀 Quick Start - Multi-Environment Bond Analytics

### Step 1: Create a New Google Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. Name it: "XTrillion Bond Analytics v6.0"

### Step 2: Install the Multi-Environment Scripts

1. In your Google Sheet, go to **Extensions → Apps Script**
2. Delete any existing code
3. Copy the entire contents of `xt_functions_complete_multi_env.gs`
4. Paste into the Apps Script editor
5. Click **Save** (💾 icon)
6. Name the project: "XTrillion Bond Analytics v6.0"

### Step 3: Verify Multi-Environment Installation

Test the installation by entering this formula in any cell:

```excel
=XT_VERSION()
```

You should see: `"XTrillion v6.0 Complete Multi-Environment (Production)"`

### Step 4: Test Environment Connectivity

Check all available environments:

```excel
=XT_ENVIRONMENTS()
```

This will show you all available environments and their usage examples.

---

## 🌐 Environment Setup

### Environment Options

XTrillion v6.0 supports three deployment environments:

| Environment | Purpose | Usage Example |
|-------------|---------|---------------|
| **testing** | Your local development | `=XT_ARRAY(A2:A10, B2:B10, , "testing")` |
| **maia_dev** | Team testing | `=XT_ARRAY(A2:A10, B2:B10, , "maia_dev")` |
| **production** | Live production | `=XT_ARRAY(A2:A10, B2:B10)` |

### Test Each Environment

**Test production (default):**
```excel
=XT_HEALTH_CHECK()
```

**Test maia development:**
```excel
=XT_TEST_ENV("maia_dev")  
```

**Test local (if running):**
```excel
=XT_TEST_ENV("testing")
```

---

## 📊 Sample Data Setup

### Step 1: Create Test Portfolio

Create a sample portfolio to test the functions:

| A (Bond) | B (Price) | C (Weight) |
|----------|-----------|------------|
| T 3 15/08/52 | 70.00 | 25% |
| T 4.1 02/15/28 | 99.50 | 25% |
| T 2.25 08/15/49 | 85.30 | 25% |
| T 1.125 02/15/31 | 92.10 | 25% |

### Step 2: Test Basic Functions

**Test single bond calculation:**
```excel
=xt_ytm("T 3 15/08/52", 70)
```

**Test array function (recommended):**
```excel
=XT_AUTO(A2:A5, B2:B5)
```

**Test with environment parameter:**
```excel
=XT_AUTO(A2:A5, B2:B5, , "production")
```

---

## 🎯 Function Categories

### 1. Array Functions (Recommended)

**Most Flexible - XT_AUTO:**
```excel
=XT_AUTO(A2:A100, B2:B100, , "production")
=XT_AUTO(A2:A100, B2:B100, , "maia_dev")
=XT_AUTO(A2:A100, B2:B100, , "testing")
```

**Standard Array - XT_ARRAY:**
```excel
=XT_ARRAY(A2:A10, B2:B10, C2, "production")
```

**Custom Metrics - XT_ARRAY_CUSTOM:**
```excel
=XT_ARRAY_CUSTOM(A2:A10, B2:B10, "ytm,duration,convexity", , "maia_dev")
```

**Smart Caching - XT_SMART:**
```excel
=XT_SMART(A2:A10, B2:B10, , FALSE, "production")
```

**Batch Processing - XT_BATCH_PROCESS:**
```excel
=XT_BATCH_PROCESS(A2:A1000, B2:B1000, 100, , "production")
```

### 2. Individual Bond Functions

**Legacy format (backward compatible):**
```excel
=xt_ytm("T 3 15/08/52", 70, , "production")
=xt_duration("T 4.25 11/15/40", 95.5, , "maia_dev")
=xt_spread("AAPL 3.45 02/09/45", 98.2, , "testing")
```

**Standardized format:**
```excel
=XT_YTM("T 3 15/08/52", 70, , "production")
=XT_DURATION("T 4.25 11/15/40", 95.5, , "maia_dev")
=XT_SPREAD("AAPL 3.45 02/09/45", 98.2, , "testing")
```

### 3. Portfolio Functions

**Portfolio Summary:**
```excel
=XT_PORTFOLIO_SUMMARY(A2:A10, B2:B10, C2:C10, , "production")
```

### 4. Environment Management

**Show all environments:**
```excel
=XT_ENVIRONMENTS()
```

**Test connectivity:**
```excel
=XT_TEST_ENV("maia_dev")
=XT_HEALTH_CHECK("testing")
```

**Environment statistics:**
```excel
=XT_API_STATS("production")
=XT_VERSION("maia_dev")
```

### 5. Debug Functions

**Debug single bond:**
```excel
=XT_DEBUG("T 3 15/08/52", 70, , "testing")
```

**Debug portfolio:**
```excel
=XT_DEBUG_PORTFOLIO("T 3 15/08/52", 70, "T 4 1/15/30", 95, "maia_dev")
```

### 6. Cache Management

**Cache utilities:**
```excel
=XT_CACHE_SIZE()
=XT_CLEAR_CACHE()
```

---

## 🔍 Verification Steps

### 1. Function Availability Check

Test that all major functions are available:

```excel
=XT_VERSION()                    // Should show v6.0
=XT_ENVIRONMENTS()               // Should show 3+ environments  
=XT_AUTO(A2:A3, B2:B3)          // Should return bond metrics
=XT_HEALTH_CHECK()               // Should show API status
```

### 2. Precision Verification

Verify that full precision is working:

```excel
=XT_DEBUG("T 3 15/08/52", 70)   // Check raw response
=XT_AUTO(A2:A3, B2:B3)          // Should show 6+ decimal places
```

**Expected results:**
- YTM values should show full precision (e.g., 5.0449628829956055)
- Duration values should show full precision (e.g., 16.116099009158262)
- No more truncated values like "5.04%" or "16.1 years"

### 3. Environment Connectivity

Test each environment if available:

```excel
=XT_TEST_ENV("testing")      // If local server running
=XT_TEST_ENV("maia_dev")     // If maia-dev deployed  
=XT_TEST_ENV("production")   // Should always work
```

### 4. Performance Test

Test array functions vs individual functions:

```excel
// Array function (1 API call for multiple bonds)
=XT_AUTO(A2:A11, B2:B11)

// Individual functions (10 separate API calls)  
=xt_ytm(A2, B2)
=xt_ytm(A3, B3)
// ... etc
```

Array functions should be significantly faster for multiple bonds.

---

## 🛠️ Development Workflow Setup

### For Developers/Advanced Users

If you're developing or testing new features:

### 1. Local Environment Setup

**Start local API server:**
```bash
FLASK_APP=google_analysis10_api.py flask run --port 8081
```

**Test local connectivity:**
```excel
=XT_TEST_ENV("testing")
=XT_AUTO(A2:A5, B2:B5, , "testing")
```

### 2. Multi-Environment Testing

**Test the same data across environments:**
```excel
// Production
=XT_AUTO(A2:A5, B2:B5, , "production")

// Maia development (if available)
=XT_AUTO(A2:A5, B2:B5, , "maia_dev")

// Local testing (if running)
=XT_AUTO(A2:A5, B2:B5, , "testing")
```

Results should be identical across environments (same precision).

### 3. Debug Mode

**Enable detailed debugging:**
```excel
=XT_DEBUG("T 3 15/08/52", 70, , "testing")
```

This shows the raw API response for troubleshooting.

---

## 📋 Troubleshooting

### Common Issues

**1. Function not recognized:**
- Verify you've pasted the complete `xt_functions_complete_multi_env.gs` file
- Check that you've saved the Apps Script project
- Try refreshing the Google Sheet

**2. Environment connection failed:**
```excel
=XT_TEST_ENV("testing")      // Check if local server is running
=XT_HEALTH_CHECK("maia_dev") // Check if deployment is healthy
```

**3. Precision issues:**
- Verify you're using the v6.0 functions
- Check that the API is returning raw numbers: `=XT_DEBUG(...)`
- Clear cache if needed: `=XT_CLEAR_CACHE()`

**4. Performance issues:**
- Use array functions instead of individual functions
- Check cache status: `=XT_CACHE_SIZE()`
- Consider using `XT_SMART()` for frequently updated data

### Getting Help

**Environment status:**
```excel
=XT_ENVIRONMENTS()        // Show all environments
=XT_API_STATS()          // Show API statistics
=XT_VERSION()            // Show version info
```

**Debug information:**
```excel
=XT_DEBUG("bond", price, , "environment")
```

**Health checks:**
```excel
=XT_HEALTH_CHECK("production")
=XT_TEST_ENV("maia_dev") 
```

---

## 🎯 Best Practices

### 1. Environment Usage
- Use `"testing"` for development and debugging
- Use `"maia_dev"` for team validation
- Use `"production"` (or omit) for live usage

### 2. Function Selection
- Use `XT_AUTO()` for most cases (most flexible)
- Use `XT_ARRAY()` for specific ranges
- Use `XT_SMART()` for frequently changing data
- Use individual functions only for single bonds

### 3. Performance Optimization
- Array functions are 30x faster for multiple bonds
- Cache frequently used calculations
- Use batch processing for large portfolios
- Monitor performance with `XT_API_STATS()`

### 4. Error Handling
- Always test functions after setup
- Use debug functions for troubleshooting
- Check environment health regularly
- Clear cache if experiencing issues

---

## 📈 Advanced Features

### Smart Caching
```excel
// Only recalculates changed bonds
=XT_SMART(A2:A100, B2:B100, , FALSE, "production")

// Force refresh all bonds  
=XT_SMART(A2:A100, B2:B100, , TRUE, "production")
```

### Custom Metrics
```excel
// Get only specific metrics
=XT_ARRAY_CUSTOM(A2:A50, B2:B50, "ytm,duration,pvbp", , "production")
```

### Portfolio Analysis
```excel
// Portfolio-weighted metrics
=XT_PORTFOLIO_SUMMARY(A2:A50, B2:B50, C2:C50, , "production")
```

### Batch Processing
```excel
// Process 1000+ bonds efficiently
=XT_BATCH_PROCESS(A2:A1000, B2:B1000, 100, , "production")
```

---

**Ready for institutional-grade bond analytics with full precision and multi-environment support!** 🎯

Version 6.0 - Complete Multi-Environment Setup Guide