#!/usr/bin/env python3
"""
Debug PEMEX accrued interest calculation
"""

import QuantLib as ql
from datetime import datetime

# PEMEX bond parameters
coupon = 6.95
maturity_date = datetime(2060, 1, 28)
settlement_date_str = "2025-04-18"
settlement_date = datetime.strptime(settlement_date_str, '%Y-%m-%d')

# Convert to QuantLib dates
ql_settlement = ql.Date(settlement_date.day, settlement_date.month, settlement_date.year)
ql_maturity = ql.Date(maturity_date.day, maturity_date.month, maturity_date.year)

# Set evaluation date
ql.Settings.instance().evaluationDate = ql_settlement

# Create calendar and conventions
calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
day_counter = ql.Thirty360(ql.Thirty360.BondBasis)
frequency = ql.Semiannual

print(f"🔍 Debugging PEMEX accrued interest calculation")
print(f"   Settlement date: {settlement_date_str}")
print(f"   Maturity date: {maturity_date.strftime('%Y-%m-%d')}")
print(f"   Coupon: {coupon}%")
print(f"   Day count: 30/360")
print()

# Create schedule starting well before settlement
schedule_start = ql_settlement
for i in range(20):  # Go back 10 years
    schedule_start = calendar.advance(schedule_start, ql.Period(-6, ql.Months))

print(f"📅 Creating schedule from {schedule_start} to {ql_maturity}")

# Create schedule
schedule = ql.Schedule(
    schedule_start,
    ql_maturity,
    ql.Period(frequency),
    calendar,
    ql.Following,
    ql.Following,
    ql.DateGeneration.Backward,
    False
)

print(f"   Schedule has {len(schedule)} dates")

# Find coupon dates around settlement
print(f"\n🔍 Finding coupon dates around settlement...")
for i in range(len(schedule) - 1):
    if schedule[i] <= ql_settlement <= schedule[i + 1]:
        prev_coupon = schedule[i]
        next_coupon = schedule[i + 1]
        print(f"   Previous coupon: {prev_coupon}")
        print(f"   Settlement:      {ql_settlement}")
        print(f"   Next coupon:     {next_coupon}")
        
        # Calculate days manually
        days_accrued = day_counter.dayCount(prev_coupon, ql_settlement)
        days_in_period = day_counter.dayCount(prev_coupon, next_coupon)
        
        print(f"\n📊 Day count calculation:")
        print(f"   Days from {prev_coupon} to {ql_settlement}: {days_accrued}")
        print(f"   Days in period: {days_in_period}")
        print(f"   Accrued fraction: {days_accrued/days_in_period:.6f}")
        
        # Calculate accrued interest
        semi_annual_coupon = coupon / 2.0
        accrued_interest = semi_annual_coupon * (days_accrued / days_in_period)
        accrued_per_million = accrued_interest * 10000
        
        print(f"\n💰 Accrued interest calculation:")
        print(f"   Semi-annual coupon: {semi_annual_coupon}%")
        print(f"   Accrued interest: {accrued_interest:.6f}%")
        print(f"   Accrued per million: ${accrued_per_million:,.2f}")
        break

# Create bond with settlement days = 0
print(f"\n🏦 Creating bond with settlement_days = 0...")
bond = ql.FixedRateBond(
    0,  # settlement days
    100.0,  # face value
    schedule,
    [coupon / 100.0],  # coupon as decimal
    day_counter
)

# Check accrued amount
accrued = bond.accruedAmount()
print(f"\n✅ Bond.accruedAmount(): {accrued:.6f}")
print(f"   Accrued per million: ${accrued * 10000:,.2f}")

# Also check with explicit reference date
accrued_ref = bond.accruedAmount(ql_settlement)
print(f"\n✅ Bond.accruedAmount(settlement_date): {accrued_ref:.6f}")
print(f"   Accrued per million: ${accrued_ref * 10000:,.2f}")

print(f"\n💡 User's expected calculation:")
print(f"   80 days from Jan 28 to Apr 18")
print(f"   80/180 * 3.475% = 1.544444%")
print(f"   $15,444.44 per million")