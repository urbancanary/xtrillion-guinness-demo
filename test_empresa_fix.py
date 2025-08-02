#!/usr/bin/env python3
"""
Test EMPRESA MAESTRO with fixed date parsing
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bond_description_parser import SmartBondParser
from google_analysis10 import process_bond_portfolio

def test_parser_fix():
    """Test that the parser now correctly handles DD-Mon-YYYY dates"""
    print("🔍 Testing parser fix for DD-Mon-YYYY dates")
    print("=" * 60)
    
    # Initialize parser
    parser = SmartBondParser('./bloomberg_index.db', './validated_quantlib_bonds.db', './bloomberg_index.db')
    
    # Test parsing
    description = "EMPRESA MAESTRO, 4.7%, 07-May-2050"
    print(f"📝 Parsing: '{description}'")
    
    result = parser.parse_bond_description(description)
    
    if result:
        print(f"\n✅ Parsed successfully:")
        print(f"   Issuer: {result.get('issuer')}")
        print(f"   Coupon: {result.get('coupon')}%") 
        print(f"   Maturity: {result.get('maturity')}")
        
        # Check if maturity is correct
        if result.get('maturity') == '2050-05-07':
            print(f"   ✅ Maturity correctly parsed as May 7, 2050!")
        else:
            print(f"   ❌ Maturity still incorrect: {result.get('maturity')}")
    else:
        print(f"❌ Failed to parse")

def test_full_calculation():
    """Test the full calculation with the fixed parser"""
    print("\n\n🧪 Testing full EMPRESA MAESTRO calculation")
    print("=" * 60)
    
    portfolio_data = {
        "data": [
            {
                "description": "EMPRESA MAESTRO, 4.7%, 07-May-2050",
                "CLOSING PRICE": 100.0,
                "WEIGHTING": 100.0
            }
        ]
    }
    
    db_path = './bonds_data.db'
    validated_db_path = './validated_quantlib_bonds.db'
    bloomberg_db_path = './bloomberg_index.db'
    
    print(f"📊 Processing: {portfolio_data['data'][0]['description']}")
    print(f"   Settlement date: 2025-04-18")
    
    try:
        results = process_bond_portfolio(
            portfolio_data,
            db_path,
            validated_db_path,
            bloomberg_db_path,
            settlement_days=0,
            settlement_date="2025-04-18"
        )
        
        if len(results) > 0:
            result = results[0]
            
            print(f"\n📈 Results:")
            print(f"   ISIN: {result.get('isin', 'Not found')}")
            print(f"   Accrued interest: {result.get('accrued_interest', 'N/A')}%")
            
            accrued = float(result.get('accrued_interest', 0))
            accrued_per_million = accrued * 10000
            print(f"   Accrued per million: ${accrued_per_million:,.2f}")
            
            # Calculate implied days
            semi_annual_coupon = 4.7 / 2.0
            implied_days = (accrued / semi_annual_coupon) * 180
            print(f"   Implied days: {implied_days:.1f}")
            
            print(f"\n💡 Expected:")
            print(f"   Accrued per million: $21,019.44")
            print(f"   Expected days: 161 (Nov 7 to Apr 18)")
            
            diff = abs(accrued_per_million - 21019.44)
            if diff < 1.0:
                print(f"\n✅ SUCCESS! Date parsing fix works correctly!")
                return True
            else:
                print(f"\n❌ Still incorrect. Difference: ${diff:,.2f}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_parser_fix()
    success = test_full_calculation()
    
    if success:
        print("\n\n🎉 EMPRESA MAESTRO date parsing fix is working correctly!")
    else:
        print("\n\n❌ EMPRESA MAESTRO fix needs more work.")