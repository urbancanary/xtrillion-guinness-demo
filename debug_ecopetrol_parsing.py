#!/usr/bin/env python3
"""
Debug ECOPETROL parsing issue
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smart_bond_parser import SmartBondParser

def test_parsing():
    """Test parsing of ECOPETROL descriptions"""
    print("🔍 Testing ECOPETROL description parsing")
    print("=" * 60)
    
    # Initialize parser
    db_path = './bonds_data.db'
    validated_db_path = './validated_quantlib_bonds.db'
    bloomberg_db_path = './bloomberg_index.db'
    
    parser = SmartBondParser(db_path, validated_db_path, bloomberg_db_path)
    
    # Test descriptions
    descriptions = [
        "ECOPETROL SA, 5.875%, 28-May-2045",  # User format
        "ECOPET 5 ⅞ 05/28/45",  # Validated DB format
        "ECOPETROL 5.875 05/28/45",  # Alternative
        "ECOPET 5.875 05/28/2045"  # Another alternative
    ]
    
    for desc in descriptions:
        print(f"\n📝 Testing: '{desc}'")
        result = parser.parse_bond_description(desc)
        
        if result:
            print(f"   ✅ Parsed successfully:")
            print(f"      Issuer: {result.get('issuer')}")
            print(f"      Coupon: {result.get('coupon')}%")
            print(f"      Maturity: {result.get('maturity')}")
            print(f"      ISIN: {result.get('isin', 'Not found')}")
        else:
            print(f"   ❌ Failed to parse")
    
    # Check if ISIN lookup works
    print("\n\n🔍 Checking ISIN lookup in databases...")
    isin = "US279158AJ82"
    
    import sqlite3
    
    # Check primary DB
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT description, coupon, maturity_date FROM bonds WHERE isin = ?", (isin,))
            result = cursor.fetchone()
            if result:
                print(f"\n📁 Primary DB:")
                print(f"   Description: {result[0]}")
                print(f"   Coupon: {result[1]}")
                print(f"   Maturity: {result[2]}")
    except Exception as e:
        print(f"❌ Primary DB error: {e}")
    
    # Check validated DB
    try:
        with sqlite3.connect(validated_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT description, coupon, maturity FROM validated_quantlib_bonds WHERE isin = ?", (isin,))
            result = cursor.fetchone()
            if result:
                print(f"\n📁 Validated DB:")
                print(f"   Description: {result[0]}")
                print(f"   Coupon: {result[1]}")
                print(f"   Maturity: {result[2]}")
    except Exception as e:
        print(f"❌ Validated DB error: {e}")

if __name__ == "__main__":
    test_parsing()