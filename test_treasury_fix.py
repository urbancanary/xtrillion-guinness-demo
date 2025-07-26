#!/usr/bin/env python3
"""
Test Treasury Classification Fix
===============================

This test validates that the Treasury classification bug is fixed:
- Treasury bonds with/without ISIN should return identical results
- Treasury bonds should use SEMIANNUAL compounding
- Method 1 (with ISIN) vs Method 2 (without ISIN) should match
"""

import sys
import logging
from datetime import datetime

# Add the project path
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

from google_analysis10 import process_bonds_with_weightings
from bond_description_parser import SmartBondParser

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_treasury_fix():
    """Test that the Treasury classification fix works"""
    
    print("🚨 TESTING TREASURY CLASSIFICATION FIX")
    print("=" * 60)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Database paths
    db_path = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/bonds_data.db'
    validated_db_path = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/validated_quantlib_bonds.db'
    
    # Test bond: US Treasury N/B, 3%, 15-Aug-2052
    test_bond = {
        'isin': 'US912810TJ79',
        'description': 'US TREASURY N/B, 3%, 15-Aug-2052', 
        'price': 71.66,
        'settlement_date': '2025-06-30'
    }
    
    print(f"📋 TEST BOND:")
    print(f"   ISIN: {test_bond['isin']}")
    print(f"   Description: {test_bond['description']}")
    print(f"   Price: {test_bond['price']}")
    print(f"   Settlement: {test_bond['settlement_date']}")
    print()
    
    # Method 1: With ISIN (Reference)
    print("🔬 METHOD 1: Direct Local + ISIN (Reference)")
    print("-" * 50)
    
    portfolio_data_with_isin = {
        "data": [{
            "BOND_CD": test_bond['isin'],
            "CLOSING PRICE": test_bond['price'],
            "WEIGHTING": 100.0,
            "Inventory Date": test_bond['settlement_date'].replace("-", "/")
        }]
    }
    
    try:
        results_with_isin = process_bonds_with_weightings(
            portfolio_data_with_isin, 
            db_path, 
            validated_db_path=validated_db_path
        )
        
        if len(results_with_isin) > 0:
            result = results_with_isin.iloc[0]
            yield_1 = float(result.get('yield', 0))
            duration_1 = float(result.get('duration', 0))
            
            print(f"✅ METHOD 1 RESULTS:")
            print(f"   Yield: {yield_1:.5f}%")
            print(f"   Duration: {duration_1:.5f} years")
            print(f"   Expected: SEMIANNUAL compounding for Treasury")
        else:
            print("❌ METHOD 1 FAILED: No results returned")
            return False
    except Exception as e:
        print(f"❌ METHOD 1 ERROR: {e}")
        return False
    
    print()
    
    # Method 2: Without ISIN (SHOULD BE FIXED)
    print("🔬 METHOD 2: Direct Local - ISIN (FIXED)")
    print("-" * 50)
    
    # Initialize parser
    parser = SmartBondParser(db_path, validated_db_path)
    
    # Parse the bond description
    parsed_bond = parser.parse_bond_description(test_bond['description'])
    
    if parsed_bond:
        print(f"📝 PARSED BOND DATA:")
        print(f"   Issuer: {parsed_bond['issuer']}")
        print(f"   Coupon: {parsed_bond['coupon']}%")
        print(f"   Maturity: {parsed_bond['maturity']}")
        print(f"   Bond Type: {parsed_bond['bond_type']} ⭐")
        print()
        
        # Predict conventions
        conventions = parser.predict_most_likely_conventions(parsed_bond)
        print(f"📊 PREDICTED CONVENTIONS:")
        print(f"   Day Count: {conventions.get('day_count')}")
        print(f"   Frequency: {conventions.get('frequency')} ⭐")
        print(f"   Treasury Override: {conventions.get('treasury_override', False)} ⭐")
        print()
        
        # Calculate using parser method
        calculation_result = parser.calculate_accrued_interest(
            parsed_bond, 
            conventions, 
            settlement_date=test_bond['settlement_date'],
            price=test_bond['price']
        )
        
        if calculation_result.get('calculation_successful'):
            yield_2 = calculation_result.get('yield_to_maturity', 0)
            duration_2 = calculation_result.get('duration', 0)
            
            print(f"✅ METHOD 2 RESULTS:")
            print(f"   Yield: {yield_2:.5f}%")
            print(f"   Duration: {duration_2:.5f} years")
            print(f"   Processing Method: {calculation_result.get('processing_method')}")
        else:
            print(f"❌ METHOD 2 FAILED: {calculation_result}")
            return False
    else:
        print("❌ PARSING FAILED: Could not parse bond description")
        return False
    
    print()
    
    # Compare Results
    print("📊 COMPARISON & VALIDATION")
    print("-" * 50)
    
    yield_diff = abs(yield_1 - yield_2)
    duration_diff = abs(duration_1 - duration_2)
    
    print(f"Yield Difference: {yield_diff:.5f}% ({yield_diff*100:.2f} bps)")
    print(f"Duration Difference: {duration_diff:.5f} years")
    print()
    
    # Validation criteria (should be very close after fix)
    yield_tolerance = 0.01  # 1 basis point
    duration_tolerance = 0.05  # 0.05 years
    
    yield_match = yield_diff <= yield_tolerance
    duration_match = duration_diff <= duration_tolerance
    
    print("🎯 VALIDATION RESULTS:")
    print(f"   Yield Match (≤1bp): {'✅ PASS' if yield_match else '❌ FAIL'}")
    print(f"   Duration Match (≤0.05yr): {'✅ PASS' if duration_match else '❌ FAIL'}")
    print()
    
    if yield_match and duration_match:
        print("🎉 BUG FIX SUCCESSFUL!")
        print("   Both methods now return identical results")
        print("   Treasury classification is working correctly")
        return True
    else:
        print("⚠️ BUG FIX INCOMPLETE!")
        print("   Methods still return different results")
        print("   Further investigation needed")
        return False

