import QuantLib as ql

# Test US Treasury 3% 2052
settlement = ql.Date(18, 4, 2025)
maturity = ql.Date(15, 8, 2052)
coupon = 0.03

print("Testing US Treasury 3% 15/08/52")
print(f"Settlement: {settlement}")
print(f"Maturity: {maturity}")

# Calculate years between
years = ql.ActualActual(ql.ActualActual.Bond).yearFraction(settlement, maturity)
print(f"Years to maturity: {years:.2f}")

# Theoretical last coupon before settlement
# For Aug 15 maturity, coupons are Feb 15 and Aug 15
last_coupon = ql.Date(15, 2, 2025)  # Feb 15, 2025
next_coupon = ql.Date(15, 8, 2025)  # Aug 15, 2025

print(f"Last coupon: {last_coupon}")
print(f"Next coupon: {next_coupon}")

# Days of accrued interest
accrued_days = settlement - last_coupon
print(f"Accrued days: {accrued_days}")
