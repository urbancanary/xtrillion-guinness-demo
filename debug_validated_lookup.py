#!/usr/bin/env python3
"""
Debug what find_isin_from_parsed_data finds
"""

import sqlite3

validated_db = "validated_quantlib_bonds.db"

print("Checking validated DB for 3% bonds maturing 2052-08-15...")
print("=" * 60)

try:
    conn = sqlite3.connect(validated_db)
    cursor = conn.cursor()
    
    # Exact query used by find_isin_from_parsed_data
    query = """
    SELECT isin, description 
    FROM validated_quantlib_bonds 
    WHERE coupon = ? 
    AND maturity = ?
    """
    
    # Check for exact match
    cursor.execute(query, (3.0, '2052-08-15'))
    results = cursor.fetchall()
    
    print(f"Found {len(results)} exact matches for coupon=3.0, maturity='2052-08-15':")
    for isin, desc in results:
        print(f"  ISIN: {isin}")
        print(f"  Desc: {desc}")
        print()
    
    # Also check what ISINs we're interested in
    print("\nChecking specific ISINs:")
    print("-" * 40)
    
    for test_isin in ['US912810TJ79', 'US91282CJZ59']:
        cursor.execute("""
        SELECT isin, description, coupon, maturity 
        FROM validated_quantlib_bonds 
        WHERE isin = ?
        """, (test_isin,))
        
        result = cursor.fetchone()
        if result:
            print(f"{test_isin}:")
            print(f"  Description: {result[1]}")
            print(f"  Coupon: {result[2]}")
            print(f"  Maturity: {result[3]}")
        else:
            print(f"{test_isin}: NOT FOUND in validated DB")
        print()
        
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")