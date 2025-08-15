#!/usr/bin/env python3
"""
Find what parameters would give duration = 16.35
"""

import QuantLib as ql

# Setup
settlement = ql.Date(18, 4, 2025)
maturity = ql.Date(15, 8, 2052)
coupon = 0.03
target_duration = 16.35

ql.Settings.instance().evaluationDate = settlement

# Create bond
issue_date = ql.Date(15, 8, 2020)
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

print("Finding parameters for duration = 16.35")
print("="*50)

# Test 1: What price gives duration 16.35?
print("\nTest 1: Finding price that gives duration 16.35")
print("(Using binary search)")

low_price = 60.0
high_price = 80.0

for i in range(20):
    mid_price = (low_price + high_price) / 2
    ytm = bond.bondYield(mid_price, ql.ActualActual(ql.ActualActual.Bond), ql.Compounded, ql.Semiannual)
    duration = ql.BondFunctions.duration(bond, ytm, ql.ActualActual(ql.ActualActual.Bond), 
                                       ql.Compounded, ql.Semiannual, ql.Duration.Modified)
    
    if abs(duration - target_duration) < 0.001:
        print(f"Found! Price ${mid_price:.4f} gives duration {duration:.4f}")
        print(f"YTM: {ytm*100:.4f}%")
        break
    elif duration > target_duration:
        low_price = mid_price
    else:
        high_price = mid_price
    
    if i < 5 or i == 19:
        print(f"  Price ${mid_price:.2f} → Duration {duration:.4f}")

# Test 2: Check if different settlement date gives 16.35
print("\n\nTest 2: Different settlement dates with price 71.66")
test_dates = [
    ql.Date(18, 10, 2024),  # 6 months earlier
    ql.Date(18, 1, 2025),   # 3 months earlier
    ql.Date(18, 7, 2025),   # 3 months later
    ql.Date(18, 10, 2025),  # 6 months later
    ql.Date(18, 4, 2026),   # 1 year later
]

for test_date in test_dates:
    ql.Settings.instance().evaluationDate = test_date
    ytm = bond.bondYield(71.66, ql.ActualActual(ql.ActualActual.Bond), ql.Compounded, ql.Semiannual)
    duration = ql.BondFunctions.duration(bond, ytm, ql.ActualActual(ql.ActualActual.Bond), 
                                       ql.Compounded, ql.Semiannual, ql.Duration.Modified)
    print(f"Settlement {test_date}: Duration = {duration:.4f}")

# Test 3: What if we use a different coupon?
print("\n\nTest 3: Different coupons with price 71.66")
ql.Settings.instance().evaluationDate = settlement

for test_coupon in [0.025, 0.0275, 0.03, 0.0325, 0.035]:
    bond_test = ql.FixedRateBond(
        0,
        100.0,
        schedule,
        [test_coupon],
        ql.ActualActual(ql.ActualActual.Bond)
    )
    ytm = bond_test.bondYield(71.66, ql.ActualActual(ql.ActualActual.Bond), ql.Compounded, ql.Semiannual)
    duration = ql.BondFunctions.duration(bond_test, ytm, ql.ActualActual(ql.ActualActual.Bond), 
                                       ql.Compounded, ql.Semiannual, ql.Duration.Modified)
    print(f"Coupon {test_coupon*100:.2f}%: Duration = {duration:.4f}, YTM = {ytm*100:.4f}%")