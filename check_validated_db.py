#!/usr/bin/env python3
"""
Check what ISINs the validated DB has for 3% bonds maturing in 2052
"""

import sqlite3

validated_db = "validated_quantlib_bonds.db"

try:
    conn = sqlite3.connect(validated_db)
    cursor = conn.cursor()
    
    # Look for 3% bonds maturing in 2052
    query = """
    SELECT isin, description, coupon, maturity 
    FROM validated_bonds 
    WHERE coupon = 3.0 
    AND maturity LIKE '%2052%'
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print("3% Bonds maturing in 2052 in validated DB:")
    print("=" * 60)
    
    for isin, desc, coupon, maturity in results:
        print(f"ISIN: {isin}")
        print(f"  Description: {desc}")
        print(f"  Coupon: {coupon}")
        print(f"  Maturity: {maturity}")
        print()
        
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    print("Trying raw query...")
    
    # Try simpler query
    try:
        conn = sqlite3.connect(validated_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Tables in validated DB: {tables}")
        conn.close()
    except Exception as e2:
        print(f"Error getting tables: {e2}")