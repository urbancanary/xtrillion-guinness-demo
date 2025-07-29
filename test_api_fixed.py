#!/usr/bin/env python3
"""
Test Full API Pipeline with Fixed ISIN
====================================

Test if the API now works end-to-end with the corrected Universal Parser.
"""

import requests
import json

def test_api_with_fixed_isin():
    """Test API with Treasury ISIN that should now work"""
    
    api_base_url = "https://future-footing-414610.uc.r.appspot.com"
    api_key = "gax10_demo_3j5h8m9k2p6r4t7w1q"
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }
    
    # Test with Treasury ISIN that exists in bloomberg_index.db
    test_isin = "US00206RGQ92"  # T 4.3 02/15/30
    price = 99.5
    
    print(f"🧪 Testing API with corrected ISIN: {test_isin}")
    print(f"📊 Price: {price}")
    
    try:
        payload = {
            "isin": test_isin,
            "price": price
        }
        
        response = requests.post(
            f"{api_base_url}/api/v1/bond/parse-and-calculate",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"\n📡 API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Success!")
            
            if "bond" in data:
                bond_info = data["bond"]
                print(f"\n📋 Bond Information:")
                print(f"   ISIN: {bond_info.get('isin')}")
                print(f"   Description: {bond_info.get('description')}")
                print(f"   Coupon: {bond_info.get('coupon_rate')}")
                print(f"   Maturity: {bond_info.get('maturity_date')}")
                print(f"   Day Count: {bond_info.get('day_count')}")
                print(f"   Frequency: {bond_info.get('frequency')}")
                print(f"   Currency: {bond_info.get('currency')}")
                
                if "analytics" in bond_info:
                    analytics = bond_info["analytics"]
                    print(f"\n💹 Analytics:")
                    print(f"   Yield to Maturity: {analytics.get('yield_to_maturity')}")
                    print(f"   Modified Duration: {analytics.get('modified_duration')}")
                    print(f"   Convexity: {analytics.get('convexity')}")
                    print(f"   DV01: {analytics.get('dv01')}")
                    print(f"   Accrued Interest: {analytics.get('accrued_interest')}")
                    
                    if analytics.get('yield_to_maturity') is not None:
                        print(f"\n🎯 SUCCESS: Full pipeline working!")
                        print(f"   ISIN lookup ✅")
                        print(f"   Bond parsing ✅") 
                        print(f"   Calculations ✅")
                    else:
                        print(f"\n⚠️  Parsing successful but calculations missing")
                else:
                    print(f"\n⚠️  No analytics in response")
            else:
                print(f"\n⚠️  No bond data in response")
                
        else:
            print(f"❌ API Failed")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ API Test Error: {e}")

if __name__ == "__main__":
    test_api_with_fixed_isin()
