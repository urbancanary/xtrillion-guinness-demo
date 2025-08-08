import QuantLib as ql

# Simple duration calculation
settlement = ql.Date(18, 4, 2025)
maturity = ql.Date(15, 8, 2052)
ytm = 0.04890641  # From API

# Years to maturity
years = ql.ActualActual(ql.ActualActual.Bond).yearFraction(settlement, maturity)
print(f"Years to maturity: {years:.6f}")

# Simple Macaulay duration approximation
# For a bond trading well below par with many years to maturity
# Macaulay ≈ Years to maturity * (1 - price/100) + price/100 * 1/ytm
price = 71.66
mac_approx = years * (1 - price/100) + (price/100) * (1/ytm)
print(f"Macaulay approximation: {mac_approx:.2f}")

# Modified duration = Macaulay / (1 + ytm/2)
mod_approx = mac_approx / (1 + ytm/2)
print(f"Modified approximation: {mod_approx:.2f}")

# Duration of a zero-coupon bond = time to maturity
zero_duration = years / (1 + ytm/2)
print(f"Zero-coupon duration: {zero_duration:.2f}")
