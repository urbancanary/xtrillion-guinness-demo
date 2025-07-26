#!/usr/bin/env python3
"""
XTrillion Core Bond Calculation Engine Test
Compare ISIN vs Description-only calculation routes
"""

import requests
import json
import pandas as pd
from datetime import datetime

def test_xtrillion_core_comparison():
    """Test XTrillion Core with ISIN vs description-only routes"""
    
    # Test bond data - US Treasury 3% 15/08/52
    test_bond = {
        "isin": "US912810TJ79",
        "price": 71.66,
        "description": "T 3 15/08/52"
    }
    
    print("🚀 XTrillion Core Bond Calculation Engine Test")
    print("=" * 70)
    print(f"Bond: {test_bond['description']}")
    print(f"ISIN: {test_bond['isin']}")
    print(f"Price: {test_bond['price']}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # API endpoint
    api_url = "http://localhost:8080/api/v1/bond/parse-and-calculate"
    results = {}
    
    # Test 1: With ISIN (ISIN hierarchy route)
    print("📊 Test 1: ISIN + Description → ISIN Hierarchy Route")
    print("-" * 50)
    
    request_with_isin = {
        "isin": test_bond["isin"],
        "price": test_bond["price"],
        "description": test_bond["description"]
    }
    
    try:
        response_with_isin = requests.post(
            api_url,
            json=request_with_isin,
            headers={"Content-Type": "application/json"},
            params={"technical": "true"},  # Get technical response
            timeout=30
        )
        
        if response_with_isin.status_code == 200:
            result_with_isin = response_with_isin.json()
            print("✅ SUCCESS - ISIN hierarchy route")
            route_used = result_with_isin.get('metadata', {}).get('route_used', 'unknown')
            calc_engine = result_with_isin.get('metadata', {}).get('calculation_engine', 'unknown')
            print(f"Route used: {route_used}")
            print(f"Calculation engine: {calc_engine}")
            results['with_isin'] = result_with_isin
        else:
            print(f"❌ FAILED - Status: {response_with_isin.status_code}")
            print(f"Response: {response_with_isin.text}")
            results['with_isin'] = None
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['with_isin'] = None
    
    print()
    
    # Test 2: Without ISIN (Parse hierarchy route)  
    print("📊 Test 2: Description Only → Parse Hierarchy Route")
    print("-" * 50)
    
    request_without_isin = {
        "price": test_bond["price"],
        "description": test_bond["description"]
        # No ISIN provided - should trigger parse hierarchy
    }
    
    try:
        response_without_isin = requests.post(
            api_url,
            json=request_without_isin,
            headers={"Content-Type": "application/json"},
            params={"technical": "true"},  # Get technical response
            timeout=30
        )
        
        if response_without_isin.status_code == 200:
            result_without_isin = response_without_isin.json()
            print("✅ SUCCESS - Parse hierarchy route")
            route_used = result_without_isin.get('metadata', {}).get('route_used', 'unknown')
            calc_engine = result_without_isin.get('metadata', {}).get('calculation_engine', 'unknown')
            print(f"Route used: {route_used}")
            print(f"Calculation engine: {calc_engine}")
            results['without_isin'] = result_without_isin
        else:
            print(f"❌ FAILED - Status: {response_without_isin.status_code}")
            print(f"Response: {response_without_isin.text}")
            results['without_isin'] = None
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results['without_isin'] = None
    
    print()
    print("🔄 Creating comparison table...")
    
    # Create comparison table
    create_comparison_table(results, test_bond)
    
    return results

def create_comparison_table(results, test_bond):
    """Create side-by-side comparison table"""
    
    print("\n" + "=" * 80)
    print("📊 XTRILLION CORE CALCULATION RESULTS COMPARISON")
    print("=" * 80)
    
    # Check if we have both results
    with_isin = results.get('with_isin')
    without_isin = results.get('without_isin')
    
    if not with_isin or not without_isin:
        print("❌ Cannot create comparison - missing results")
        if with_isin:
            print("✅ ISIN route: SUCCESS")
        else:
            print("❌ ISIN route: FAILED")
            
        if without_isin:
            print("✅ Parse route: SUCCESS")
        else:
            print("❌ Parse route: FAILED")
        return
    
    # Extract key metrics for comparison
    comparison_data = []
    
    # Basic info
    comparison_data.append([
        "🎯 Route Used",
        with_isin.get('metadata', {}).get('route_used', 'unknown'),
        without_isin.get('metadata', {}).get('route_used', 'unknown')
    ])
    
    comparison_data.append([
        "🔧 Calculation Engine", 
        with_isin.get('metadata', {}).get('calculation_engine', 'unknown'),
        without_isin.get('metadata', {}).get('calculation_engine', 'unknown')
    ])
    
    # Bond identification
    with_isin_bond = with_isin.get('bond_info', {})
    without_isin_bond = without_isin.get('bond_info', {})
    
    comparison_data.append([
        "📋 Identified ISIN",
        with_isin_bond.get('isin', 'N/A'),
        without_isin_bond.get('isin', 'N/A')
    ])
    
    comparison_data.append([
        "📝 Bond Name",
        with_isin_bond.get('name', 'N/A'),
        without_isin_bond.get('name', 'N/A')
    ])
    
    # Financial metrics
    with_isin_calcs = with_isin.get('calculations', {})
    without_isin_calcs = without_isin.get('calculations', {})
    
    comparison_data.append([
        "💰 Yield (%)",
        f"{with_isin_calcs.get('yield', 0):.4f}",
        f"{without_isin_calcs.get('yield', 0):.4f}"
    ])
    
    comparison_data.append([
        "⏱️ Duration (years)",
        f"{with_isin_calcs.get('duration', 0):.4f}",
        f"{without_isin_calcs.get('duration', 0):.4f}"
    ])
    
    comparison_data.append([
        "📈 Spread (bps)",
        f"{with_isin_calcs.get('spread', 0):.2f}",
        f"{without_isin_calcs.get('spread', 0):.2f}"
    ])
    
    comparison_data.append([
        "💵 Clean Price",
        f"{with_isin_calcs.get('clean_price', 0):.4f}",
        f"{without_isin_calcs.get('clean_price', 0):.4f}"
    ])
    
    comparison_data.append([
        "💸 Dirty Price", 
        f"{with_isin_calcs.get('dirty_price', 0):.4f}",
        f"{without_isin_calcs.get('dirty_price', 0):.4f}"
    ])
    
    comparison_data.append([
        "🏦 Accrued Interest",
        f"{with_isin_calcs.get('accrued_interest', 0):.4f}",
        f"{without_isin_calcs.get('accrued_interest', 0):.4f}"
    ])
    
    # Create formatted table
    print(f"{'Metric':<25} {'ISIN Route':<20} {'Parse Route':<20} {'Match':<10}")
    print("-" * 80)
    
    for row in comparison_data:
        metric, isin_val, parse_val = row
        
        # Check if values match (for numeric values)
        try:
            if metric in ["💰 Yield (%)", "⏱️ Duration (years)", "📈 Spread (bps)", "💵 Clean Price", "💸 Dirty Price", "🏦 Accrued Interest"]:
                isin_num = float(isin_val)
                parse_num = float(parse_val)
                match = "✅ YES" if abs(isin_num - parse_num) < 0.001 else f"❌ NO (Δ{abs(isin_num - parse_num):.4f})"
            else:
                match = "✅ YES" if isin_val == parse_val else "❌ NO"
        except:
            match = "✅ YES" if isin_val == parse_val else "❌ NO"
        
        print(f"{metric:<25} {isin_val:<20} {parse_val:<20} {match:<10}")
    
    print("\n" + "=" * 80)
    print("🎯 ANALYSIS SUMMARY")
    print("=" * 80)
    
    # Calculate differences
    try:
        yield_diff = abs(float(with_isin_calcs.get('yield', 0)) - float(without_isin_calcs.get('yield', 0)))
        duration_diff = abs(float(with_isin_calcs.get('duration', 0)) - float(without_isin_calcs.get('duration', 0)))
        spread_diff = abs(float(with_isin_calcs.get('spread', 0)) - float(without_isin_calcs.get('spread', 0)))
        
        print(f"📊 Yield Difference: {yield_diff:.6f}% ({'✅ EXCELLENT' if yield_diff < 0.001 else '⚠️ REVIEW'})")
        print(f"📊 Duration Difference: {duration_diff:.6f} years ({'✅ EXCELLENT' if duration_diff < 0.001 else '⚠️ REVIEW'})")
        print(f"📊 Spread Difference: {spread_diff:.6f} bps ({'✅ EXCELLENT' if spread_diff < 0.001 else '⚠️ REVIEW'})")
        
        overall_match = yield_diff < 0.001 and duration_diff < 0.001 and spread_diff < 0.001
        print(f"\n🏆 OVERALL ASSESSMENT: {'✅ PERFECT MATCH - XTrillion Core unified hierarchy working!' if overall_match else '⚠️ DIFFERENCES DETECTED - Review calculation paths'}")
        
    except Exception as e:
        print(f"❌ Error calculating differences: {e}")
    
    print(f"\n🔧 Both routes using: XTrillion Core calculation engine")
    print(f"📋 Test bond: {test_bond['description']} (ISIN: {test_bond['isin']})")
    print(f"💰 Input price: {test_bond['price']}")

if __name__ == "__main__":
    results = test_xtrillion_core_comparison()
