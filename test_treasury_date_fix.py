#!/usr/bin/env python3
"""
Test Treasury Date Format Fix
===========================

Test the enhanced Treasury date format detection.
"""

import sys
import logging
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

# Enable detailed logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_treasury_date_fix():
    """Test the Treasury date format fix"""
    
    try:
        from core.universal_bond_parser import UniversalBondParser
        
        print("🏛️ Testing Treasury Date Format Fix...")
        
        parser = UniversalBondParser(
            './bonds_data.db',
            './validated_quantlib_bonds.db',
            './bloomberg_index.db'
        )
        
        # Test the problematic Treasury bond
        treasury_description = "T 3 15/08/52"
        treasury_isin = "US912810TJ79"
        
        print(f"\n📊 Testing Treasury Description: {treasury_description}")
        
        # Test description parsing with the fix
        desc_result = parser.parse_bond(treasury_description)
        
        print(f"\n📋 Description Parsing Results:")
        print(f"   Parsing Success: {getattr(desc_result, 'parsing_success', False)}")
        print(f"   Parser Used: {getattr(desc_result, 'parser_used', 'N/A')}")
        print(f"   Treasury Override Applied: {getattr(desc_result, 'treasury_override_applied', False)}")
        print(f"   Error: {getattr(desc_result, 'error_message', 'None')}")
        print(f"   Coupon: {desc_result.coupon_rate}")
        print(f"   Maturity: {desc_result.maturity_date}")
        print(f"   Day Count: {desc_result.day_count}")
        print(f"   Frequency: {desc_result.frequency}")
        print(f"   Business Convention: {desc_result.business_convention}")
        
        if getattr(desc_result, 'parsing_success', False):
            print(f"\n✅ SUCCESS: Treasury description parsing now works!")
            if desc_result.maturity_date == "2052-08-15":
                print(f"✅ DATE CORRECT: 15/08/52 → 2052-08-15 (15-Aug-2052)")
            else:
                print(f"⚠️ DATE ISSUE: Expected 2052-08-15, got {desc_result.maturity_date}")
        else:
            print(f"\n❌ FAILED: Treasury description parsing still failing")
            print(f"   Error: {getattr(desc_result, 'error_message', 'Unknown')}")
        
        # Test ISIN parsing too
        print(f"\n📊 Testing Treasury ISIN: {treasury_isin}")
        isin_result = parser.parse_bond(treasury_isin)
        
        print(f"\n📋 ISIN Parsing Results:")
        print(f"   Parsing Success: {getattr(isin_result, 'parsing_success', False)}")
        print(f"   Parser Used: {getattr(isin_result, 'parser_used', 'N/A')}")
        print(f"   Treasury Override Applied: {getattr(isin_result, 'treasury_override_applied', False)}")
        print(f"   Error: {getattr(isin_result, 'error_message', 'None')}")
        
        # Compare if both succeed
        if (getattr(desc_result, 'parsing_success', False) and 
            getattr(isin_result, 'parsing_success', False)):
            
            print(f"\n🔍 CONVENTION COMPARISON:")
            conventions_match = (
                desc_result.day_count == isin_result.day_count and
                desc_result.frequency == isin_result.frequency and
                desc_result.business_convention == isin_result.business_convention
            )
            
            if conventions_match:
                print(f"   ✅ PERFECT MATCH!")
                print(f"   Day Count: {desc_result.day_count}")
                print(f"   Frequency: {desc_result.frequency}")
                print(f"   Business Convention: {desc_result.business_convention}")
                print(f"\n🎯 SUCCESS: Treasury override eliminated convention differences!")
            else:
                print(f"   ❌ CONVENTIONS STILL MISMATCH")
                print(f"   ISIN: {isin_result.day_count}, {isin_result.frequency}, {isin_result.business_convention}")
                print(f"   DESC: {desc_result.day_count}, {desc_result.frequency}, {desc_result.business_convention}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_treasury_date_fix()
