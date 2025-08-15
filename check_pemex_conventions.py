#!/usr/bin/env python3
"""
Check PEMEX bond conventions and settlement date handling
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google_analysis10 import process_bond_portfolio
import QuantLib as ql

print("🔍 Checking PEMEX bond conventions and holiday adjustment")
print("=" * 60)

# Check if April 18, 2025 is a holiday
settlement_date = ql.Date(18, 4, 2025)
calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)

print(f"\n📅 Settlement date analysis:")
print(f"   Requested date: {settlement_date} (April 18, 2025)")
print(f"   Is holiday: {calendar.isHoliday(settlement_date)}")
print(f"   Holiday name: Good Friday")
print(f"   Following adjustment: {calendar.adjust(settlement_date, ql.Following)}")
print(f"   Preceding adjustment: {calendar.adjust(settlement_date, ql.Preceding)}")
print(f"   ModifiedFollowing adjustment: {calendar.adjust(settlement_date, ql.ModifiedFollowing)}")

# Create portfolio data
portfolio_data = {
    "data": [
        {
            "description": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060",
            "CLOSING PRICE": 100.0,
            "WEIGHTING": 100.0
        }
    ]
}

# Database paths
db_path = './bonds_data.db'
validated_db_path = './validated_quantlib_bonds.db'
bloomberg_db_path = './bloomberg_index.db'

print(f"\n📊 Processing PEMEX bond to see conventions...")

# Process with April 17 (non-holiday) to see the difference
print(f"\n1️⃣ Testing with April 17, 2025 (non-holiday):")
results_apr17 = process_bond_portfolio(
    portfolio_data,
    db_path,
    validated_db_path,
    bloomberg_db_path,
    settlement_days=0,
    settlement_date="2025-04-17"
)

if len(results_apr17) > 0:
    result = results_apr17[0]
    accrued = float(result.get('accrued_interest', 0))
    accrued_per_million = accrued * 10000
    print(f"   Accrued interest: {accrued:.6f}%")
    print(f"   Accrued per million: ${accrued_per_million:,.2f}")
    
    # Calculate implied days
    semi_annual_coupon = 6.95 / 2.0
    implied_days = (accrued / semi_annual_coupon) * 180
    print(f"   Implied days: {implied_days:.1f}")

# Process with April 18 (holiday)
print(f"\n2️⃣ Testing with April 18, 2025 (holiday - Good Friday):")
results_apr18 = process_bond_portfolio(
    portfolio_data,
    db_path,
    validated_db_path,
    bloomberg_db_path,
    settlement_days=0,
    settlement_date="2025-04-18"
)

if len(results_apr18) > 0:
    result = results_apr18[0]
    accrued = float(result.get('accrued_interest', 0))
    accrued_per_million = accrued * 10000
    print(f"   Accrued interest: {accrued:.6f}%")
    print(f"   Accrued per million: ${accrued_per_million:,.2f}")
    
    # Calculate implied days
    semi_annual_coupon = 6.95 / 2.0
    implied_days = (accrued / semi_annual_coupon) * 180
    print(f"   Implied days: {implied_days:.1f}")

# Process with April 21 (following business day)
print(f"\n3️⃣ Testing with April 21, 2025 (next business day):")
results_apr21 = process_bond_portfolio(
    portfolio_data,
    db_path,
    validated_db_path,
    bloomberg_db_path,
    settlement_days=0,
    settlement_date="2025-04-21"
)

if len(results_apr21) > 0:
    result = results_apr21[0]
    accrued = float(result.get('accrued_interest', 0))
    accrued_per_million = accrued * 10000
    print(f"   Accrued interest: {accrued:.6f}%")
    print(f"   Accrued per million: ${accrued_per_million:,.2f}")
    
    # Calculate implied days
    semi_annual_coupon = 6.95 / 2.0
    implied_days = (accrued / semi_annual_coupon) * 180
    print(f"   Implied days: {implied_days:.1f}")

print(f"\n💡 Analysis:")
print(f"   The system appears to be using business day conventions")
print(f"   April 18 (holiday) → April 21 (next business day)")
print(f"   This explains the 83 days vs 80 days difference")

print(f"\n📋 Recommendation:")
print(f"   For bonds, accrued interest is typically calculated to the")
print(f"   actual settlement date, regardless of holidays.")
print(f"   We should disable business day adjustment for accrued calculations.")