# ECOPETROL Accrued Interest Analysis

## Issue Summary
ECOPETROL SA, 5.875%, 28-May-2045 is showing $22,810.75 per million instead of the expected $22,847.22.

## Root Cause
The bond description parser is creating a slightly incorrect coupon schedule when parsing the description format "ECOPETROL SA, 5.875%, 28-May-2045", resulting in:
- **Calculated**: 139.8 days → $22,810.75
- **Expected**: 140 days → $22,847.22
- **Difference**: 0.2 days → $36.47

## Solution
When using the ISIN (US279158AJ82), the system correctly:
1. Retrieves validated conventions from the database
2. Uses Unadjusted business day convention
3. Calculates exactly 140 days
4. Returns $22,847.22 per million

## Test Results

### With Description Only
```
Description: ECOPETROL SA, 5.875%, 28-May-2045
Accrued: $22,810.75 (139.8 days)
Status: ❌ $36.47 difference
```

### With ISIN
```
ISIN: US279158AJ82
Accrued: $22,847.22 (140.0 days)
Status: ✅ Exact match
```

## Recommendations
1. **For accurate results**: Always use ISIN when available
2. **Alternative**: Use the exact description format from validated database: "ECOPET 5 ⅞ 05/28/45"
3. **Long-term fix**: Improve the parser to handle various description formats more accurately

## Technical Details
- **Coupon**: 5.875% annual (2.9375% semi-annual)
- **Previous coupon**: November 28, 2024
- **Settlement**: April 18, 2025
- **Next coupon**: May 28, 2025
- **Day count**: 30/360
- **Business convention**: Unadjusted
- **Accrued days**: 140 (Nov 28 to Apr 18)
- **Accrued fraction**: 140/180 = 0.777778
- **Accrued interest**: 2.9375% × 0.777778 = 2.284722%
- **Per million**: $22,847.22