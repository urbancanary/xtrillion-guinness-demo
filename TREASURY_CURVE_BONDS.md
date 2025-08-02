# US Treasury Yield Curve Construction

## Overview

The US Treasury yield curve is constructed using **"on-the-run" Treasury securities** - the most recently auctioned Treasury bonds at each maturity point. These are the most liquid and actively traded Treasuries.

## Current On-The-Run Securities (as of August 2025)

### Bills (Less than 1 year)
- **4-week (1-month)**: Auctioned weekly
- **8-week (2-month)**: Auctioned weekly  
- **13-week (3-month)**: Auctioned weekly
- **26-week (6-month)**: Auctioned weekly
- **52-week (1-year)**: Auctioned monthly

### Notes (2-10 years)
- **2-year**: Auctioned monthly
- **3-year**: Auctioned quarterly
- **5-year**: Auctioned monthly
- **7-year**: Auctioned monthly
- **10-year**: Auctioned quarterly (Feb, May, Aug, Nov)

### Bonds (20-30 years)
- **20-year**: Auctioned quarterly (Feb, May, Aug, Nov)
- **30-year**: Auctioned quarterly (Feb, May, Aug, Nov)

## Example Current On-The-Run Treasuries (August 2025)

| Maturity | CUSIP | Coupon | Maturity Date | Issue Date |
|----------|--------|---------|---------------|------------|
| 3-month | 912797KZ9 | 0.000% | 2025-10-30 | 2025-07-31 |
| 6-month | 912797LM7 | 0.000% | 2026-01-29 | 2025-07-31 |
| 2-year | 91282CHH1 | 4.750% | 2027-07-31 | 2025-07-31 |
| 5-year | 91282CHG3 | 4.375% | 2030-07-31 | 2025-07-31 |
| 10-year | 91282CHF5 | 4.250% | 2035-05-15 | 2025-05-15 |
| 30-year | 912810TK6 | 4.500% | 2055-05-15 | 2025-05-15 |

*Note: These are example CUSIPs - actual on-the-run securities change with each auction*

## Yield Curve Construction Methodology

1. **Data Collection**: At ~3:30 PM ET each trading day, the Federal Reserve Bank of New York collects bid-side market price quotations for on-the-run securities.

2. **Price to Yield Conversion**: Prices are converted to yields using standard bond mathematics.

3. **Interpolation**: The Treasury uses a **monotone convex spline** method to interpolate between the observed yields to create a smooth curve.

4. **Par Yield Calculation**: The resulting curve represents par yields (the coupon rate at which a bond would trade at par).

## Key Points

- **On-The-Run vs Off-The-Run**: Only the most recently issued securities are used, as they are the most liquid and best represent current market conditions.

- **Benchmark Status**: These securities serve as benchmarks for pricing other fixed income securities.

- **Daily Updates**: The curve is updated every business day after market close.

- **No Negative Yields**: The Treasury floors all yields at zero (no negative yields accepted).

## Data Sources

1. **Official Treasury Data**: 
   - https://home.treasury.gov/resource-center/data-chart-center/interest-rates
   - Updated daily around 4:00 PM ET

2. **Federal Reserve Economic Data (FRED)**:
   - https://fred.stlouisfed.org/
   - Provides historical yield curve data

3. **TreasuryDirect API**:
   - https://data.treasury.gov/
   - Machine-readable formats (JSON, XML)

## Implementation Notes

- The `tsys_enhanced` table stores the interpolated yield curve points, not individual bond data
- Updates should occur after 4:00 PM ET to ensure data availability
- Weekend/holiday handling is important - no new data on non-business days
- The curve represents a "risk-free" benchmark for USD-denominated fixed income