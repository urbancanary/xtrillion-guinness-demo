#!/usr/bin/env python3
"""
Test the spread calculation fix by calling the actual function
"""

import sys
import os

# Add the project directory to path
project_dir = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10'
sys.path.insert(0, project_dir)

def test_actual_calculation():
    """Test the actual calculation function to verify spread fix works"""
    
    print("🧪 TESTING ACTUAL SPREAD CALCULATION")
    print("=" * 50)
    
    try:
        # Import the actual functions
        from google_analysis10 import process_bond_portfolio
        from datetime import datetime
        
        # Test with a corporate bond that should have a spread
        test_portfolio = {
            "data": [
                {
                    "description": "ECOPETROL SA, 5.875%, 28-May-2045",
                    "price": 69.31,
                    "weighting": 100.0
                }
            ]
        }
        
        print("📊 Testing ECOPETROL bond calculation...")
        print(f"   Description: {test_portfolio['data'][0]['description']}")
        print(f"   Price: {test_portfolio['data'][0]['price']}")
        
        # Call the portfolio processing function
        result = process_bond_portfolio(
            portfolio_data=test_portfolio,
            db_path='./bonds_data.db',
            validated_db_path='./validated_quantlib_bonds.db',
            bloomberg_db_path='./bloomberg_index.db',
            settlement_days=0,
            settlement_date='2025-07-30'
        )
        
        if result and len(result) > 0:
            bond_result = result[0]
            
            print(f"\n✅ Calculation completed!")
            print(f"   Status: {bond_result.get('successful', 'Unknown')}")
            
            if bond_result.get('successful'):
                ytm = bond_result.get('ytm')
                g_spread = bond_result.get('g_spread')
                z_spread = bond_result.get('z_spread')
                
                print(f"   YTM: {ytm:.4f}%" if ytm else "   YTM: N/A")
                print(f"   G-Spread: {g_spread:.0f} bps" if g_spread and g_spread != 0 else f"   G-Spread: {g_spread} (not calculated)")
                print(f"   Z-Spread: {z_spread:.0f} bps" if z_spread and z_spread != 0 else f"   Z-Spread: {z_spread} (not calculated)")
                
                if g_spread and g_spread > 200:
                    print("\n🎉 SUCCESS: Spread calculation appears to be working!")
                    print(f"   Corporate bond shows {g_spread:.0f} bps spread over treasuries ✅")
                    return True
                else:
                    print(f"\n❌ ISSUE: Expected corporate spread >200 bps, got {g_spread}")
                    return False
            else:
                error = bond_result.get('error', 'Unknown error')
                print(f"   Error: {error}")
                return False
        else:
            print("❌ No results returned from calculation")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_treasury_bond():
    """Test with a treasury bond to verify 0 spread"""
    
    print("\n🏛️ TESTING TREASURY BOND (should have 0 spread)")
    print("=" * 50)
    
    try:
        from google_analysis10 import process_bond_portfolio
        
        # Test with a Treasury bond that should have 0 spread
        test_portfolio = {
            "data": [
                {
                    "description": "T 3 15/08/52",
                    "price": 71.66,
                    "weighting": 100.0
                }
            ]
        }
        
        print("📊 Testing Treasury bond calculation...")
        print(f"   Description: {test_portfolio['data'][0]['description']}")
        
        result = process_bond_portfolio(
            portfolio_data=test_portfolio,
            db_path='./bonds_data.db',
            validated_db_path='./validated_quantlib_bonds.db',
            bloomberg_db_path='./bloomberg_index.db',
            settlement_days=0,
            settlement_date='2025-07-30'
        )
        
        if result and len(result) > 0:
            bond_result = result[0]
            
            if bond_result.get('successful'):
                g_spread = bond_result.get('g_spread')
                print(f"   Treasury G-Spread: {g_spread} bps (should be 0 or null)")
                
                if g_spread == 0 or g_spread is None:
                    print("✅ Treasury spread correctly set to 0/null")
                    return True
                else:
                    print(f"❌ Treasury should have 0 spread, got {g_spread}")
                    return False
            else:
                print(f"   Treasury calculation failed: {bond_result.get('error')}")
                return False
        else:
            print("❌ No Treasury results returned")
            return False
            
    except Exception as e:
        print(f"❌ Treasury test failed: {e}")
        return False

if __name__ == "__main__":
    print("🎯 TESTING SPREAD CALCULATION FIX WITH ACTUAL FUNCTIONS")
    print("=" * 60)
    
    corporate_success = test_actual_calculation()
    treasury_success = test_treasury_bond()
    
    print("\n📊 FINAL RESULTS:")
    print("=" * 40)
    print(f"Corporate Bond Spread: {'✅ WORKING' if corporate_success else '❌ NOT WORKING'}")
    print(f"Treasury Bond Spread: {'✅ WORKING' if treasury_success else '❌ NOT WORKING'}")
    
    if corporate_success and treasury_success:
        print("\n🎉 ALL TESTS PASSED! Spread calculation fix is working correctly!")
        print("🚀 Ready for production deployment!")
    else:
        print("\n❌ Some tests failed. Fix needs more work before deployment.")
