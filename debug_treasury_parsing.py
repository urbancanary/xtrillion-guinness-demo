#!/usr/bin/env python3
"""
Debug the Treasury parsing issue
"""

import sys
sys.path.append('.')

def test_treasury_parsing():
    """Test Treasury parsing with the exact input that's failing"""
    
    from bond_description_parser import SmartBondParser
    
    print("🧪 DEBUGGING TREASURY PARSING")
    print("=" * 40)
    
    # Test the exact same input
    description = "T 3 15/08/52"
    print(f"Testing description: {description}")
    
    try:
        parser = SmartBondParser('./bonds_data.db', './validated_quantlib_bonds.db')
        result = parser.parse_bond_description(description)
        
        print("✅ Parsing successful!")
        print(f"Result: {result}")
        
        if result:
            print()
            print("📋 Parsed Bond Details:")
            print(f"  Issuer: {result.get('issuer', 'N/A')}")
            print(f"  Coupon: {result.get('coupon', 'N/A')}")
            print(f"  Maturity: {result.get('maturity', 'N/A')}")
            print(f"  Bond Type: {result.get('bond_type', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Parsing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_treasury_parsing()
