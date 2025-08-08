#!/usr/bin/env python3
"""
Check current day count conventions in validated_quantlib_bonds.db
"""

import sqlite3
import pandas as pd

print("Checking day count conventions in validated_quantlib_bonds.db")
print("=" * 80)

try:
    conn = sqlite3.connect("validated_quantlib_bonds.db")
    
    # Get unique day count conventions
    query = """
    SELECT DISTINCT fixed_day_count, COUNT(*) as count
    FROM validated_quantlib_bonds
    GROUP BY fixed_day_count
    ORDER BY count DESC
    """
    
    df = pd.read_sql_query(query, conn)
    
    print("\nCurrent day count conventions in database:")
    print("-" * 60)
    for idx, row in df.iterrows():
        print(f"{row['fixed_day_count']:<30} - {row['count']:>6} bonds")
    
    # Check a few specific examples
    print("\n" + "=" * 80)
    print("Sample bonds with each convention:")
    print("-" * 60)
    
    for day_count in df['fixed_day_count'].unique():
        if day_count:  # Skip NULL values
            sample_query = f"""
            SELECT isin, description, fixed_day_count, fixed_frequency
            FROM validated_quantlib_bonds
            WHERE fixed_day_count = '{day_count}'
            LIMIT 3
            """
            sample_df = pd.read_sql_query(sample_query, conn)
            print(f"\n{day_count}:")
            for _, bond in sample_df.iterrows():
                print(f"  - {bond['isin']}: {bond['description']}")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)
print("Convention mapping needed:")
print("  'Actual/Actual (ISMA)'  -> 'ActualActual.Bond'")
print("  'Thirty360'             -> 'Thirty360.BondBasis'")
print("  'ACT/360'               -> 'Actual360'")
print("  'ACT/365'               -> 'Actual365Fixed'")