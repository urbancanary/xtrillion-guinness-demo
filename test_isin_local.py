#!/usr/bin/env python3
"""
Local test of ISIN lookup implementation
"""

from bond_master_hierarchy_enhanced import calculate_bond_master
import json

# Test cases
test_cases = [
    {
        "name": "ISIN only - not in database",
        "args": {
            "isin": "XX9999999999",
            "price": 71.66,
            "settlement_date": "2025-08-01"
        }
    },
    {
        "name": "ISIN only - valid Treasury",
        "args": {
            "isin": "US912810TJ79",
            "price": 71.66,
            "settlement_date": "2025-08-01"
        }
    },
    {
        "name": "Invalid ISIN with description",
        "args": {
            "isin": "XX9999999999",
            "description": "T 3 15/08/52",
            "price": 71.66,
            "settlement_date": "2025-08-01"
        }
    }
]

# Database paths
DB_PATH = "bonds_data.db"
VALIDATED_DB = "validated_quantlib_bonds.db"
BLOOMBERG_DB = "bloomberg_index.db"

print("🧪 Local ISIN Lookup Test")
print("=" * 60)

for test in test_cases:
    print(f"\n{test['name']}")
    print("-" * 40)
    
    result = calculate_bond_master(
        isin=test['args'].get('isin'),
        description=test['args'].get('description'),
        price=test['args'].get('price'),
        settlement_date=test['args'].get('settlement_date'),
        db_path=DB_PATH,
        validated_db_path=VALIDATED_DB,
        bloomberg_db_path=BLOOMBERG_DB
    )
    
    if result.get('success'):
        print("✅ Success")
        print(f"  YTM: {result.get('ytm', 'N/A')}")
        print(f"  Duration: {result.get('duration', 'N/A')}")
        print(f"  Route: {result.get('route_used', 'N/A')}")
    else:
        print("❌ Error")
        print(f"  Status: {result.get('status', 'N/A')}")
        print(f"  Message: {result.get('message', 'N/A')}")
        if result.get('suggestions'):
            print("  Suggestions:")
            for s in result.get('suggestions', []):
                print(f"    - {s}")
    
    print()