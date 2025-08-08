#!/usr/bin/env python3
"""Verify US Treasury calculations with June 30, 2025 settlement"""

import QuantLib as ql

# Setup with June 30, 2025 settlement
settlement = ql.Date(30, 6, 2025)
maturity = ql.Date(15, 8, 2052)
coupon = 0.03
clean_price = 71.66

ql.Settings.instance().evaluationDate = settlement

# Create bond
issue_date = ql.Date(15, 8, 2020)  # Arbitrary issue date on schedule
schedule = ql.Schedule(
    issue_date,
    maturity,
    ql.Period(ql.Semiannual),
    ql.NullCalendar(),
    ql.Unadjusted,
    ql.Unadjusted,
    ql.DateGeneration.Backward,
    False
)

bond = ql.FixedRateBond(
    0,
    100.0,
    schedule,
    [coupon],
    ql.ActualActual(ql.ActualActual.Bond)
)

print("US Treasury 3% 15/08/52 - Settlement June 30, 2025")
print("="*60)
print(f"Clean Price: ${clean_price}")
print(f"Settlement Date: {settlement}")
print()

# Calculate YTM
ytm = bond.bondYield(clean_price, ql.ActualActual(ql.ActualActual.Bond), ql.Compounded, ql.Semiannual)
print(f"Yield to Maturity: {ytm*100:.6f}%")

# Calculate duration
duration = ql.BondFunctions.duration(
    bond, ytm, ql.ActualActual(ql.ActualActual.Bond), 
    ql.Compounded, ql.Semiannual, ql.Duration.Modified
)
print(f"Modified Duration: {duration:.6f}")

# Get accrued interest
accrued = bond.accruedAmount()
print(f"Accrued Interest: ${accrued:.6f}")

print("\n" + "-"*60)
print("Expected values:")
print(f"Expected YTM: 4.898837%")
print(f"Expected Duration: 16.350751")
print()
print(f"YTM Match? {abs(ytm*100 - 4.898837) < 0.0001}")
print(f"Duration Match? {abs(duration - 16.350751) < 0.0001}")
print("="*60)