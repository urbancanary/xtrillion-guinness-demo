#!/usr/bin/env python3
"""
Check what conventions are in the database for the treasury bond
"""

import sqlite3

print("Checking database conventions for Treasury bonds...")
print("=" * 60)

# Check validated database
try:
    conn = sqlite3.connect("validated_quantlib_bonds.db")
    cursor = conn.cursor()
    
    # Look for our specific ISINs
    query = """
    SELECT isin, description, fixed_business_convention, business_day_convention,
           fixed_day_count, day_count, fixed_frequency
    FROM validated_quantlib_bonds
    WHERE isin IN ('US912810TJ79', 'US91282CJZ59')
    OR (coupon = 3.0 AND maturity = '2052-08-15')
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print(f"Found {len(results)} matches:")
    for row in results:
        print(f"\nISIN: {row[0]}")
        print(f"  Description: {row[1]}")
        print(f"  fixed_business_convention: {row[2]}")
        print(f"  business_day_convention: {row[3]}")
        print(f"  fixed_day_count: {row[4]}")
        print(f"  day_count: {row[5]}")
        print(f"  fixed_frequency: {row[6]}")
        
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("KEY FINDING:")
print("The validated database has 'fixed_business_convention: Unadjusted'")
print("But TREASURY_CONVENTIONS only sets 'business_day_convention: Following'")
print("This is why we get different results!")