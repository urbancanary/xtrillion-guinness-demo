import QuantLib as ql

# Setup
settlement = ql.Date(18, 4, 2025)
maturity = ql.Date(15, 8, 2052)
coupon = 0.03
clean_price = 71.66  # This should be CLEAN price

ql.Settings.instance().evaluationDate = settlement

# Create bond
issue_date = ql.Date(15, 8, 2024)
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

print("Verifying Clean vs Dirty Price Usage")
print("="*50)
print(f"Input price: ${clean_price} (should be CLEAN price)")
print()

# Calculate yield from clean price
ytm = bond.bondYield(clean_price, ql.ActualActual(ql.ActualActual.Bond), ql.Compounded, ql.Semiannual)
print(f"YTM calculated from clean price: {ytm*100:.6f}%")

# Get accrued interest
accrued = bond.accruedAmount()
print(f"Accrued interest: ${accrued:.6f}")

# Calculate dirty price
dirty_price = clean_price + accrued
print(f"Dirty price: ${clean_price:.2f} + ${accrued:.6f} = ${dirty_price:.6f}")

# Verify by calculating clean price back from YTM
calculated_dirty = bond.dirtyPrice(ytm, ql.ActualActual(ql.ActualActual.Bond), ql.Compounded, ql.Semiannual)
calculated_clean = bond.cleanPrice(ytm, ql.ActualActual(ql.ActualActual.Bond), ql.Compounded, ql.Semiannual)

print()
print("Verification:")
print(f"Calculated clean price from YTM: ${calculated_clean:.6f}")
print(f"Calculated dirty price from YTM: ${calculated_dirty:.6f}")
print(f"Clean price matches input? {abs(calculated_clean - clean_price) < 0.001}")

# Calculate duration
duration = ql.BondFunctions.duration(
    bond, ytm, ql.ActualActual(ql.ActualActual.Bond), 
    ql.Compounded, ql.Semiannual, ql.Duration.Modified
)
print(f"\nModified Duration: {duration:.6f}")

# Double check with API values
print("\nAPI Comparison:")
print(f"API clean price: $71.66")
print(f"API dirty price: $72.173812")
print(f"API accrued: $0.513812")
print(f"Our accrued: ${accrued:.6f}")
print(f"Difference in accrued: ${abs(accrued - 0.513812):.6f}")
