#!/usr/bin/env python3
"""
Debug z_spread specifically in production environment
"""

import sys
import os
sys.path.append('.')

from bond_master_hierarchy_enhanced import calculate_bond_master
import json

def test_z_spread_directly():
    """Test z_spread calculation specifically"""
    
    description = "ECOPETROL SA, 5.875%, 28-May-2045"
    price = 69.31
    settlement_date = "2025-07-31"
    
    print("🧪 Testing z_spread calculation specifically...")
    
    try:
        result = calculate_bond_master(
            isin=None,
            description=description,
            price=price,
            settlement_date=settlement_date,
            db_path="./bonds_data.db",
            validated_db_path="./validated_quantlib_bonds.db",
            bloomberg_db_path="./bloomberg_index.db"
        )
        
        print(f"📊 G-Spread: {result.get('spread')}")
        print(f"📊 Z-Spread: {result.get('z_spread')}")
        
        # Check all spread-related fields
        spread_fields = {}
        for key, value in result.items():
            if 'spread' in key.lower():
                spread_fields[key] = value
        
        print(f"💰 All spread fields: {json.dumps(spread_fields, indent=2, default=str)}")
        
        # Test if z_spread calculation is working
        g_spread = result.get('spread')
        if g_spread is not None:
            expected_z_spread = g_spread + 10
            actual_z_spread = result.get('z_spread')
            
            print(f"🧮 Expected Z-Spread: {expected_z_spread}")
            print(f"🧮 Actual Z-Spread: {actual_z_spread}")
            
            if actual_z_spread is None:
                print("❌ Z-Spread is None despite G-Spread being calculated!")
            elif abs(actual_z_spread - expected_z_spread) < 0.01:
                print("✅ Z-Spread calculation is correct!")
            else:
                print(f"⚠️ Z-Spread calculation discrepancy: expected {expected_z_spread}, got {actual_z_spread}")
        else:
            print("❌ G-Spread is None - spread calculation failed entirely")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_z_spread_directly()
