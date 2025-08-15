#!/usr/bin/env python3
"""Update treasury database with correct values"""

from us_treasury_yield_fetcher import USTreasuryYieldFetcher
from datetime import datetime

# Expected values from treasury website to verify
expected = {
    '2025-07-31': {'M1M': 4.49, 'M2M': 4.47, 'M3M': 4.46, 'M6M': 4.41, 'M1Y': 4.40},
    '2025-08-01': {'M1M': 4.49, 'M2M': 4.46, 'M3M': 4.44, 'M6M': 4.35, 'M1Y': 4.30}
}

fetcher = USTreasuryYieldFetcher()

# Update each date
for date_str in ['2025-07-30', '2025-07-31', '2025-08-01']:
    date = datetime.strptime(date_str, '%Y-%m-%d')
    print(f"\nUpdating {date_str}...")
    
    yields = fetcher.fetch_yield_curve_data(date)
    
    if yields:
        # Check a few values if we have expected data
        if date_str in expected:
            print("  Verifying key values:")
            for key in ['M1M', 'M2M', 'M3M', 'M6M', 'M1Y']:
                fetched = yields.get(key)
                expect = expected[date_str].get(key)
                if fetched and expect:
                    match = "✓" if abs(fetched - expect) < 0.01 else "✗"
                    print(f"    {key}: {fetched:.2f} (expected {expect:.2f}) {match}")
        
        # Update database
        success = fetcher.update_database(yields, date)
        
        if success:
            print(f"  ✓ Successfully updated {date_str}")
        else:
            print(f"  ✗ Failed to update {date_str}")
    else:
        print(f"  ✗ No yields fetched for {date_str}")

print("\nDone!")