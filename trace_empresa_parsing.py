#!/usr/bin/env python3
"""
Trace EMPRESA MAESTRO parsing and calculation
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google_analysis10 import process_bond_portfolio
import logging

# Enable detailed logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def trace_empresa():
    """Trace the full processing of EMPRESA MAESTRO"""
    print("🔍 Tracing EMPRESA MAESTRO processing")
    print("=" * 60)
    
    # Test with the exact input that shows wrong result
    portfolio_data = {
        "data": [
            {
                "description": "EMPRESA MAESTRO, 4.7%, 07-May-2050",
                "CLOSING PRICE": 100.0,
                "WEIGHTING": 100.0
            }
        ]
    }
    
    print(f"📋 Input description: {portfolio_data['data'][0]['description']}")
    print(f"   Settlement date: 2025-04-18")
    print()
    
    db_path = './bonds_data.db'
    validated_db_path = './validated_quantlib_bonds.db' 
    bloomberg_db_path = './bloomberg_index.db'
    
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
            
            print(f"\n📊 Results:")
            print(f"   ISIN found: {result.get('isin', 'None')}")
            print(f"   Accrued interest: {result.get('accrued_interest', 'N/A')}%")
            
            accrued = float(result.get('accrued_interest', 0))
            accrued_per_million = accrued * 10000
            print(f"   Accrued per million: ${accrued_per_million:,.2f}")
            
            # Calculate implied days
            semi_annual_coupon = 4.7 / 2.0
            implied_days = (accrued / semi_annual_coupon) * 180
            print(f"   Implied days: {implied_days:.1f}")
            
            print(f"\n💡 Analysis:")
            print(f"   Expected: $21,019.44 (161 days)")
            print(f"   Got: ${accrued_per_million:,.2f} ({implied_days:.1f} days)")
            
            # Work out what coupon dates this implies
            if implied_days < 110:  # Around 103 days
                print(f"\n   This suggests coupon dates of Jan/Jul instead of May/Nov")
                print(f"   The maturity might be parsed as July 5 instead of May 7")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def check_parser_directly():
    """Check the parser directly"""
    print("\n\n🔍 Checking parser directly")
    print("=" * 60)
    
    from bond_description_parser import SmartBondParser
    
    # Initialize parser
    db_path = './bonds_data.db'
    validated_db_path = './validated_quantlib_bonds.db'
    bloomberg_db_path = './bloomberg_index.db'
    
    parser = SmartBondParser(bloomberg_db_path, validated_db_path, bloomberg_db_path)
    
    # Test parsing
    description = "EMPRESA MAESTRO, 4.7%, 07-May-2050"
    print(f"📝 Parsing: '{description}'")
    
    result = parser.parse_bond_description(description)
    
    if result:
        print(f"\n✅ Parsed successfully:")
        print(f"   Issuer: {result.get('issuer')}")
        print(f"   Coupon: {result.get('coupon')}%")
        print(f"   Maturity: {result.get('maturity')}")
        print(f"   ISIN: {result.get('isin', 'Not found')}")
        
        # Check if maturity is correct
        if result.get('maturity') == '2050-05-07':
            print(f"   ✅ Maturity correctly parsed as May 7, 2050")
        else:
            print(f"   ❌ Maturity incorrectly parsed!")
    else:
        print(f"❌ Failed to parse")

if __name__ == "__main__":
    trace_empresa()
    check_parser_directly()