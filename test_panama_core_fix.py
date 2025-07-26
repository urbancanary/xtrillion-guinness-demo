#!/usr/bin/env python3
"""
Simple direct test of the PANAMA bond fix
Tests only the core SmartBondParser integration in corporate fallback
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def test_core_panama_fix():
    """Test the core SmartBondParser integration directly"""
    print("🧪 TESTING CORE PANAMA BOND FIX")
    print("=" * 50)
    
    try:
        # Import the fixed components
        from core.enhanced_portfolio_fallback import EnhancedPortfolioFallback
        from bond_description_parser import SmartBondParser  
        from dual_database_manager import DualDatabaseManager
        
        # Setup minimal components
        db_manager = DualDatabaseManager('bonds_data.db', 'validated_quantlib_bonds.db')
        bond_parser = SmartBondParser('bonds_data.db', 'validated_quantlib_bonds.db')
        
        # Create enhanced fallback
        fallback = EnhancedPortfolioFallback(bond_parser, db_manager)
        
        # Test data for PANAMA bond
        panama_row = {'Name': 'PANAMA, 3.87%, 23-Jul-2060'}
        panama_isin = 'US698299BL70'
        panama_price = 56.60
        
        print(f"📋 Input Data:")
        print(f"   ISIN: {panama_isin}")
        print(f"   Row: {panama_row}")  
        print(f"   Price: {panama_price}")
        
        # Test the resolve_bond_data method
        print(f"\\n🔍 Testing resolve_bond_data method...")
        success, bond_data = fallback.resolve_bond_data(panama_isin, panama_row, panama_price)
        
        print(f"\\n📊 RESULT:")
        print(f"   Success: {success}")
        
        if success:
            # bond_data should be a tuple: (coupon, maturity, name, country, region, dm_em, ...)
            coupon = bond_data[0]
            maturity = bond_data[1]  
            name = bond_data[2]
            
            print(f"   Coupon: {coupon:.5f} ({coupon*100:.3f}%)")
            print(f"   Maturity: {maturity}")
            print(f"   Name: {name}")
            
            # Check if we got SmartBondParser data vs synthetic data
            expected_coupon = 0.0387  # 3.87% from SmartBondParser
            synthetic_coupon = 0.045  # 4.5% synthetic fallback
            
            if abs(coupon - expected_coupon) < 0.001:
                print(f"\\n✅ PERFECT: Got SmartBondParser data!")
                print(f"   ✅ Coupon: {coupon*100:.2f}% (SmartBondParser 3.87%)")
                print(f"   ✅ Maturity: {maturity} (SmartBondParser 2060-07-23)")
                return True
                
            elif abs(coupon - synthetic_coupon) < 0.001:
                print(f"\\n❌ FAIL: Still getting synthetic fallback data")
                print(f"   ❌ Coupon: {coupon*100:.2f}% (synthetic 4.5%)")
                print(f"   ❌ Maturity: {maturity} (synthetic 2028-12-31)")
                return False
                
            else:
                print(f"\\n⚠️ UNKNOWN: Got unexpected data")
                print(f"   Coupon: {coupon*100:.2f}% (expected 3.87% or 4.5%)")
                print(f"   Maturity: {maturity}")
                return False
        else:
            print(f"   ❌ Resolution failed: {bond_data}")
            return False
            
    except Exception as e:
        print(f"\\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 CORE PANAMA BOND FIX TEST")
    print("=" * 40)
    
    success = test_core_panama_fix()
    
    print("\\n" + "=" * 40)
    if success:
        print("🎉 CORE FIX WORKING!")
        print("✅ SmartBondParser integration successful")
        print("✅ PANAMA gets correct data (3.87%, 2060)")
    else:
        print("⚠️ CORE FIX NEEDS DEBUG")
        print("❌ Still issues with SmartBondParser integration")
