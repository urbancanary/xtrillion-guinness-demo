#!/usr/bin/env python3
"""
Test Treasury Override Integration
================================

Test the integrated Treasury override system to verify it fixes convention mismatches.
"""

import sys
import logging
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

# Enable detailed logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_treasury_override_integration():
    """Test the integrated Treasury override system"""
    
    try:
        from core.universal_bond_parser import UniversalBondParser
        
        print("🏛️ Testing Treasury Override Integration...")
        
        parser = UniversalBondParser(
            './bonds_data.db',
            './validated_quantlib_bonds.db',
            './bloomberg_index.db'
        )
        
        # Test cases: ISIN vs Description for same Treasury bond
        test_cases = [
            {
                "name": "Treasury 4.3% 2030",
                "isin": "US00206RGQ92",
                "description": "T 4.3 02/15/30"
            }
        ]
        
        for test_case in test_cases:
            print(f"\n{'='*80}")
            print(f"🧪 Testing: {test_case['name']}")
            print(f"{'='*80}")
            
            # Test ISIN parsing
            print(f"\n📊 ISIN Test: {test_case['isin']}")
            isin_result = parser.parse_bond(test_case['isin'])
            
            print(f"   Parsing Success: {getattr(isin_result, 'parsing_success', False)}")
            print(f"   Parser Used: {getattr(isin_result, 'parser_used', 'N/A')}")
            print(f"   Treasury Override Applied: {getattr(isin_result, 'treasury_override_applied', False)}")
            print(f"   Day Count: {isin_result.day_count}")
            print(f"   Frequency: {isin_result.frequency}")
            print(f"   Business Convention: {isin_result.business_convention}")
            print(f"   Coupon: {isin_result.coupon_rate}")
            print(f"   Maturity: {isin_result.maturity_date}")
            
            # Test Description parsing
            print(f"\n📊 Description Test: {test_case['description']}")
            desc_result = parser.parse_bond(test_case['description'])
            
            print(f"   Parsing Success: {getattr(desc_result, 'parsing_success', False)}")
            print(f"   Parser Used: {getattr(desc_result, 'parser_used', 'N/A')}")
            print(f"   Treasury Override Applied: {getattr(desc_result, 'treasury_override_applied', False)}")
            print(f"   Day Count: {desc_result.day_count}")
            print(f"   Frequency: {desc_result.frequency}")
            print(f"   Business Convention: {desc_result.business_convention}")
            print(f"   Coupon: {desc_result.coupon_rate}")
            print(f"   Maturity: {desc_result.maturity_date}")
            
            # Compare conventions
            print(f"\n🔍 Convention Comparison:")
            conventions_match = (
                isin_result.day_count == desc_result.day_count and
                isin_result.frequency == desc_result.frequency and
                isin_result.business_convention == desc_result.business_convention
            )
            
            if conventions_match:
                print(f"   ✅ CONVENTIONS NOW MATCH!")
                print(f"   ✅ Day Count: {isin_result.day_count}")
                print(f"   ✅ Frequency: {isin_result.frequency}")
                print(f"   ✅ Business Convention: {isin_result.business_convention}")
                print(f"\n🎯 SUCCESS: Treasury override fixed the convention mismatch!")
                print(f"   ISIN and Description parsing now use identical conventions.")
                print(f"   This should eliminate fractional yield differences!")
            else:
                print(f"   ❌ CONVENTIONS STILL MISMATCH!")
                print(f"   ISIN: {isin_result.day_count}, {isin_result.frequency}, {isin_result.business_convention}")
                print(f"   DESC: {desc_result.day_count}, {desc_result.frequency}, {desc_result.business_convention}")
            
            # Check if both had Treasury override applied
            isin_override = getattr(isin_result, 'treasury_override_applied', False)
            desc_override = getattr(desc_result, 'treasury_override_applied', False)
            
            print(f"\n🏛️ Treasury Override Status:")
            print(f"   ISIN Override Applied: {isin_override}")
            print(f"   Description Override Applied: {desc_override}")
            
            if isin_override and desc_override:
                print(f"   ✅ Both paths correctly applied Treasury override!")
            elif not isin_override and not desc_override:
                print(f"   ⚠️  Neither path applied Treasury override - check detection logic")
            else:
                print(f"   ⚠️  Inconsistent override application - one path missed")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_treasury_override_integration()
