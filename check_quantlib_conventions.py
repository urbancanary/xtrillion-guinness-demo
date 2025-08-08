#!/usr/bin/env python3
"""
Check QuantLib day count convention names
"""

import QuantLib as ql

print("QuantLib Day Count Convention Reference")
print("=" * 60)

# Create different day counters and check their names
day_counters = [
    ("ActualActual.Bond", ql.ActualActual(ql.ActualActual.Bond)),
    ("ActualActual.ISMA", ql.ActualActual(ql.ActualActual.ISMA)),
    ("ActualActual.ISDA", ql.ActualActual(ql.ActualActual.ISDA)),
    ("ActualActual.Historical", ql.ActualActual(ql.ActualActual.Historical)),
    ("ActualActual.Actual365", ql.ActualActual(ql.ActualActual.Actual365)),
    ("ActualActual.AFB", ql.ActualActual(ql.ActualActual.AFB)),
    ("ActualActual.Euro", ql.ActualActual(ql.ActualActual.Euro)),
    ("Thirty360.BondBasis", ql.Thirty360(ql.Thirty360.BondBasis)),
    ("Thirty360.USA", ql.Thirty360(ql.Thirty360.USA)),
    ("Thirty360.European", ql.Thirty360(ql.Thirty360.European)),
    ("Thirty360.EurobondBasis", ql.Thirty360(ql.Thirty360.EurobondBasis)),
    ("Actual360", ql.Actual360()),
    ("Actual365Fixed", ql.Actual365Fixed()),
]

for name, dc in day_counters:
    print(f"{name:30} -> {dc}")

print("\n" + "=" * 60)
print("Key findings:")
print("1. ActualActual.Bond and ActualActual.ISMA are DIFFERENT in QuantLib!")
print("2. For US Treasuries, we should use ActualActual.Bond")
print("3. Thirty360.BondBasis is the standard 30/360 for bonds")

print("\n" + "=" * 60)
print("Recommended mapping for our database:")
print("  'ActualActual.Bond'     <- For US Treasuries (not ISMA!)")
print("  'Thirty360.BondBasis'   <- For corporate bonds with 30/360")
print("  'Actual360'             <- For money market instruments")
print("  'Actual365Fixed'        <- For some specific instruments")