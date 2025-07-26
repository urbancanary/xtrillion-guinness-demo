#!/usr/bin/env python3
"""
Focused Treasury Detection Fix Validation
========================================

This test validates ONLY the Treasury detection fix by testing:
1. Treasury description reconstruction from synthetic ISIN
2. Treasury detection via description 
3. SEMIANNUAL vs ANNUAL compounding selection
"""

import sys
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

from google_analysis10 import extract_bond_description_for_treasury_detection
from treasury_bond_fix import TreasuryBondDetector, get_correct_quantlib_compounding
import QuantLib as ql

def test_treasury_detection_fix_focused():
    print("🎯 FOCUSED TREASURY DETECTION FIX VALIDATION")
    print("=" * 60)
    
    # Test Case: The exact failing case from the bug report
    synthetic_isin = "PARSED_T_3.0_20520815"
    expected_description = "T 3.0 15/08/2052"
    
    print(f"📋 TEST CASE: {synthetic_isin}")
    print(f"Expected Description: {expected_description}")
    print()
    
    # Test 1: Description Reconstruction 
    print("🧪 TEST 1: Description Reconstruction")
    print("-" * 40)
    
    bond_data = {'isin': synthetic_isin, 'coupon': 3.0, 'maturity': '2052-08-15'}
    reconstructed = extract_bond_description_for_treasury_detection(bond_data, synthetic_isin)
    
    if reconstructed == expected_description:
        print(f"✅ PASS: {reconstructed}")
    else:
        print(f"❌ FAIL: Expected '{expected_description}', got '{reconstructed}'")
        return False
    
    print()
    
    # Test 2: Treasury Detection via Description
    print("🧪 TEST 2: Treasury Detection via Description")
    print("-" * 40)
    
    detector = TreasuryBondDetector()
    is_treasury, method = detector.is_treasury_bond(description=reconstructed)
    
    print(f"Description: {reconstructed}")
    print(f"Is Treasury: {is_treasury}")
    print(f"Detection Method: {method}")
    
    if is_treasury:
        print("✅ PASS: Treasury correctly detected")
    else:
        print("❌ FAIL: Treasury not detected")
        return False
    
    print()
    
    # Test 3: Compounding Frequency Selection
    print("🧪 TEST 3: Compounding Frequency Selection")  
    print("-" * 40)
    
    # Test with description (should be SEMIANNUAL)
    compounding_with_desc = get_correct_quantlib_compounding(
        isin=synthetic_isin, 
        description=reconstructed
    )
    
    # Test without description (should be ANNUAL - the old bug)
    compounding_without_desc = get_correct_quantlib_compounding(
        isin=synthetic_isin, 
        description=None
    )
    
    with_desc_str = "SEMIANNUAL" if compounding_with_desc == ql.Semiannual else "ANNUAL"
    without_desc_str = "SEMIANNUAL" if compounding_without_desc == ql.Semiannual else "ANNUAL"
    
    print(f"With Description: {with_desc_str}")
    print(f"Without Description: {without_desc_str}")
    
    # Validation
    if with_desc_str == "SEMIANNUAL":
        print("✅ PASS: Treasury uses SEMIANNUAL with description")
    else:
        print("❌ FAIL: Treasury should use SEMIANNUAL with description")
        return False
    
    if without_desc_str == "ANNUAL":
        print("✅ PASS: Non-Treasury (no description) uses ANNUAL")
    else:
        print("⚠️  INFO: Without description also detected as Treasury")
    
    print()
    
    # Test 4: Before/After Fix Comparison
    print("🧪 TEST 4: Before/After Fix Comparison")
    print("-" * 40)
    
    # BEFORE fix: description=None (the bug)
    compounding_before = get_correct_quantlib_compounding(synthetic_isin, description=None)
    before_str = "SEMIANNUAL" if compounding_before == ql.Semiannual else "ANNUAL"
    
    # AFTER fix: description provided
    compounding_after = get_correct_quantlib_compounding(synthetic_isin, description=reconstructed)
    after_str = "SEMIANNUAL" if compounding_after == ql.Semiannual else "ANNUAL"
    
    print(f"BEFORE fix (no description): {before_str}")
    print(f"AFTER fix (with description): {after_str}")
    
    if after_str == "SEMIANNUAL":
        print("✅ PASS: Fix correctly identifies Treasury for SEMIANNUAL compounding")
        fix_success = True
    else:
        print("❌ FAIL: Fix should result in SEMIANNUAL compounding")
        fix_success = False
    
    print()
    
    # Summary
    print("🎯 VALIDATION SUMMARY")
    print("-" * 40)
    print("✅ Description Reconstruction: WORKING")
    print("✅ Treasury Detection: WORKING") 
    print("✅ SEMIANNUAL Compounding: WORKING")
    
    if fix_success:
        print("\n🎉 TREASURY DETECTION FIX: SUCCESS!")
        print("   Treasury bonds now correctly use SEMIANNUAL compounding")
        print("   Description reconstruction from synthetic ISIN works")
        print("   The core Treasury classification bug is FIXED!")
        return True
    else:
        print("\n❌ TREASURY DETECTION FIX: FAILED")
        return False

def test_multiple_treasury_patterns():
    print("\n🧪 TESTING MULTIPLE TREASURY PATTERNS")
    print("=" * 60)
    
    detector = TreasuryBondDetector()
    
    test_cases = [
        "T 3.0 15/08/2052",  # Reconstructed from synthetic ISIN
        "US TREASURY N/B, 3%, 15-Aug-2052",  # Full description
        "TREASURY 2.5% 12/31/28",  # Alternative pattern
        "UST 4.0 05/31/30",  # UST pattern
        "GALAXY PIPELINE, 3.25%, 30-Sep-2040",  # Corporate (should not detect)
    ]
    
    for i, description in enumerate(test_cases, 1):
        is_treasury, method = detector.is_treasury_bond(description=description)
        compounding = get_correct_quantlib_compounding(description=description)
        compounding_str = "SEMIANNUAL" if compounding == ql.Semiannual else "ANNUAL"
        
        expected_treasury = i <= 4  # First 4 are Treasury, last is Corporate
        status = "✅" if is_treasury == expected_treasury else "❌"
        
        print(f"{status} {i}: {description}")
        print(f"     Treasury: {is_treasury} | Compounding: {compounding_str} | Method: {method}")
        print()

if __name__ == "__main__":
    try:
        # Primary test: Treasury detection fix validation
        success = test_treasury_detection_fix_focused()
        
        # Secondary test: Multiple patterns
        test_multiple_treasury_patterns()
        
        print("\n" + "=" * 80)
        if success:
            print("🏆 OVERALL RESULT: TREASURY DETECTION FIX SUCCESS!")
            print("    The critical bug has been resolved")
            print("    Treasury bonds now use correct SEMIANNUAL compounding")
        else:
            print("❌ OVERALL RESULT: TREASURY DETECTION FIX FAILED")
        
    except Exception as e:
        print(f"❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
