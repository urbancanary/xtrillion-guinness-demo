#!/usr/bin/env python3
"""
Test EMPRESA MAESTRO in production
"""

import requests
import json

def test_empresa_production():
    """Test EMPRESA MAESTRO bond in production"""
    print("🧪 Testing EMPRESA MAESTRO in Production")
    print("=" * 60)
    
    url = "https://future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis"
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "xTr1ll10n_2025_pr0d"
    }
    
    # Test with the description format
    payload = {
        "description": "EMPRESA MAESTRO, 4.7%, 07-May-2050",
        "price": 100.0,
        "settlement_date": "2025-04-18"
    }
    
    print(f"📤 Testing with description format...")
    print(f"   Description: {payload['description']}")
    print(f"   Settlement: {payload['settlement_date']}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        result = response.json()
        
        if result.get('status') == 'success':
            analytics = result.get('analytics', {})
            accrued = analytics.get('accrued_interest', 0)
            accrued_per_million = accrued * 10000
            
            print(f"\n📊 Production Results:")
            print(f"   Accrued interest: {accrued:.6f}%")
            print(f"   Accrued per million: ${accrued_per_million:,.2f}")
            
            print(f"\n💡 Expected:")
            print(f"   Accrued per million: $21,019.44")
            
            diff = abs(accrued_per_million - 21019.44)
            if diff < 1.0:
                print(f"\n✅ PRODUCTION FIX SUCCESSFUL!")
                print(f"   Date parsing is working correctly.")
                return True
            else:
                print(f"\n❌ Production still showing incorrect value.")
                print(f"   Difference: ${diff:,.2f}")
                return False
        else:
            print(f"❌ API Error: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_empresa_production()
    
    if success:
        print("\n\n🎉 EMPRESA MAESTRO date parsing fix is working correctly in PRODUCTION!")
    else:
        print("\n\n❌ Production deployment may need verification.")