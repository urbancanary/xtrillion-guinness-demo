#!/usr/bin/env python3
"""Calculate accrued interest from first principles"""

from datetime import datetime

# US Treasury 3% 2052
coupon_rate = 0.03
face_value = 100
settlement_date = datetime(2025, 4, 18)

# For US Treasury maturing Aug 15, 2052
# Coupons are paid Feb 15 and Aug 15
# Semi-annual payments = 3% / 2 = 1.5% = $1.50 per $100 face

# Last coupon date before settlement (April 18, 2025)
last_coupon_date = datetime(2025, 2, 15)
next_coupon_date = datetime(2025, 8, 15)

print("US Treasury 3% 15/08/52 - Accrued Interest Calculation")
print("="*60)
print(f"Settlement Date: {settlement_date.strftime('%Y-%m-%d')}")
print(f"Coupon Rate: {coupon_rate*100}% annual")
print(f"Semi-annual coupon: ${coupon_rate * face_value / 2:.2f}")
print(f"Last Coupon: {last_coupon_date.strftime('%Y-%m-%d')}")
print(f"Next Coupon: {next_coupon_date.strftime('%Y-%m-%d')}")
print()

# Calculate days
days_since_last_coupon = (settlement_date - last_coupon_date).days
days_in_coupon_period = (next_coupon_date - last_coupon_date).days

print(f"Days since last coupon: {days_since_last_coupon}")
print(f"Days in coupon period: {days_in_coupon_period}")
print(f"Fraction of period: {days_since_last_coupon}/{days_in_coupon_period} = {days_since_last_coupon/days_in_coupon_period:.6f}")

# Method 1: Simple 30/360 day count (common for treasuries)
# Assumes 30 days per month, 360 days per year
days_30_360 = (settlement_date.year - last_coupon_date.year) * 360 + \
              (settlement_date.month - last_coupon_date.month) * 30 + \
              (min(settlement_date.day, 30) - min(last_coupon_date.day, 30))

print(f"\nUsing 30/360 day count: {days_30_360} days")
coupon_period_30_360 = 180  # 6 months = 180 days in 30/360
accrued_30_360 = (coupon_rate * face_value / 2) * (days_30_360 / coupon_period_30_360)
print(f"Accrued (30/360): ${accrued_30_360:.6f}")

# Method 2: Actual/Actual (Bond basis) - actual days
accrued_actual = (coupon_rate * face_value / 2) * (days_since_last_coupon / days_in_coupon_period)
print(f"\nUsing Actual/Actual: {days_since_last_coupon} days")
print(f"Accrued (Actual/Actual): ${accrued_actual:.6f}")

# Method 3: Actual/365
days_per_year = 365
accrued_365 = coupon_rate * face_value * (days_since_last_coupon / days_per_year)
print(f"\nUsing Actual/365: {days_since_last_coupon} days")
print(f"Accrued (Actual/365): ${accrued_365:.6f}")

print("\n" + "="*60)
print("SUMMARY:")
print(f"API Accrued Interest: $0.513812")
print(f"30/360 Calculation: ${accrued_30_360:.6f}")
print(f"Actual/Actual Calculation: ${accrued_actual:.6f}")
print(f"Actual/365 Calculation: ${accrued_365:.6f}")

# Check which is closest
api_value = 0.5138121546961326
diffs = [
    ("30/360", abs(accrued_30_360 - api_value)),
    ("Actual/Actual", abs(accrued_actual - api_value)),
    ("Actual/365", abs(accrued_365- api_value))
]
closest = min(diffs, key=lambda x: x[1])
print(f"\nClosest match: {closest[0]} (difference: ${closest[1]:.8f})")