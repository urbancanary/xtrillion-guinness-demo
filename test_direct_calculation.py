#!/usr/bin/env python3
"""
🧪 Direct Bond Calculation Test
Test calculate_bond_master directly without API
"""

import sys
import os
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

from bond_master_hierarchy_enhanced import calculate_bond_master
import json
from datetime import datetime

def test_direct_calculation():
    """Test the same bond from API test directly"""
    
    print("🧪 DIRECT CALCULATION TEST")
    print("=" * 50)
    print("Bond: T 3 15/08/52")
    print("Price: 71.66")
    print("=" * 50)
    print()
    
    try:
        # Test with the enhanced calculate_bond_master function
        result = calculate_bond_master(
            isin=None,  # No ISIN - will use parse hierarchy
            description="T 3 15/08/52",
            price=71.66,
            settlement_date=None,  # Use default
            db_path='./bonds_data.db',
            validated_db_path='./validated_quantlib_bonds.db',
            bloomberg_db_path='./bloomberg_index.db'
        )
        
        print("✅ CALCULATION SUCCESSFUL!")
        print()
        print("📊 FULL RESULT:")
        print(json.dumps(result, indent=2, default=str))
        
        # Extract key metrics for comparison
        if 'analytics' in result and result['analytics']:
            analytics = result['analytics']
            print()
            print("🔍 KEY METRICS COMPARISON:")
            print(f"   Annual Yield: {analytics.get('annual_yield', 'N/A')}%")
            print(f"   Duration: {analytics.get('annual_duration', 'N/A')} years")
            print(f"   Clean Price: {analytics.get('clean_price', 'N/A')}")
            print(f"   Dirty Price: {analytics.get('dirty_price', 'N/A')}")
            print(f"   Accrued Interest: {analytics.get('accrued_interest', 'N/A')}")
        
        # Check for any errors or warnings
        if 'status' in result:
            print(f"   Status: {result['status']}")
        
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
            
        if 'warnings' in result and result['warnings']:
            print(f"   ⚠️ Warnings: {result['warnings']}")
            
    except Exception as e:
        print(f"❌ CALCULATION FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_calculation()
