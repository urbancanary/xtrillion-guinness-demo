#!/usr/bin/env python3
"""
Real ISIN vs Description Test
==========================

Tests with actual ISINs that exist in the database to isolate the convention discrepancy issue.
"""

import sys
import json
import requests
from datetime import datetime

# Add path
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

def test_real_bonds():
    """Test with bonds that actually exist in the database"""
    
    # Real bonds from the database
    real_bonds = [
        {
            "name": "US Treasury 3% 2052",
            "isin": "US91282CJZ59",
            "description_exact": "US TREASURY N/B, 3%, 15-Aug-2052",
            "description_simple": "T 3 08/15/52",
            "price": 71.66
        },
        {
            "name": "ABBV 4.625% 2042", 
            "isin": "US00287YCZ07",
            "description_exact": "ABBV 4 ⅝ 10/01/42",
            "description_simple": "ABBV 4.625 10/01/42",
            "price": 95.50
        }
    ]
    
    api_base_url = "https://future-footing-414610.uc.r.appspot.com"
    api_key = "gax10_demo_3j5h8m9k2p6r4t7w1q"
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }
    
    for bond in real_bonds:
        print(f"\n{'='*100}")
        print(f"🔬 Testing: {bond['name']}")
        print(f"   ISIN: {bond['isin']}")
        print(f"   Description: {bond['description_exact']}")
        print(f"{'='*100}")
        
        # Results storage
        results = {}
        
        # Test 1: ISIN API call
        print(f"\n📊 Test 1: API with ISIN")
        try:
            isin_payload = {
                "isin": bond['isin'],
                "price": bond['price']
            }
            
            response = requests.post(
                f"{api_base_url}/api/v1/bond/parse-and-calculate",
                headers=headers,
                json=isin_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                results['isin_api'] = data
                print("✅ ISIN API Success")
                
                if "bond" in data:
                    bond_info = data["bond"]
                    print(f"   Conventions:")
                    print(f"     Day Count: {bond_info.get('day_count')}")
                    print(f"     Frequency: {bond_info.get('frequency')}")
                    print(f"     Maturity: {bond_info.get('maturity_date')}")
                    print(f"     Coupon: {bond_info.get('coupon_rate')}")
                    
                    if "analytics" in bond_info:
                        analytics = bond_info["analytics"]
                        print(f"   Analytics:")
                        print(f"     Yield: {analytics.get('yield_to_maturity')}")
                        print(f"     Duration: {analytics.get('modified_duration')}")
                        print(f"     Convexity: {analytics.get('convexity')}")
            else:
                print(f"❌ ISIN API Failed: {response.status_code}")
                print(f"   Response: {response.text}")
                results['isin_api'] = {"error": response.text}
                
        except Exception as e:
            print(f"❌ ISIN API Error: {e}")
            results['isin_api'] = {"error": str(e)}
        
        # Test 2: Description API call (exact)
        print(f"\n📊 Test 2: API with Exact Description")
        try:
            desc_payload = {
                "description": bond['description_exact'],
                "price": bond['price']
            }
            
            response = requests.post(
                f"{api_base_url}/api/v1/bond/parse-and-calculate",
                headers=headers,
                json=desc_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                results['desc_exact_api'] = data
                print("✅ Description API Success")
                
                if "bond" in data:
                    bond_info = data["bond"]
                    print(f"   Conventions:")
                    print(f"     Day Count: {bond_info.get('day_count')}")
                    print(f"     Frequency: {bond_info.get('frequency')}")
                    print(f"     Maturity: {bond_info.get('maturity_date')}")
                    print(f"     Coupon: {bond_info.get('coupon_rate')}")
                    
                    if "analytics" in bond_info:
                        analytics = bond_info["analytics"]
                        print(f"   Analytics:")
                        print(f"     Yield: {analytics.get('yield_to_maturity')}")
                        print(f"     Duration: {analytics.get('modified_duration')}")
                        print(f"     Convexity: {analytics.get('convexity')}")
            else:
                print(f"❌ Description API Failed: {response.status_code}")
                print(f"   Response: {response.text}")
                results['desc_exact_api'] = {"error": response.text}
                
        except Exception as e:
            print(f"❌ Description API Error: {e}")
            results['desc_exact_api'] = {"error": str(e)}
        
        # Test 3: Universal Parser Direct Test
        print(f"\n📊 Test 3: Universal Parser Direct")
        try:
            from core.universal_bond_parser import UniversalBondParser
            
            parser = UniversalBondParser(
                './bonds_data.db',
                './validated_quantlib_bonds.db',
                './bloomberg_index.db'
            )
            
            # Test ISIN
            isin_spec = parser.parse_bond(bond['isin'])
            print(f"   ISIN Parsing:")
            print(f"     Success: {getattr(isin_spec, 'parsing_success', 'N/A')}")
            print(f"     Day Count: {isin_spec.day_count}")
            print(f"     Frequency: {isin_spec.frequency}")
            print(f"     Maturity: {isin_spec.maturity_date}")
            print(f"     Coupon: {isin_spec.coupon_rate}")
            
            # Test Description
            desc_spec = parser.parse_bond(bond['description_exact'])
            print(f"   Description Parsing:")
            print(f"     Success: {getattr(desc_spec, 'parsing_success', 'N/A')}")
            print(f"     Day Count: {desc_spec.day_count}")
            print(f"     Frequency: {desc_spec.frequency}")
            print(f"     Maturity: {desc_spec.maturity_date}")
            print(f"     Coupon: {desc_spec.coupon_rate}")
            
            # Convention comparison
            if (isin_spec.day_count != desc_spec.day_count or 
                isin_spec.frequency != desc_spec.frequency):
                print(f"\n⚠️  CONVENTION MISMATCH!")
                print(f"   ISIN: {isin_spec.day_count}, {isin_spec.frequency}")
                print(f"   DESC: {desc_spec.day_count}, {desc_spec.frequency}")
            else:
                print(f"\n✅ Universal Parser conventions match!")
                
            results['universal_parser'] = {
                'isin': {
                    'parsing_success': getattr(isin_spec, 'parsing_success', 'N/A'),
                    'day_count': isin_spec.day_count,
                    'frequency': isin_spec.frequency,
                    'maturity_date': isin_spec.maturity_date,
                    'coupon_rate': isin_spec.coupon_rate
                },
                'description': {
                    'parsing_success': getattr(desc_spec, 'parsing_success', 'N/A'),
                    'day_count': desc_spec.day_count,
                    'frequency': desc_spec.frequency,
                    'maturity_date': desc_spec.maturity_date,
                    'coupon_rate': desc_spec.coupon_rate
                }
            }
            
        except Exception as e:
            print(f"❌ Universal Parser Error: {e}")
            results['universal_parser'] = {"error": str(e)}
        
        # Analysis Summary
        print(f"\n🎯 ANALYSIS SUMMARY:")
        
        # Check if ISIN and Description give different results
        if 'isin_api' in results and 'desc_exact_api' in results:
            if 'bond' in results['isin_api'] and 'bond' in results['desc_exact_api']:
                isin_analytics = results['isin_api']['bond'].get('analytics', {})
                desc_analytics = results['desc_exact_api']['bond'].get('analytics', {})
                
                isin_yield = isin_analytics.get('yield_to_maturity')
                desc_yield = desc_analytics.get('yield_to_maturity')
                
                if isin_yield is not None and desc_yield is not None:
                    yield_diff = abs(float(isin_yield) - float(desc_yield))
                    print(f"   Yield Difference: {yield_diff:.6f}")
                    
                    if yield_diff > 0.001:  # More than 0.1 basis points
                        print(f"   ⚠️  SIGNIFICANT YIELD DIFFERENCE DETECTED!")
                    else:
                        print(f"   ✅ Yield difference within tolerance")
        
        # Save results for this bond
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"real_bond_test_{bond['name'].replace(' ', '_')}_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"   📁 Results saved to: {filename}")

if __name__ == "__main__":
    print(f"🚀 Real ISIN vs Description Test")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Testing with bonds that actually exist in the database...")
    
    test_real_bonds()
    
    print(f"\n🎯 Test Complete!")
    print(f"\nNext Steps:")
    print(f"1. Review any convention mismatches")
    print(f"2. Check yield calculation differences") 
    print(f"3. Investigate Universal Parser ISIN vs Description logic")
