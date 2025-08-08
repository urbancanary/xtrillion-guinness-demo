#!/usr/bin/env python3
"""Test the corrected treasury fetcher"""

from us_treasury_yield_fetcher import USTreasuryYieldFetcher
from datetime import datetime

# Test dates
dates = ['2025-07-30', '2025-07-31', '2025-08-01']

fetcher = USTreasuryYieldFetcher()

for date_str in dates:
    date = datetime.strptime(date_str, '%Y-%m-%d')
    print(f"\nFetching data for {date_str}...")
    
    yields = fetcher.fetch_yield_curve_data(date)
    
    if yields:
        print("Fetched yields:")
        for tenor in ['M1M', 'M2M', 'M3M', 'M6M', 'M1Y', 'M2Y', 'M3Y', 'M5Y', 'M7Y', 'M10Y', 'M20Y', 'M30Y']:
            if tenor in yields:
                print(f"  {tenor}: {yields[tenor]:.2f}")
            else:
                print(f"  {tenor}: Missing")
    else:
        print("  ERROR: No yields fetched!")

# Now update the database with correct values
print("\nUpdating database with corrected values...")
success = fetcher.update_database_batch({
    datetime(2025, 7, 30): fetcher.fetch_yield_curve_data(datetime(2025, 7, 30)),
    datetime(2025, 7, 31): fetcher.fetch_yield_curve_data(datetime(2025, 7, 31)),
    datetime(2025, 8, 1): fetcher.fetch_yield_curve_data(datetime(2025, 8, 1))
})

if success:
    print("✓ Database updated successfully!")
else:
    print("✗ Database update failed!")