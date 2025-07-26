#!/usr/bin/env python3
"""
🚨 CRITICAL TEST: Verify Treasury Detection Fix
==============================================

Tests that US912810TJ79 is now correctly detected as Treasury bond
using the fixed Treasury detection logic.
"""

import os
import sys

# Add project path
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

from treasury_bond_fix import TreasuryBondDetector

def test_treasury_detection_fix():
    """Test that the fixed Treasury detector works for US912810TJ79"""
    print("🧪 TESTING FIXED TREASURY DETECTION")
    print("=" * 50)
    
    # Initialize the WORKING Treasury detector
    db_path = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/bonds_data.db'
    validated_db_path = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/validated_quantlib_bonds.db'
    
    detector = TreasuryBondDetector(db_path, validated_db_path)
    
    # Test the problematic Treasury ISIN
    test_isin = "US912810TJ79"
    test_description = "US TREASURY N/B, 3%, 15-Aug-2052"
    
    print(f"🎯 Testing ISIN: {test_isin}")
    print(f"📝 Description: {test_description}")
    print()
    
    # Test Treasury detection
    is_treasury, detection_method = detector.is_treasury_bond(test_isin, test_description)
    
    if is_treasury:
        print(f"✅ SUCCESS: Treasury detected via {detection_method}")
        print(f"🏛️ ISIN {test_isin} correctly identified as Treasury bond!")
        
        # Test compounding frequency
        from treasury_bond_fix import get_correct_quantlib_compounding
        import QuantLib as ql
        
        compounding = get_correct_quantlib_compounding(test_isin, test_description, 
                                                     primary_db_path=db_path, 
                                                     secondary_db_path=validated_db_path)
        print(f"⚙️ Compounding: {compounding}")
        
        if compounding == ql.Semiannual:
            print("✅ CORRECT: Treasury using SEMIANNUAL compounding (ql.Semiannual = 2)")
            print()
            print("🎉 TREASURY DETECTION FIX SUCCESSFUL!")
            print("   ✅ ISIN pattern US912810* detected")
            print("   ✅ Semiannual compounding applied")
            print("   ✅ Database creep fixed!")
            return True
        else:
            print(f"❌ WRONG COMPOUNDING: Expected {ql.Semiannual}, got {compounding}")
            
    else:
        print(f"❌ FAILED: Treasury NOT detected")
        print(f"💔 ISIN {test_isin} still not recognized as Treasury")
        
    return False

if __name__ == "__main__":
    try:
        success = test_treasury_detection_fix()
        if success:
            print("\n" + "="*60)
            print("🚀 DATABASE CREEP FIXED!")
            print("   The Treasury ISIN US912810TJ79 is now correctly detected")
            print("   Layer 3 ISIN Stub Detection is working!")
            print("="*60)
        else:
            print("\n❌ Fix verification failed - more work needed")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
