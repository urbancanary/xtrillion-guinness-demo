#!/usr/bin/env python3
"""
Test PEMEX bond fix in production
"""

import requests
import json

def test_pemex_production():
    """Test PEMEX bond against production API"""
    print("🧪 Testing PEMEX bond fix in PRODUCTION")
    print("=" * 60)
    
    url = "https://future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis"
    
    payload = {
        "description": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060",
        "price": 100.0,
        "settlement_date": "2025-04-18"
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "xTr1ll10n_2025_pr0d"
    }
    
    print(f"📤 Sending request to production API...")
    print(f"   URL: {url}")
    print(f"   Settlement date: {payload['settlement_date']} (Good Friday)")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        result = response.json()
        
        if result.get('status') == 'success':
            analytics = result.get('analytics', {})
            accrued = analytics.get('accrued_interest', 0)
            accrued_per_million = accrued * 10000
            
            print(f"\n📊 Production API Results:")
            print(f"   Settlement date: {analytics.get('settlement_date', 'N/A')}")
            print(f"   Accrued interest: {accrued:.6f}%") 
            print(f"   Accrued per million: ${accrued_per_million:,.2f}")
            
            print(f"\n💡 Expected Result:")
            print(f"   80 days from Jan 28 to Apr 18")
            print(f"   Accrued interest: 1.544444%")
            print(f"   Accrued per million: $15,444.44")
            
            # Check if fix worked
            expected_accrued_per_million = 15444.44
            if abs(accrued_per_million - expected_accrued_per_million) < 1.0:
                print("\n✅ PRODUCTION FIX SUCCESSFUL!")
                print("   The settlement date is being used correctly.")
                print("   No T+3 adjustment is being applied.")
                return True
            else:
                print("\n❌ Production still showing incorrect accrued.")
                print(f"   Difference: ${abs(accrued_per_million - expected_accrued_per_million):,.2f}")
                return False
        else:
            print(f"❌ API Error: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_pemex_production()
    
    if success:
        print("\n\n🎉 PEMEX bond settlement date fix is working correctly in PRODUCTION!")
    else:
        print("\n\n❌ Production deployment may need verification.")