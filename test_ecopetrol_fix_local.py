#!/usr/bin/env python3
"""
Test ECOPETROL fix locally
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google_analysis10 import process_bond_portfolio

def test_ecopetrol_description():
    """Test ECOPETROL with description only (should now find ISIN)"""
    print("🧪 Testing ECOPETROL with description only")
    print("=" * 60)
    
    portfolio_data = {
        "data": [
            {
                "description": "ECOPETROL SA, 5.875%, 28-May-2045",
                "CLOSING PRICE": 100.0,
                "WEIGHTING": 100.0
            }
        ]
    }
    
    db_path = './bonds_data.db'
    validated_db_path = './validated_quantlib_bonds.db'
    bloomberg_db_path = './bloomberg_index.db'
    
    print(f"📊 Processing with description: {portfolio_data['data'][0]['description']}")
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
            print(f"   Accrued Interest: {result.get('accrued_interest', 'N/A')}%")
            
            accrued = float(result.get('accrued_interest', 0))
            accrued_per_million = accrued * 10000
            print(f"   Accrued per million: ${accrued_per_million:,.2f}")
            
            print(f"\n💡 Expected:")
            print(f"   ISIN should be found: US279158AJ82")
            print(f"   Accrued per million: $22,847.22")
            
            if abs(accrued_per_million - 22847.22) < 1.0:
                print(f"\n✅ SUCCESS! ISIN lookup fix is working!")
                return True
            else:
                print(f"\n❌ Still not calculating correctly")
                return False
        else:
            print("❌ No results returned")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    success = test_ecopetrol_description()
    
    if success:
        print("\n🎉 ECOPETROL ISIN lookup fix is working correctly!")
    else:
        print("\n❌ ECOPETROL fix needs more work.")