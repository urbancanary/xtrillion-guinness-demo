#!/usr/bin/env python3
"""
Standalone QuantLib calculation for US Treasury 3% 15/08/52
Settlement: 18-Apr-2025
Expected Duration: 16.35
"""

import QuantLib as ql

print("="*60)
print("US Treasury 3% 15/08/52 - Standalone QuantLib Calculation")
print("="*60)

# Bond parameters
settlement_date = ql.Date(18, 4, 2025)
maturity_date = ql.Date(15, 8, 2052)
issue_date = ql.Date(15, 8, 2022)  # Assuming a recent issue
coupon_rate = 0.03
price = 71.66

print(f"Settlement Date: {settlement_date}")
print(f"Maturity Date: {maturity_date}")
print(f"Coupon Rate: {coupon_rate*100}%")
print(f"Price: ${price}")
print()

# Set evaluation date
ql.Settings.instance().evaluationDate = settlement_date

# Calendar and day count
calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
day_count = ql.ActualActual(ql.ActualActual.Bond)
business_convention = ql.Unadjusted
end_of_month = False

# Create schedule
schedule = ql.Schedule(
    issue_date,
    maturity_date,
    ql.Period(ql.Semiannual),
    calendar,
    business_convention,
    business_convention,
    ql.DateGeneration.Backward,
    end_of_month
)

# Create bond
bond = ql.FixedRateBond(
    0,  # settlement days (we're using settlement date directly)
    100.0,  # face amount
    schedule,
    [coupon_rate],  # coupon rate
    day_count
)

# Calculate yield (no pricing engine needed for yield calculation)
compounding = ql.Compounded
frequency = ql.Semiannual
ytm = bond.bondYield(price, day_count, compounding, frequency)

print(f"Yield to Maturity: {ytm*100:.6f}%")

# Calculate durations
modified_duration = ql.BondFunctions.duration(
    bond,
    ytm,
    day_count,
    compounding,
    frequency,
    ql.Duration.Modified
)

macaulay_duration = ql.BondFunctions.duration(
    bond,
    ytm,
    day_count,
    compounding,
    frequency,
    ql.Duration.Macaulay
)

# Calculate other metrics
convexity = ql.BondFunctions.convexity(
    bond,
    ytm,
    day_count,
    compounding,
    frequency
)

# Accrued interest
accrued = bond.accruedAmount()
clean_price = price
dirty_price = clean_price + accrued

print(f"Modified Duration: {modified_duration:.6f}")
print(f"Macaulay Duration: {macaulay_duration:.6f}")
print(f"Convexity: {convexity:.6f}")
print(f"Accrued Interest: ${accrued:.6f}")
print(f"Clean Price: ${clean_price:.2f}")
print(f"Dirty Price: ${dirty_price:.6f}")

# Try alternative calculation methods
print("\n" + "-"*60)
print("Alternative Calculations:")
print("-"*60)

# Method 2: Using BondFunctions directly
print("\nMethod 2 - BondFunctions with settlement date:")
mod_dur2 = ql.BondFunctions.duration(
    bond,
    ytm,
    day_count,
    compounding,
    frequency,
    ql.Duration.Modified,
    settlement_date
)
print(f"Modified Duration: {mod_dur2:.6f}")

# Method 3: Different settlement days
print("\nMethod 3 - With 2 settlement days:")
bond2 = ql.FixedRateBond(
    2,  # settlement days
    100.0,
    schedule,
    [coupon_rate],
    day_count
)
ytm2 = bond2.bondYield(price, day_count, compounding, frequency, settlement_date)
mod_dur3 = ql.BondFunctions.duration(
    bond2,
    ytm2,
    day_count,
    compounding,
    frequency,
    ql.Duration.Modified,
    settlement_date
)
print(f"YTM: {ytm2*100:.6f}%")
print(f"Modified Duration: {mod_dur3:.6f}")

# Method 4: Try without end of month adjustment
print("\nMethod 4 - With end_of_month = True:")
schedule4 = ql.Schedule(
    issue_date,
    maturity_date,
    ql.Period(ql.Semiannual),
    calendar,
    business_convention,
    business_convention,
    ql.DateGeneration.Backward,
    True  # end of month
)
bond4 = ql.FixedRateBond(0, 100.0, schedule4, [coupon_rate], day_count)
ytm4 = bond4.bondYield(price, day_count, compounding, frequency)
mod_dur4 = ql.BondFunctions.duration(
    bond4,
    ytm4,
    day_count,
    compounding,
    frequency,
    ql.Duration.Modified
)
print(f"YTM: {ytm4*100:.6f}%")
print(f"Modified Duration: {mod_dur4:.6f}")

print("\n" + "="*60)
print("SUMMARY:")
print(f"Expected Duration: 16.35")
print(f"Calculated Duration: {modified_duration:.2f}")
print(f"Difference: {abs(16.35 - modified_duration):.2f}")
print("="*60)