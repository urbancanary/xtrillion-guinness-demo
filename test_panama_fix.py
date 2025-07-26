#!/usr/bin/env python3
"""
Test script to verify the PANAMA bond parsing fix
"""
import sys
import logging
from pathlib import Path

# Add the google_analysis10 directory to the Python path
sys.path.append(str(Path(__file__).parent))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger()

def test_smartbondparser_directly():
    """Test SmartBondParser directly on PANAMA bond"""
    print("\n🧪 TESTING SMARTBONDPARSER DIRECTLY:")
    
    try:
        from bond_description_parser import SmartBondParser
        
        # Use the correct database paths
        db_path = "bonds_data.db"
        validated_db_path = "validated_quantlib_bonds.db"
        
        parser = SmartBondParser(db_path, validated_db_path)
        
        description = "PANAMA, 3.87%, 23-Jul-2060"
        print(f"Description: {description}")
        
        result = parser.parse_bond_description(description)
        print(f"Parsed result: {result}")
        
        if result and 'coupon' in result and 'maturity' in result:
            coupon = result['coupon']
            maturity = result['maturity']  # Already a string in YYYY-MM-DD format
            print(f"✅ SUCCESS: Coupon {coupon}%, Maturity {maturity}")
            return True, coupon, maturity
        else:
            print("❌ FAIL: Incomplete parsing result")
            return False, None, None
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None

def test_corporate_fallback_method():
    """Test the _create_corporate_fallback_data method directly"""
    print("\n🧪 TESTING _create_corporate_fallback_data METHOD:")
    
    try:
        # Mock the necessary components
        class MockDualDB:
            pass
            
        class MockBondParser:
            pass
        
        from core.enhanced_portfolio_fallback import EnhancedPortfolioFallback
        
        # Create instance with mocks
        fallback = EnhancedPortfolioFallback(MockBondParser(), MockDualDB())
        
        # Test data
        isin = "US698299BL70"
        row = {'Name': 'PANAMA, 3.87%, 23-Jul-2060'}
        price = 56.60
        conventions = {}
        
        print(f"ISIN: {isin}")
        print(f"Row: {row}")
        
        # Test the method
        success, bond_data = fallback._create_corporate_fallback_data(isin, row, price, conventions)
        
        print(f"Success: {success}")
        if success:
            coupon, maturity, name = bond_data[0], bond_data[1], bond_data[2]
            print(f"Coupon: {coupon:.4f} ({coupon*100:.2f}%)")
            print(f"Maturity: {maturity}")
            print(f"Name: {name}")
            
            # Check if we got the RIGHT data
            expected_coupon = 0.0387  # 3.87%
            expected_maturity = '2060-07-23'
            
            if abs(coupon - expected_coupon) < 0.001 and maturity == expected_maturity:
                print('✅ SUCCESS: Got CORRECT parsed data (3.87%, 2060)')
                return True
            elif abs(coupon - 0.045) < 0.001 and maturity == '2028-12-31':
                print('❌ FAIL: Still getting wrong synthetic data (4.5%, 2028)')
                return False
            else:
                print(f'⚠️ UNEXPECTED: Got different data ({coupon*100:.2f}%, {maturity})')
                return False
        else:
            print("❌ FAIL: Method returned False")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 TESTING PANAMA BOND FIX")
    print("=" * 50)
    
    # Test 1: SmartBondParser directly
    parser_success, coupon, maturity = test_smartbondparser_directly()
    
    # Test 2: The corporate fallback method
    method_success = test_corporate_fallback_method()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    print(f"SmartBondParser Direct: {'✅ PASS' if parser_success else '❌ FAIL'}")
    print(f"Corporate Fallback Method: {'✅ PASS' if method_success else '❌ FAIL'}")
    
    if parser_success and method_success:
        print("\n🎉 ALL TESTS PASSED! Fix is working correctly!")
    else:
        print("\n⚠️ Some tests failed. Fix needs debugging.")
