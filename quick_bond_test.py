#!/usr/bin/env python3
"""
Quick Bond Test - Simple ISIN vs Description Comparison
=====================================================

Quick test to compare ISIN vs description parsing for the same bond.
Shows conventions and calculations side by side.

Usage:
    python quick_bond_test.py
"""

import sys
import json
import requests
from datetime import datetime

# Add path
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

def test_bond_comparison():
    """Test the same bond using ISIN and description"""
    
    # Test bond data
    test_bonds = [
        {
            "name": "US Treasury 3% 2052",
            "isin": "US912810TJ79", 
            "description": "T 3 08/15/52",
            "price": 71.66
        },
        {
            "name": "Panama 3.87% 2060",
            "isin": "US698299BL70",
            "description": "PANAMA, 3.87%, 23-Jul-2060", 
            "price": 56.60
        },
        {
            "name": "Treasury 4.625% 2025",
            "isin": "US912828Z290",
            "description": "T 4.625 02/15/25",
            "price": 99.5
        }
    ]
    
    api_base_url = "https://future-footing-414610.uc.r.appspot.com"
    api_key = "gax10_demo_3j5h8m9k2p6r4t7w1q"
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }
    
    for bond in test_bonds:
        print(f"\n{'='*80}")
        print(f"🔬 Testing: {bond['name']}")
        print(f"{'='*80}")
        
        # Test with ISIN
        print(f"\n📊 ISIN Test: {bond['isin']}")
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
                isin_data = response.json()
                print("✅ ISIN Success")
                
                if "bond" in isin_data:
                    bond_info = isin_data["bond"]
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
                print(f"❌ ISIN Failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ ISIN Error: {e}")
        
        # Test with Description  
        print(f"\n📊 Description Test: {bond['description']}")
        try:
            desc_payload = {
                "description": bond['description'],
                "price": bond['price']
            }
            
            response = requests.post(
                f"{api_base_url}/api/v1/bond/parse-and-calculate",
                headers=headers, 
                json=desc_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                desc_data = response.json()
                print("✅ Description Success")
                
                if "bond" in desc_data:
                    bond_info = desc_data["bond"]
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
                print(f"❌ Description Failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Description Error: {e}")
        
        print(f"\n" + "="*80)

def test_direct_calculate_bond_master():
    """Test direct calculate_bond_master function"""
    print(f"\n🔧 Testing Direct calculate_bond_master...")
    
    try:
        from bond_master_hierarchy import calculate_bond_master
        
        # Test with description
        portfolio_data = [{
            "description": "T 4.625 02/15/25",
            "price": 99.5,
            "weighting": 100.0
        }]
        
        results = calculate_bond_master(portfolio_data)
        
        if results and len(results) > 0:
            result = results[0]
            print("✅ Direct calculate_bond_master Success")
            print(f"   Conventions:")
            print(f"     Day Count: {result.get('day_count')}")
            print(f"     Frequency: {result.get('frequency')}")
            print(f"     Maturity: {result.get('maturity_date')}")
            print(f"     Coupon: {result.get('coupon_rate')}")
            print(f"   Analytics:")
            print(f"     Yield: {result.get('yield_to_maturity')}")
            print(f"     Duration: {result.get('modified_duration')}")
            print(f"     Convexity: {result.get('convexity')}")
        else:
            print("❌ No results returned")
            
    except Exception as e:
        print(f"❌ Direct test error: {e}")

def test_universal_parser():
    """Test Universal Parser directly"""
    print(f"\n🔍 Testing Universal Parser...")
    
    try:
        from core.universal_bond_parser import UniversalBondParser
        
        parser = UniversalBondParser(
            './bonds_data.db',
            './validated_quantlib_bonds.db',
            './bloomberg_index.db'
        )
        
        # Test with ISIN
        print(f"\n   ISIN: US912828Z290")
        isin_spec = parser.parse_bond("US912828Z290")
        print(f"     ✅ Parsing Success: {getattr(isin_spec, 'parsing_success', 'N/A')}")
        print(f"     Day Count: {isin_spec.day_count}")
        print(f"     Frequency: {isin_spec.frequency}")
        print(f"     Maturity: {isin_spec.maturity_date}")
        print(f"     Coupon: {isin_spec.coupon_rate}")
        
        # Test with description
        print(f"\n   Description: T 4.625 02/15/25")
        desc_spec = parser.parse_bond("T 4.625 02/15/25")
        print(f"     ✅ Parsing Success: {getattr(desc_spec, 'parsing_success', 'N/A')}")
        print(f"     Day Count: {desc_spec.day_count}")
        print(f"     Frequency: {desc_spec.frequency}")
        print(f"     Maturity: {desc_spec.maturity_date}")
        print(f"     Coupon: {desc_spec.coupon_rate}")
        
        # Compare conventions
        if (isin_spec.day_count != desc_spec.day_count or 
            isin_spec.frequency != desc_spec.frequency):
            print(f"\n⚠️  CONVENTION MISMATCH DETECTED!")
            print(f"   ISIN: {isin_spec.day_count}, {isin_spec.frequency}")
            print(f"   DESC: {desc_spec.day_count}, {desc_spec.frequency}")
        else:
            print(f"\n✅ Conventions match!")
            
    except Exception as e:
        print(f"❌ Universal parser test error: {e}")

if __name__ == "__main__":
    print(f"🚀 Quick Bond Test - ISIN vs Description")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test API endpoints
    test_bond_comparison()
    
    # Test direct function
    test_direct_calculate_bond_master()
    
    # Test Universal Parser
    test_universal_parser()
    
    print(f"\n🎯 Test Complete!")
