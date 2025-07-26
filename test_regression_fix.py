#!/usr/bin/env python3
"""
Test Regression Fix: Validate Method 1 and Method 2 Both Work
==============================================================

Tests the targeted fix that should restore Method 1 while preserving Treasury fix for Method 2
"""

import sys
import logging
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

from google_analysis10 import process_bonds_with_weightings
from bond_description_parser import SmartBondParser

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def test_method_1_real_isin():
    """Test Method 1: Real ISIN (should work again after fix)"""
    print("🧪 TESTING METHOD 1: Real ISIN US912810TJ79")
    
    db_path = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/bonds_data.db'
    validated_db_path = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/validated_quantlib_bonds.db'
    
    portfolio_data = {
        "data": [{
            "BOND_CD": "US912810TJ79",
            "CLOSING PRICE": 71.66,
            "WEIGHTING": 100.0,
            "Inventory Date": "2025/06/30"
        }]
    }
    
    try:
        results = process_bonds_with_weightings(portfolio_data, db_path, validated_db_path=validated_db_path)
        
        if len(results) > 0 and 'yield' in results.columns:
            bond_yield = results.iloc[0]['yield']
            bond_duration = results.iloc[0]['duration']
            
            print(f"✅ Method 1 SUCCESS:")
            print(f"   ISIN: US912810TJ79")
            print(f"   Yield: {bond_yield:.5f}%")
            print(f"   Duration: {bond_duration:.5f} years")
            
            if bond_yield > 0 and bond_duration > 0:
                print("🎉 METHOD 1 RESTORED!")
                return True
            else:
                print("❌ Method 1 still returning zero values")
                return False
        else:
            print("❌ Method 1 failed - no results returned")
            return False
            
    except Exception as e:
        print(f"❌ Method 1 failed with error: {e}")
        return False

def test_method_2_synthetic_isin():
    """Test Method 2: Synthetic ISIN (should continue working with Treasury fix)"""
    print("\n🧪 TESTING METHOD 2: Synthetic Treasury Bond")
    
    db_path = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/bonds_data.db'
    validated_db_path = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/validated_quantlib_bonds.db'
    
    parser = SmartBondParser(db_path, validated_db_path)
    
    # Test Treasury bond parsing
    treasury_description = "T 3 15/08/2052"
    
    try:
        parsed_bond = parser.parse_bond_description(treasury_description)
        
        if parsed_bond:
            conventions = parser.predict_most_likely_conventions(parsed_bond)
            
            calculation_result = parser.calculate_accrued_interest(
                parsed_bond,
                conventions,
                settlement_date="2025-06-30",
                price=71.66
            )
            
            if calculation_result.get('calculation_successful'):
                bond_yield = calculation_result.get('yield_to_maturity', 0)
                bond_duration = calculation_result.get('duration', 0)
                
                print(f"✅ Method 2 SUCCESS:")
                print(f"   Description: {treasury_description}")
                print(f"   Synthetic ISIN: {parsed_bond.get('isin', 'N/A')}")
                print(f"   Yield: {bond_yield:.5f}%")
                print(f"   Duration: {bond_duration:.5f} years")
                
                if bond_yield > 0 and bond_duration > 0:
                    print("🎉 METHOD 2 TREASURY FIX PRESERVED!")
                    return True
                else:
                    print("❌ Method 2 returning zero values")
                    return False
            else:
                print("❌ Method 2 calculation failed")
                return False
        else:
            print("❌ Method 2 parsing failed")
            return False
            
    except Exception as e:
        print(f"❌ Method 2 failed with error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 TESTING REGRESSION FIX")
    print("=" * 50)
    
    method1_success = test_method_1_real_isin()
    method2_success = test_method_2_synthetic_isin()
    
    print("\n" + "=" * 50)
    print("📊 REGRESSION FIX RESULTS:")
    print(f"   Method 1 (Real ISIN): {'✅ RESTORED' if method1_success else '❌ STILL BROKEN'}")
    print(f"   Method 2 (Synthetic): {'✅ PRESERVED' if method2_success else '❌ BROKEN'}")
    
    if method1_success and method2_success:
        print("\n🏆 REGRESSION FIX: COMPLETE SUCCESS!")
        print("Both methods now working correctly!")
    else:
        print("\n🚨 REGRESSION FIX: PARTIAL OR FAILED")
        print("Further debugging needed.")
