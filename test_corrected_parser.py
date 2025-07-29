#!/usr/bin/env python3
"""
Test Corrected Universal Parser
============================

Test the fixed Universal Parser with a real Treasury ISIN from bloomberg_index.db
"""

import sys
import logging
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

# Enable detailed logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_corrected_parser():
    """Test the corrected Universal Parser"""
    
    try:
        from core.universal_bond_parser import UniversalBondParser
        
        print("🔍 Testing Corrected Universal Parser...")
        
        parser = UniversalBondParser(
            './bonds_data.db',
            './validated_quantlib_bonds.db',
            './bloomberg_index.db'
        )
        
        # Use a real Treasury ISIN from bloomberg_index.db
        test_isin = "US00206RGQ92"  # T 4.3 02/15/30
        print(f"\n📊 Testing Treasury ISIN: {test_isin}")
        
        # Test the parse_bond method
        result = parser.parse_bond(test_isin)
        
        print(f"\n📋 Results:")
        print(f"   Input Type: {result.input_type}")
        print(f"   Parsing Success: {getattr(result, 'parsing_success', 'N/A')}")
        print(f"   Parser Used: {getattr(result, 'parser_used', 'N/A')}")
        print(f"   Error: {getattr(result, 'error_message', 'N/A')}")
        print(f"   ISIN: {result.isin}")
        print(f"   Description: {result.description}")
        print(f"   Coupon: {result.coupon_rate}")
        print(f"   Maturity: {result.maturity_date}")
        print(f"   Day Count: {result.day_count}")
        print(f"   Frequency: {result.frequency}")
        print(f"   Business Convention: {result.business_convention}")
        print(f"   Currency: {result.currency}")
        print(f"   Country: {result.country}")
        
        # Test if this would work for calculations
        if result.parsing_success:
            print(f"\n✅ ISIN lookup successful!")
            print(f"✅ Has required data for bond calculations")
        else:
            print(f"\n❌ ISIN lookup failed: {getattr(result, 'error_message', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_corrected_parser()
