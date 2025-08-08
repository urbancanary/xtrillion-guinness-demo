#!/usr/bin/env python3
"""Test the fixed treasury fetcher"""

from us_treasury_yield_fetcher import USTreasuryYieldFetcher
from datetime import datetime

# Expected values from treasury website
expected_values = {
    '2025-07-30': {
        'M1M': 4.41, 'M2M': 4.48, 'M3M': 4.45, 'M6M': 4.41,
        'M1Y': 4.39, 'M2Y': 4.31, 'M3Y': 4.12, 'M5Y': 3.94,
        'M7Y': 3.89, 'M10Y': 3.96, 'M20Y': 4.15, 'M30Y': 4.38
    },
    '2025-07-31': {
        'M1M': 4.49, 'M2M': 4.47, 'M3M': 4.46, 'M6M': 4.41,
        'M1Y': 4.40, 'M2Y': 4.31, 'M3Y': 4.10, 'M5Y': 3.94,
        'M7Y': 3.89, 'M10Y': 3.96, 'M20Y': 4.14, 'M30Y': 4.37
    },
    '2025-08-01': {
        'M1M': 4.49, 'M2M': 4.46, 'M3M': 4.44, 'M6M': 4.35,
        'M1Y': 4.30, 'M2Y': 4.16, 'M3Y': 3.87, 'M5Y': 3.69,
        'M7Y': 3.67, 'M10Y': 3.77, 'M20Y': 3.97, 'M30Y': 4.23
    }
}

fetcher = USTreasuryYieldFetcher()

for date_str, expected in expected_values.items():
    date = datetime.strptime(date_str, '%Y-%m-%d')
    print(f"\nFetching data for {date_str}...")
    
    yields = fetcher.fetch_yield_curve_data(date)
    
    if not yields:
        print("  ERROR: No yields fetched!")
        continue
        
    print("  Comparing values:")
    print("  Tenor | Expected | Fetched | Diff")
    print("  ------|----------|---------|------")
    
    all_correct = True
    for tenor in ['M1M', 'M2M', 'M3M', 'M6M', 'M1Y', 'M2Y', 'M3Y', 'M5Y', 'M7Y', 'M10Y', 'M20Y', 'M30Y']:
        expected_val = expected.get(tenor, 'N/A')
        fetched_val = yields.get(tenor, 'N/A')
        
        if expected_val != 'N/A' and fetched_val != 'N/A':
            diff = fetched_val - expected_val
            status = "✓" if abs(diff) < 0.01 else "✗"
            all_correct = all_correct and (abs(diff) < 0.01)
            print(f"  {tenor:5} | {expected_val:8.2f} | {fetched_val:7.2f} | {diff:+5.2f} {status}")
        else:
            print(f"  {tenor:5} | {expected_val:8} | {fetched_val:7} | N/A")
            all_correct = False
    
    if all_correct:
        print("  ✓ All values match!")
    else:
        print("  ✗ Some values don't match")
        
print("\nDone.")