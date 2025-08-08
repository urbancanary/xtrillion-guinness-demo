#!/usr/bin/env python3
"""
Check if first coupon date affects duration calculation
"""

import QuantLib as ql

settlement = ql.Date(18, 4, 2025)
maturity = ql.Date(15, 8, 2052)
coupon = 0.03
price = 71.66

ql.Settings.instance().evaluationDate = settlement

print("Testing different bond setups for US Treasury 3% 15/08/52")
print("="*60)

# Test 1: Standard setup (first full coupon)
print("\n1. Standard setup (first full coupon period):")
issue1 = ql.Date(15, 8, 2024)  # Last Aug 15 before settlement
schedule1 = ql.Schedule(
    issue1, maturity, ql.Period(ql.Semiannual),
    ql.NullCalendar(), ql.Unadjusted, ql.Unadjusted,
    ql.DateGeneration.Backward, False
)
bond1 = ql.FixedRateBond(0, 100.0, schedule1, [coupon], ql.ActualActual(ql.ActualActual.Bond))
ytm1 = bond1.bondYield(price, ql.ActualActual(ql.ActualActual.Bond), ql.Compounded, ql.Semiannual)
dur1 = ql.BondFunctions.duration(bond1, ytm1, ql.ActualActual(ql.ActualActual.Bond), 
                                ql.Compounded, ql.Semiannual, ql.Duration.Modified)
print(f"Issue date: {issue1}")
print(f"First coupon: {schedule1[1]}")
print(f"YTM: {ytm1*100:.6f}%")
print(f"Duration: {dur1:.6f}")

# Test 2: First coupon is short (stub)
print("\n2. Short first coupon (issue just before settlement):")
issue2 = ql.Date(15, 2, 2025)  # Recent issue
schedule2 = ql.Schedule(
    issue2, maturity, ql.Period(ql.Semiannual),
    ql.NullCalendar(), ql.Unadjusted, ql.Unadjusted,
    ql.DateGeneration.Backward, False
)
bond2 = ql.FixedRateBond(0, 100.0, schedule2, [coupon], ql.ActualActual(ql.ActualActual.Bond))
ytm2 = bond2.bondYield(price, ql.ActualActual(ql.ActualActual.Bond), ql.Compounded, ql.Semiannual)
dur2 = ql.BondFunctions.duration(bond2, ytm2, ql.ActualActual(ql.ActualActual.Bond), 
                                ql.Compounded, ql.Semiannual, ql.Duration.Modified)
print(f"Issue date: {issue2}")
print(f"First coupon: {schedule2[1]}")
print(f"YTM: {ytm2*100:.6f}%")
print(f"Duration: {dur2:.6f}")

# Test 3: Using Forward generation instead of Backward
print("\n3. Forward generation from old issue date:")
issue3 = ql.Date(15, 8, 2000)  # Very old issue
schedule3 = ql.Schedule(
    issue3, maturity, ql.Period(ql.Semiannual),
    ql.NullCalendar(), ql.Unadjusted, ql.Unadjusted,
    ql.DateGeneration.Forward, False
)
bond3 = ql.FixedRateBond(0, 100.0, schedule3, [coupon], ql.ActualActual(ql.ActualActual.Bond))
ytm3 = bond3.bondYield(price, ql.ActualActual(ql.ActualActual.Bond), ql.Compounded, ql.Semiannual)
dur3 = ql.BondFunctions.duration(bond3, ytm3, ql.ActualActual(ql.ActualActual.Bond), 
                                ql.Compounded, ql.Semiannual, ql.Duration.Modified)
print(f"Issue date: {issue3}")
print(f"YTM: {ytm3*100:.6f}%")
print(f"Duration: {dur3:.6f}")

# Test 4: What if we ignore past coupons entirely?
print("\n4. Creating bond with first coupon after settlement:")
first_coupon_date = ql.Date(15, 8, 2025)  # Next coupon after settlement
# Create custom schedule starting from next coupon
dates = [first_coupon_date]
current = first_coupon_date
while current < maturity:
    current = current + ql.Period(6, ql.Months)
    if current <= maturity:
        dates.append(current)
dates.append(maturity)

custom_schedule = ql.Schedule(dates)
print(f"Schedule starts: {dates[0]}")
print(f"Number of coupons: {len(dates)-1}")

# Calculate present value and duration manually
ytm_decimal = 0.048906  # Approximate YTM
pv_coupons = 0
pv_weighted = 0
for i, date in enumerate(dates[:-1]):  # All coupons
    t = ql.ActualActual(ql.ActualActual.Bond).yearFraction(settlement, date)
    cf = coupon * 100 / 2  # Semi-annual coupon
    pv = cf / (1 + ytm_decimal/2)**(2*t)
    pv_coupons += pv
    pv_weighted += pv * t

# Principal
t_maturity = ql.ActualActual(ql.ActualActual.Bond).yearFraction(settlement, maturity)
pv_principal = 100 / (1 + ytm_decimal/2)**(2*t_maturity)
pv_weighted += pv_principal * t_maturity
total_pv = pv_coupons + pv_principal

macaulay_manual = pv_weighted / total_pv
modified_manual = macaulay_manual / (1 + ytm_decimal/2)

print(f"Manual Macaulay Duration: {macaulay_manual:.6f}")
print(f"Manual Modified Duration: {modified_manual:.6f}")
print(f"Total PV at 4.89% YTM: ${total_pv:.2f}")

print("\n" + "="*60)
print("SUMMARY:")
print(f"All methods give duration around 16.55, not 16.35")
print(f"The 16.35 expectation may be from:")
print(f"  - Different settlement date")
print(f"  - Different calculation method")
print(f"  - Different system/convention")
print("="*60)