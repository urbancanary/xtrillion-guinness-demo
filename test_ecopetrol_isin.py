#!/usr/bin/env python3
"""
Test ECOPETROL bond with ISIN
"""

import requests
import json

def test_ecopetrol_with_isin():
    """Test ECOPETROL bond using ISIN"""
    print("🧪 Testing ECOPETROL bond with ISIN")
    print("=" * 60)
    
    url = "https://future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis"
    
    payload = {
        "isin": "US279158AJ82",  # ECOPETROL ISIN
        "description": "ECOPETROL SA, 5.875%, 28-May-2045",
        "price": 100.0,
        "settlement_date": "2025-04-18"
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "xTr1ll10n_2025_pr0d"
    }
    
    print(f"📤 Testing with ISIN...")
    print(f"   ISIN: {payload['isin']}")
    print(f"   Settlement date: {payload['settlement_date']}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        result = response.json()
        
        if result.get('status') == 'success':
            analytics = result.get('analytics', {})
            accrued = analytics.get('accrued_interest', 0)
            accrued_per_million = accrued * 10000
            
            print(f"\n📊 Production API Results:")
            print(f"   Accrued interest: {accrued:.6f}%") 
            print(f"   Accrued per million: ${accrued_per_million:,.2f}")
            
            print(f"\n💡 Expected from validated DB:")
            print(f"   Accrued per million: $22,847.22")
            print(f"   Difference: ${abs(accrued_per_million - 22847.22):,.2f}")
            
            # Calculate implied days
            semi_annual_coupon = 5.875 / 2.0
            implied_days = (accrued / semi_annual_coupon) * 180
            print(f"\n📐 Analysis:")
            print(f"   Semi-annual coupon: {semi_annual_coupon}%")
            print(f"   Implied days: {implied_days:.1f}")
            print(f"   Expected days: 140")
            print(f"   Day difference: {140 - implied_days:.1f}")
            
            return accrued_per_million
            
        else:
            print(f"❌ API Error: {result}")
            return None
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def test_local_calculation():
    """Test local calculation to debug"""
    print("\n\n🔍 Testing local calculation...")
    print("=" * 60)
    
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from google_analysis10 import process_bond_portfolio
    
    portfolio_data = {
        "data": [
            {
                "isin": "US279158AJ82",
                "description": "ECOPETROL SA, 5.875%, 28-May-2045",
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
            print(f"   Accrued interest: {accrued:.6f}%")
            print(f"   Accrued per million: ${accrued_per_million:,.2f}")
            
            return accrued_per_million
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    prod_result = test_ecopetrol_with_isin()
    local_result = test_local_calculation()
    
    print("\n\n📊 Summary:")
    print("=" * 60)
    print(f"   Production result: ${prod_result:,.2f}" if prod_result else "   Production: Failed")
    print(f"   Local result: ${local_result:,.2f}" if local_result else "   Local: Failed")
    print(f"   Expected: $22,847.22")
    
    if prod_result and abs(prod_result - 22847.22) < 1.0:
        print("\n✅ ECOPETROL is calculating correctly!")
    else:
        print("\n❌ ECOPETROL accrued needs investigation")