#!/usr/bin/env python3
"""
Final verification test for PANAMA bond fix
Tests the real portfolio calculation system with our SmartBondParser integration
"""
import sys
from pathlib import Path

# Add the google_analysis10 directory to the Python path
sys.path.append(str(Path(__file__).parent))

import logging
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def test_panama_in_real_system():
    """Test PANAMA bond using the real portfolio calculation system"""
    print("\n🧪 TESTING PANAMA BOND IN REAL CALCULATION SYSTEM")
    print("=" * 60)
    
    try:
        # Use the proven portfolio calculator
        from proven_portfolio_calculator import ProvenPortfolioCalculator
        
        # Create calculator instance
        calculator = ProvenPortfolioCalculator()
        
        # Test data for PANAMA bond (from the documents)
        panama_test_data = {
            'ISIN': 'US698299BL70',
            'PX_MID': 56.60,
            'Name': 'PANAMA, 3.87%, 23-Jul-2060',
            'Weight': 4.0  # Example weight
        }
        
        print(f"🏛️ Testing PANAMA bond:")
        print(f"   ISIN: {panama_test_data['ISIN']}")
        print(f"   Price: {panama_test_data['PX_MID']}")
        print(f"   Description: {panama_test_data['Name']}")
        
        # Calculate bond metrics
        result = calculator.calculate_bond_metrics(
            panama_test_data['ISIN'],
            panama_test_data['PX_MID'],
            panama_test_data
        )
        
        if result['success']:
            yield_val = result['yield']
            duration = result['duration']
            
            print(f"\n🎯 CALCULATION RESULT:")
            print(f"   Yield: {yield_val:.5f} ({yield_val*100:.3f}%)")
            print(f"   Duration: {duration:.3f} years")
            
            # Check if we got reasonable data (should be around 7.32679% from corrected table)
            expected_yield_range = (0.070, 0.080)  # 7.0% - 8.0% reasonable range
            
            if expected_yield_range[0] <= yield_val <= expected_yield_range[1]:
                print("\n✅ SUCCESS: PANAMA bond yield is in expected range!")
                print(f"   Expected: {expected_yield_range[0]*100:.1f}% - {expected_yield_range[1]*100:.1f}%")
                print(f"   Actual: {yield_val*100:.3f}%")
                
                # Check if we got parsed data (3.87% coupon)
                if 'coupon' in result and abs(result['coupon'] - 0.0387) < 0.001:
                    print("✅ BONUS: Detected correct coupon from SmartBondParser (3.87%)")
                
                return True
            else:
                print(f"\n⚠️ WARNING: Yield outside expected range")
                print(f"   Expected: {expected_yield_range[0]*100:.1f}% - {expected_yield_range[1]*100:.1f}%")
                print(f"   Actual: {yield_val*100:.3f}%")
                return False
        else:
            print(f"\n❌ CALCULATION FAILED:")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_panama_with_fallback():
    """Test PANAMA bond specifically with the enhanced fallback system"""
    print("\n🧪 TESTING PANAMA BOND WITH ENHANCED FALLBACK")
    print("=" * 60)
    
    try:
        # Test with the enhanced fallback directly
        from core.enhanced_portfolio_fallback import EnhancedPortfolioFallback
        from bond_description_parser import SmartBondParser
        from dual_database_manager import DualDatabaseManager
        
        # Setup components
        db_manager = DualDatabaseManager('bonds_data.db', 'validated_quantlib_bonds.db')
        bond_parser = SmartBondParser('bonds_data.db', 'validated_quantlib_bonds.db')
        
        # Create fallback processor
        fallback = EnhancedPortfolioFallback(bond_parser, db_manager)
        
        # Test data for PANAMA bond
        panama_data = {
            'Name': 'PANAMA, 3.87%, 23-Jul-2060'
        }
        isin = 'US698299BL70'
        price = 56.60
        
        print(f"🏛️ Testing with Enhanced Fallback:")
        print(f"   ISIN: {isin}")
        print(f"   Price: {price}")
        print(f"   Row data: {panama_data}")
        
        # Test the enhanced resolution
        success, bond_data = fallback.enhanced_resolve_bond_data(isin, panama_data, price)
        
        if success:
            coupon, maturity, name = bond_data[0], bond_data[1], bond_data[2]
            
            print(f"\n🎯 FALLBACK RESULT:")
            print(f"   Success: {success}")
            print(f"   Coupon: {coupon:.5f} ({coupon*100:.3f}%)")
            print(f"   Maturity: {maturity}")
            print(f"   Name: {name}")
            
            # Check if we got the correct parsed data
            expected_coupon = 0.0387  # 3.87%
            expected_maturity = '2060-07-23'
            
            coupon_correct = abs(coupon - expected_coupon) < 0.001
            maturity_correct = maturity == expected_maturity
            
            if coupon_correct and maturity_correct:
                print("\n✅ PERFECT: Got exact SmartBondParser data!")
                print(f"   ✅ Coupon: {coupon*100:.2f}% (expected 3.87%)")
                print(f"   ✅ Maturity: {maturity} (expected 2060-07-23)")
                return True
            else:
                print(f"\n⚠️ PARTIAL: Some data doesn't match expected")
                print(f"   Coupon: {coupon*100:.2f}% ({'✅' if coupon_correct else '❌'} expected 3.87%)")
                print(f"   Maturity: {maturity} ({'✅' if maturity_correct else '❌'} expected 2060-07-23)")
                return False
        else:
            print(f"\n❌ FALLBACK FAILED:")
            print(f"   Success: {success}")
            print(f"   Data: {bond_data}")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 FINAL VERIFICATION: PANAMA BOND FIX")
    print("=" * 70)
    
    # Test 1: Enhanced fallback system
    fallback_success = test_panama_with_fallback()
    
    # Test 2: Real portfolio calculation system
    portfolio_success = test_panama_in_real_system()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 FINAL TEST SUMMARY:")
    print(f"   Enhanced Fallback Test: {'✅ PASS' if fallback_success else '❌ FAIL'}")
    print(f"   Portfolio Calculation Test: {'✅ PASS' if portfolio_success else '❌ FAIL'}")
    
    if fallback_success and portfolio_success:
        print("\n🎉 COMPLETE SUCCESS!")
        print("   ✅ SmartBondParser integration working perfectly")
        print("   ✅ PANAMA bond gets correct data (3.87%, 2060-07-23)")
        print("   ✅ Fix is ready for production!")
    elif fallback_success:
        print("\n🎯 PARTIAL SUCCESS!")
        print("   ✅ SmartBondParser integration working")
        print("   ⚠️ Portfolio system needs additional verification")
    else:
        print("\n⚠️ FIX NEEDS MORE WORK")
        print("   ❌ Some components still failing")
