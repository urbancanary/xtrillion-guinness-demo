#!/usr/bin/env python3
"""
Test Portfolio Spread Calculation - Google Analysis 10
=======================================================

This script tests whether the portfolio endpoint is returning spread values
for both individual bonds and the overall portfolio.

Expected Results:
- Individual bonds should have spread values (not 0 for non-Treasury bonds)  
- Portfolio should have weighted-average spread value
- Treasury bonds should have 0 spread
- Corporate/Sovereign bonds should have positive spread values
"""

import requests
import json

# API Configuration
API_BASE = "https://future-footing-414610.uc.r.appspot.com"
API_KEY = "gax10_demo_3j5h8m9k2p6r4t7w1q"

def test_portfolio_spread():
    """Test portfolio endpoint spread calculation"""
    
    print("🧪 Testing Portfolio Spread Calculation")
    print("=" * 60)
    
    # Test portfolio with bonds that should have different spread values
    test_portfolio = {
        "data": [
            {
                "BOND_CD": "T 3 15/08/52",
                "CLOSING PRICE": 71.66,
                "WEIGHTING": 40.0
            },
            {
                "BOND_CD": "PANAMA, 3.87%, 23-Jul-2060", 
                "CLOSING PRICE": 56.60,
                "WEIGHTING": 30.0
            },
            {
                "BOND_CD": "ECOPETROL SA, 5.875%, 28-May-2045",
                "CLOSING PRICE": 69.31,
                "WEIGHTING": 30.0
            }
        ]
    }
    
    print("📊 Test Portfolio:")
    print("   1. US Treasury (should have 0 spread)")
    print("   2. Panama sovereign (should have spread > 0)")  
    print("   3. Ecopetrol corporate (should have spread > 0)")
    print()
    
    try:
        print("🔄 Making API request...")
        response = requests.post(
            f"{API_BASE}/api/v1/portfolio/analysis",
            headers={
                'Content-Type': 'application/json',
                'X-API-Key': API_KEY
            },
            json=test_portfolio,
            timeout=30
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Portfolio Analysis Results:")
            
            # Check portfolio-level spread
            portfolio_metrics = result.get('portfolio_metrics', {})
            if portfolio_metrics:
                print("\n📊 Portfolio-Level Metrics:")
                print(f"   Portfolio Yield: {portfolio_metrics.get('portfolio_yield', 'N/A')}")
                print(f"   Portfolio Duration: {portfolio_metrics.get('portfolio_duration', 'N/A')}")
                print(f"   Portfolio Spread: {portfolio_metrics.get('portfolio_spread', 'N/A')} ⭐")
                print(f"   Total Bonds: {portfolio_metrics.get('total_bonds', 'N/A')}")
                print(f"   Success Rate: {portfolio_metrics.get('success_rate', 'N/A')}")
            
            # Check individual bond spreads
            bond_data = result.get('bond_data', [])
            if bond_data:
                print("\n🔍 Individual Bond Spreads:")
                for i, bond in enumerate(bond_data):
                    bond_name = bond.get('name', bond.get('description', f'Bond {i+1}'))
                    spread_value = bond.get('spread')
                    
                    print(f"   {i+1}. {bond_name[:50]}")
                    print(f"      Yield: {bond.get('yield', 'N/A')}")
                    print(f"      Duration: {bond.get('duration', 'N/A')}")
                    print(f"      Spread: {spread_value} ⭐")
                    print(f"      Status: {bond.get('status', 'N/A')}")
                    print()
            
            # Analysis of results
            print("📈 Spread Analysis:")
            
            # Check portfolio spread
            portfolio_spread = portfolio_metrics.get('portfolio_spread', 'N/A')
            if isinstance(portfolio_spread, str):
                if "0" in portfolio_spread or portfolio_spread == "N/A":
                    print("❌ ISSUE: Portfolio spread is 0 or missing")
                else:
                    print(f"✅ Portfolio spread calculated: {portfolio_spread}")
            elif isinstance(portfolio_spread, (int, float)):
                if portfolio_spread == 0:
                    print("❌ ISSUE: Portfolio spread is 0")
                else:
                    print(f"✅ Portfolio spread calculated: {portfolio_spread}")
            
            # Check individual bond spreads
            bonds_with_spread = 0
            treasury_count = 0
            
            for bond in bond_data:
                spread = bond.get('spread')
                bond_name = bond.get('name', '')
                
                # Check if it's a Treasury (should have 0 spread)
                if any(treasury_indicator in bond_name.upper() for treasury_indicator in ['TREASURY', 'T ', 'UST']):
                    treasury_count += 1
                    if spread is None or spread == "null" or str(spread) == "0" or str(spread) == "0 bps":
                        print(f"✅ Treasury bond correctly has 0 spread: {bond_name[:30]}")
                    else:
                        print(f"⚠️  Treasury bond has non-zero spread: {bond_name[:30]} = {spread}")
                else:
                    # Non-Treasury bonds should have positive spread
                    if spread is not None and spread != "null" and str(spread) != "0" and str(spread) != "0 bps":
                        bonds_with_spread += 1
                        print(f"✅ Non-Treasury bond has spread: {bond_name[:30]} = {spread}")
                    else:
                        print(f"❌ Non-Treasury bond missing spread: {bond_name[:30]} = {spread}")
            
            # Summary
            total_bonds = len(bond_data)
            expected_spread_bonds = total_bonds - treasury_count
            
            print(f"\n📊 Summary:")
            print(f"   Total bonds: {total_bonds}")
            print(f"   Treasury bonds: {treasury_count}")
            print(f"   Expected spread bonds: {expected_spread_bonds}")
            print(f"   Bonds with spread: {bonds_with_spread}")
            
            if bonds_with_spread == expected_spread_bonds:
                print("✅ All non-Treasury bonds have spread values")
            else:
                print(f"❌ {expected_spread_bonds - bonds_with_spread} bonds missing spread values")
                
            # Overall assessment
            portfolio_spread_ok = portfolio_spread != 0 and portfolio_spread != "0 bps" and portfolio_spread != "N/A"
            individual_spreads_ok = bonds_with_spread == expected_spread_bonds
            
            if portfolio_spread_ok and individual_spreads_ok:
                print("\n🎉 PASS: Both individual and portfolio spreads are working correctly")
            else:
                print("\n❌ FAIL: Spread calculation has issues")
                if not portfolio_spread_ok:
                    print("   - Portfolio spread is 0 or missing")
                if not individual_spreads_ok:
                    print("   - Some individual bonds missing spread values")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error text: {response.text[:500]}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_individual_bond_spread():
    """Test individual bond endpoint spread calculation"""
    
    print("\n" + "=" * 60)
    print("🧪 Testing Individual Bond Spread Calculation")
    print("=" * 60)
    
    test_bonds = [
        {
            "description": "T 3 15/08/52",
            "price": 71.66,
            "expected_spread": 0,
            "type": "Treasury"
        },
        {
            "description": "ECOPETROL SA, 5.875%, 28-May-2045", 
            "price": 69.31,
            "expected_spread": ">0",
            "type": "Corporate"
        },
        {
            "description": "PANAMA, 3.87%, 23-Jul-2060",
            "price": 56.60,
            "expected_spread": ">0", 
            "type": "Sovereign"
        }
    ]
    
    for i, bond in enumerate(test_bonds):
        print(f"\n📊 Testing Bond {i+1}: {bond['type']}")
        print(f"   Description: {bond['description']}")
        print(f"   Expected Spread: {bond['expected_spread']}")
        
        try:
            response = requests.post(
                f"{API_BASE}/api/v1/bond/analysis",
                headers={
                    'Content-Type': 'application/json',
                    'X-API-Key': API_KEY
                },
                json={
                    "description": bond['description'],
                    "price": bond['price']
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                analytics = result.get('analytics', {})
                spread = analytics.get('spread')
                z_spread = analytics.get('z_spread')
                
                print(f"   Result - Spread: {spread}, Z-Spread: {z_spread}")
                
                if bond['expected_spread'] == 0:
                    if spread == 0 or spread is None:
                        print(f"   ✅ {bond['type']} correctly has 0 spread")
                    else:
                        print(f"   ⚠️  {bond['type']} has unexpected spread: {spread}")
                else:  # expected_spread == ">0"
                    if spread and spread != 0:
                        print(f"   ✅ {bond['type']} has spread: {spread}")
                    else:
                        print(f"   ❌ {bond['type']} missing spread (got: {spread})")
                        
            else:
                print(f"   ❌ API Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Request Error: {e}")

if __name__ == "__main__":
    # Test both individual and portfolio spread calculations
    test_portfolio_spread()
    test_individual_bond_spread()
    
    print("\n" + "=" * 60)
    print("🎯 Test Complete")
    print("=" * 60)
    print("If spreads are showing as 0 for non-Treasury bonds, the spread")
    print("calculation logic needs to be implemented in the bond calculation engine.")
