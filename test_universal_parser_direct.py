#!/usr/bin/env python3
"""
Direct Universal Parser Test
==========================

Test the Universal Parser ISIN lookup directly with detailed logging.
"""

import sys
import logging
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def test_universal_parser_direct():
    """Test Universal Parser directly with debug info"""
    
    try:
        from core.universal_bond_parser import UniversalBondParser
        
        print("🔍 Testing Universal Parser ISIN lookup...")
        
        parser = UniversalBondParser(
            './bonds_data.db',
            './validated_quantlib_bonds.db',
            './bloomberg_index.db'
        )
        
        test_isin = "US91282CJZ59"
        print(f"\n📊 Testing ISIN: {test_isin}")
        
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
        print(f"   Currency: {result.currency}")
        print(f"   Country: {result.country}")
        
        # Test database lookup directly
        print(f"\n🔍 Testing direct database lookup...")
        bond_data = parser._lookup_isin_in_database(test_isin, './bonds_data.db')
        
        if bond_data:
            print(f"✅ Found in bonds_data.db:")
            for key, value in bond_data.items():
                if value is not None:
                    print(f"   {key}: {value}")
        else:
            print(f"❌ Not found in bonds_data.db")
        
        # Test validated database
        bond_data = parser._lookup_isin_in_database(test_isin, './validated_quantlib_bonds.db')
        
        if bond_data:
            print(f"✅ Found in validated_quantlib_bonds.db:")
            for key, value in bond_data.items():
                if value is not None:
                    print(f"   {key}: {value}")
        else:
            print(f"❌ Not found in validated_quantlib_bonds.db")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_universal_parser_direct()
