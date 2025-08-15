#!/usr/bin/env python3
"""
Simplest possible QuantLib calculation for US Treasury
"""

import QuantLib as ql

# Parameters
settlement = ql.Date(18, 4, 2025)
maturity = ql.Date(15, 8, 2052)
coupon = 0.03
price = 71.66

print("Simple US Treasury Calculation")
print("="*40)

# Method 1: Most basic setup
issue_date = ql.Date(15, 8, 2020)  # 5 years before settlement
schedule = ql.Schedule(
    issue_date,
    maturity,
    ql.Period(ql.Semiannual),
    ql.NullCalendar(),  # No calendar adjustments
    ql.Unadjusted,
    ql.Unadjusted,
    ql.DateGeneration.Backward,
    False
)

bond = ql.FixedRateBond(
    0,  # settlement days
    100.0,
    schedule,
    [coupon],
    ql.ActualActual(ql.ActualActual.Bond)
)

# Set evaluation date to settlement
ql.Settings.instance().evaluationDate = settlement

ytm = bond.bondYield(price, ql.ActualActual(ql.ActualActual.Bond), ql.Compounded, ql.Semiannual)
duration = ql.BondFunctions.duration(bond, ytm, ql.ActualActual(ql.ActualActual.Bond), 
                                   ql.Compounded, ql.Semiannual, ql.Duration.Modified)

print(f"YTM: {ytm*100:.4f}%")
print(f"Duration: {duration:.4f}")

# Try with 30/360 day count
print("\nWith 30/360 day count:")
day_count_30_360 = ql.Thirty360(ql.Thirty360.USA)
bond30 = ql.FixedRateBond(
    0,
    100.0,
    schedule,
    [coupon],
    day_count_30_360
)

ytm30 = bond30.bondYield(price, day_count_30_360, ql.Compounded, ql.Semiannual)
duration30 = ql.BondFunctions.duration(bond30, ytm30, day_count_30_360, 
                                     ql.Compounded, ql.Semiannual, ql.Duration.Modified)

print(f"YTM: {ytm30*100:.4f}%")
print(f"Duration: {duration30:.4f}")

# Try with simple yield calculation
print("\nDirect calculation check:")
years_to_maturity = ql.ActualActual(ql.ActualActual.Bond).yearFraction(settlement, maturity)
print(f"Years to maturity: {years_to_maturity:.2f}")

# If duration should be 16.35, what would the YTM be?
print("\nReverse calculation:")
target_duration = 16.35
# Approximate: Duration ≈ (1 - (1+y/2)^(-2n)) / (y/2) for semi-annual
# For long bonds, duration ≈ 1/(y/2) - n/(1+y/2)^(2n+1)
# This is complex, so let's try different yields

for test_ytm in [0.048, 0.049, 0.050, 0.051]:
    test_dur = ql.BondFunctions.duration(bond, test_ytm, ql.ActualActual(ql.ActualActual.Bond), 
                                       ql.Compounded, ql.Semiannual, ql.Duration.Modified)
    print(f"YTM {test_ytm*100:.1f}% gives duration {test_dur:.2f}")