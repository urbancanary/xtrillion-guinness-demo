#!/usr/bin/env python3
"""
ISIN vs Description Comparison Test
=================================

Compare the same bond using ISIN vs description to identify fractional yield differences.
Uses Treasury bond that exists in bloomberg_index.db.
"""

import sys
import requests
import json
from datetime import datetime

sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

def test_same_bond_isin_vs_description():
    """Test the same bond using both ISIN and description"""
    
    api_base_url = "https://future-footing-414610.uc.r.appspot.com"
    api_key = "gax10_demo_3j5h8m9k2p6r4t7w1q"
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }
    
    # Same Treasury bond - test both ways
    test_bond = {
        "isin": "US00206RGQ92",
        "description": "T 4.3 02/15/30",
        "price": 99.5
    }
    
    print(f"🔬 Testing Same Bond: ISIN vs Description")
    print(f"   ISIN: {test_bond['isin']}")
    print(f"   Description: {test_bond['description']}")
    print(f"   Price: {test_bond['price']}")
    
    results = {}
    
    # Test 1: ISIN-based API call
    print(f"\n📊 Test 1: API with ISIN")
    try:
        isin_payload = {
            "isin": test_bond['isin'],
            "price": test_bond['price']
        }
        
        response = requests.post(
            f"{api_base_url}/api/v1/bond/parse-and-calculate",
            headers=headers,
            json=isin_payload,
            timeout=30
        )
        
        results['isin_api'] = {
            'status_code': response.status_code,
            'response': response.json() if response.status_code == 200 else response.text
        }
        
        if response.status_code == 200:
            data = response.json()
            print("✅ ISIN API Success")
            if "bond" in data and "analytics" in data["bond"]:
                analytics = data["bond"]["analytics"]
                print(f"   Yield: {analytics.get('yield_to_maturity')}")
                print(f"   Duration: {analytics.get('modified_duration')}")
                print(f"   Convexity: {analytics.get('convexity')}")
        else:
            print(f"❌ ISIN API Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ ISIN API Error: {e}")
        results['isin_api'] = {'error': str(e)}
    
    # Test 2: Description-based API call
    print(f"\n📊 Test 2: API with Description")
    try:
        desc_payload = {
            "description": test_bond['description'],
            "price": test_bond['price']
        }
        
        response = requests.post(
            f"{api_base_url}/api/v1/bond/parse-and-calculate",
            headers=headers,
            json=desc_payload,
            timeout=30
        )
        
        results['desc_api'] = {
            'status_code': response.status_code,
            'response': response.json() if response.status_code == 200 else response.text
        }
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Description API Success")
            if "bond" in data and "analytics" in data["bond"]:
                analytics = data["bond"]["analytics"]
                print(f"   Yield: {analytics.get('yield_to_maturity')}")
                print(f"   Duration: {analytics.get('modified_duration')}")
                print(f"   Convexity: {analytics.get('convexity')}")
        else:
            print(f"❌ Description API Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Description API Error: {e}")
        results['desc_api'] = {'error': str(e)}
    
    # Test 3: Local Universal Parser for comparison
    print(f"\n📊 Test 3: Local Universal Parser")
    try:
        from core.universal_bond_parser import UniversalBondParser
        
        parser = UniversalBondParser(
            './bonds_data.db',
            './validated_quantlib_bonds.db',
            './bloomberg_index.db'
        )
        
        # Test ISIN parsing
        isin_spec = parser.parse_bond(test_bond['isin'])
        print(f"   ISIN Parsing Success: {getattr(isin_spec, 'parsing_success', False)}")
        print(f"   ISIN Conventions: {isin_spec.day_count}, {isin_spec.frequency}")
        
        # Test Description parsing  
        desc_spec = parser.parse_bond(test_bond['description'])
        print(f"   Description Parsing Success: {getattr(desc_spec, 'parsing_success', False)}")
        print(f"   Description Conventions: {desc_spec.day_count}, {desc_spec.frequency}")
        
        # Compare conventions
        if (isin_spec.day_count != desc_spec.day_count or 
            isin_spec.frequency != desc_spec.frequency):
            print(f"\n⚠️  CONVENTION MISMATCH DETECTED!")
            print(f"   ISIN: {isin_spec.day_count}, {isin_spec.frequency}")
            print(f"   DESC: {desc_spec.day_count}, {desc_spec.frequency}")
        else:
            print(f"\n✅ Local parser conventions match")
            
        results['local_parser'] = {
            'isin_success': getattr(isin_spec, 'parsing_success', False),
            'desc_success': getattr(desc_spec, 'parsing_success', False),
            'isin_conventions': f"{isin_spec.day_count}, {isin_spec.frequency}",
            'desc_conventions': f"{desc_spec.day_count}, {desc_spec.frequency}"
        }
        
    except Exception as e:
        print(f"❌ Local parser error: {e}")
        results['local_parser'] = {'error': str(e)}
    
    # Analysis and comparison
    print(f"\n🎯 ANALYSIS:")
    
    # Check for yield differences if both API calls succeeded
    if ('isin_api' in results and 'desc_api' in results and
        results['isin_api'].get('status_code') == 200 and
        results['desc_api'].get('status_code') == 200):
        
        try:
            isin_data = results['isin_api']['response']
            desc_data = results['desc_api']['response']
            
            isin_analytics = isin_data['bond']['analytics']
            desc_analytics = desc_data['bond']['analytics']
            
            isin_yield = isin_analytics.get('yield_to_maturity')
            desc_yield = desc_analytics.get('yield_to_maturity')
            
            if isin_yield is not None and desc_yield is not None:
                yield_diff = abs(float(isin_yield) - float(desc_yield))
                print(f"   Yield Difference: {yield_diff:.6f}")
                
                if yield_diff > 0.001:
                    print(f"   ⚠️  SIGNIFICANT YIELD DIFFERENCE! This is the fractional difference you mentioned.")
                    print(f"   ISIN Yield: {isin_yield}")
                    print(f"   Description Yield: {desc_yield}")
                else:
                    print(f"   ✅ Yield difference within tolerance")
            else:
                print(f"   ⚠️  Cannot compare yields - one or both are None")
                
        except Exception as e:
            print(f"   ❌ Yield comparison failed: {e}")
    else:
        print(f"   ⚠️  Cannot compare API results - one or both failed")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"isin_vs_description_comparison_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📁 Results saved to: {filename}")
    
    return results

if __name__ == "__main__":
    print(f"🔍 ISIN vs Description Comparison Test")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = test_same_bond_isin_vs_description()
    
    print(f"\n🎯 SUMMARY:")
    print(f"This test identifies the source of fractional yield differences")
    print(f"between ISIN-based and description-based parsing for the same bond.")