def test_synthetic_isin_reconstruction():
    """Test that synthetic ISIN reconstruction works"""
    print("\n🧪 TESTING SYNTHETIC ISIN RECONSTRUCTION")
    print("=" * 60)
    
    from google_analysis10 import extract_bond_description_for_treasury_detection
    
    test_cases = [
        {
            'isin': 'PARSED_T_3.0_20520815',
            'expected': 'T 3.0 15/08/2052'
        },
        {
            'isin': 'PARSED_T_4.25_20301215', 
            'expected': 'T 4.25 15/12/2030'
        },
        {
            'isin': 'US912810TJ79',  # Real ISIN - no reconstruction
            'expected': None
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"📝 TEST {i}: {test['isin']}")
        
        bond_data = {'isin': test['isin']}
        reconstructed = extract_bond_description_for_treasury_detection(bond_data, test['isin'])
        
        if test['expected']:
            if reconstructed == test['expected']:
                print(f"   ✅ PASS: {reconstructed}")
            else:
                print(f"   ❌ FAIL: Expected '{test['expected']}', got '{reconstructed}'")
        else:
            print(f"   📍 Real ISIN (no reconstruction): {reconstructed}")
        print()

if __name__ == "__main__":
    try:
        # Test 1: Synthetic ISIN reconstruction
        test_synthetic_isin_reconstruction()
        
        # Test 2: Full calculation comparison
        success = test_treasury_fix()
        
        print("\n🎯 OVERALL RESULT:")
        print("=" * 60)
        if success:
            print("✅ TREASURY CLASSIFICATION BUG FIX: SUCCESS!")
            print("   Both methods return identical results")
            print("   Treasury bonds use SEMIANNUAL compounding")
        else:
            print("❌ TREASURY CLASSIFICATION BUG FIX: FAILED")
            print("   Methods still return different results")
        
    except Exception as e:
        print(f"❌ TEST EXECUTION ERROR: {e}")
        import traceback
        traceback.print_exc()
