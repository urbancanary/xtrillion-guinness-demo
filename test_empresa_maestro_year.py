#!/usr/bin/env python3
"""
Test EMPRESA MAESTRO with full year
"""

import requests
import json

def test_with_full_year():
    """Test with 4-digit year"""
    print("🧪 Testing EMPRESA MAESTRO with full year format")
    print("=" * 60)
    
    url = "https://future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis"
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "xTr1ll10n_2025_pr0d"
    }
    
    # Test with full year
    payload = {
        "description": "BMETR 4.7 05/07/2050",
        "price": 100.0,
        "settlement_date": "2025-04-18"
    }
    
    print(f"📤 Testing: {payload['description']}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        result = response.json()
        
        if result.get('status') == 'success':
            analytics = result.get('analytics', {})
            accrued = analytics.get('accrued_interest', 0)
            accrued_per_million = accrued * 10000
            
            print(f"\n📊 Results:")
            print(f"   Accrued interest: {accrued:.6f}%")
            print(f"   Accrued per million: ${accrued_per_million:,.2f}")
            
            # Calculate implied days
            semi_annual_coupon = 4.7 / 2.0
            implied_days = (accrued / semi_annual_coupon) * 180
            print(f"   Implied days: {implied_days:.1f}")
            
            print(f"\n💡 Expected:")
            print(f"   Accrued per million: $21,019.44")
            print(f"   Expected days: 161")
            
            diff = abs(accrued_per_million - 21019.44)
            if diff < 1.0:
                print(f"\n✅ SUCCESS! Correct calculation with full year.")
            else:
                print(f"\n❌ Still incorrect. Difference: ${diff:,.2f}")
                
        else:
            print(f"❌ API Error: {result}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_local_calculation():
    """Test locally to debug"""
    print("\n\n🔍 Testing local calculation...")
    print("=" * 60)
    
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from google_analysis10 import process_bond_portfolio
    
    # Test with ISIN
    portfolio_data = {
        "data": [
            {
                "isin": "USP37466AS18",
                "description": "BMETR 4.7 05/07/2050",  # Full year
                "CLOSING PRICE": 100.0,
                "WEIGHTING": 100.0
            }
        ]
    }
    
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
            accrued = float(result.get('accrued_interest', 0))
            accrued_per_million = accrued * 10000
            
            print(f"📊 Local Results:")
            print(f"   ISIN: {result.get('isin', 'N/A')}")
            print(f"   Accrued interest: {accrued:.6f}%")
            print(f"   Accrued per million: ${accrued_per_million:,.2f}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_full_year()
    test_local_calculation()