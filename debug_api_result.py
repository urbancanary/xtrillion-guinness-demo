#!/usr/bin/env python3
"""
Debug what the API calculation engine actually returns
Test the exact calculate_bond_master call that the API makes
"""

import sys
import os
sys.path.append('.')

from bond_master_hierarchy_enhanced import calculate_bond_master
import json

def test_api_calculation_directly():
    """Test the exact calculation call that the API makes"""
    
    # Exact parameters like the API uses
    description = "ECOPETROL SA, 5.875%, 28-May-2045"
    price = 69.31
    settlement_date = "2025-07-31"
    db_path = "./bonds_data.db"
    validated_db_path = "./validated_quantlib_bonds.db"
    bloomberg_db_path = "./bloomberg_index.db"
    
    print("🧪 Testing calculate_bond_master directly (API call)...")
    print(f"📊 Bond: {description}")
    print(f"💰 Price: {price}")
    print(f"📅 Settlement: {settlement_date}")
    
    try:
        # Call the exact function the API calls
        result = calculate_bond_master(
            isin=None,
            description=description,
            price=price,
            settlement_date=settlement_date,
            db_path=db_path,
            validated_db_path=validated_db_path,
            bloomberg_db_path=bloomberg_db_path
        )
        
        print(f"\n📋 Result type: {type(result)}")
        
        if isinstance(result, dict):
            print(f"🔍 All result keys: {list(result.keys())}")
            
            # Focus on spread-related fields
            spread_fields = {}
            for key, value in result.items():
                if 'spread' in key.lower():
                    spread_fields[key] = value
            
            print(f"💰 Spread-related fields: {spread_fields}")
            
            # Check other important fields
            important_fields = ['ytm', 'duration', 'spread', 'z_spread', 'z_spread_semi', 'success', 'error']
            for field in important_fields:
                if field in result:
                    print(f"🔑 {field}: {result[field]}")
                else:
                    print(f"❌ Missing field: {field}")
                    
        else:
            print(f"❌ Result is not a dict: {result}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_calculation_directly()
