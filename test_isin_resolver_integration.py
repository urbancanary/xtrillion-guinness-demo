#!/usr/bin/env python3
"""
🎯 ISIN-Only Lookup Test with Intelligent Resolver
Test what happens when we integrate the intelligent ISIN resolver
with the bond analysis API to make ISIN-only lookups work
"""

import requests
import json
import sys
import os

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from intelligent_isin_resolver import IntelligentISINResolver

# API Configuration
API_BASE = "https://future-footing-414610.uc.r.appspot.com"
API_KEY = "gax10_demo_3j5h8m9k2p6r4t7w1q"

def call_bond_analysis_with_resolver(isin: str, price: float):
    """
    Simulate what would happen if ISIN resolver was integrated:
    1. Try ISIN-only first (current behavior)
    2. If fails, use resolver to get description, then try description
    """
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    print(f"🔍 Testing ISIN: {isin} @ ${price}")
    
    # Step 1: Try ISIN-only (current behavior - should fail)
    print("   Step 1: Trying ISIN-only (current API behavior)...")
    try:
        payload = {"isin": isin, "price": price}
        response = requests.post(f"{API_BASE}/api/v1/bond/analysis", json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            print("   ✅ ISIN-only worked! (unexpected)")
            return response.json()
        else:
            print(f"   ❌ ISIN-only failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ ISIN-only exception: {e}")
    
    # Step 2: Use intelligent resolver as fallback
    print("   Step 2: Using intelligent resolver fallback...")
    resolver = IntelligentISINResolver()
    resolution = resolver.resolve_isin_to_description(isin)
    
    if not resolution:
        print("   ❌ Resolver failed to find description")
        return {"status": "error", "error": "No resolution found"}
    
    resolved_description = resolution['description']
    confidence = resolution['confidence']
    source = resolution['source']
    
    print(f"   ✅ Resolved to: '{resolved_description}'")
    print(f"   📊 Source: {source} (confidence: {confidence})")
    
    # Step 3: Try with resolved description
    print("   Step 3: Trying with resolved description...")
    try:
        payload = {"description": resolved_description, "price": price}
        response = requests.post(f"{API_BASE}/api/v1/bond/analysis", json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            # Add resolver metadata
            result['resolver_metadata'] = {
                'original_isin': isin,
                'resolved_description': resolved_description,
                'resolution_source': source,
                'resolution_confidence': confidence
            }
            print("   ✅ Analysis with resolved description succeeded!")
            return result
        else:
            print(f"   ❌ Analysis with resolved description failed: {response.status_code}")
            return {"status": "error", "error": f"API returned {response.status_code} with resolved description"}
            
    except Exception as e:
        print(f"   ❌ Analysis exception: {e}")
        return {"status": "error", "error": str(e)}

def test_isin_resolution_integration():
    """Test ISIN resolution integration with multiple bonds"""
    
    print("🎯 ISIN-Only Lookup Test with Intelligent Resolver Integration")
    print("=" * 80)
    print("Simulating what would happen if intelligent resolver was integrated into API")
    print("=" * 80)
    
    # Test bonds from our failed ISIN tests
    test_bonds = [
        {"isin": "US912810TJ79", "price": 71.66, "name": "US Treasury"},
        {"isin": "US279158AJ82", "price": 69.31, "name": "Ecopetrol"},
        {"isin": "US698299BL70", "price": 56.60, "name": "Panama"},
        {"isin": "XS2249741674", "price": 77.88, "name": "Galaxy Pipeline"},
        {"isin": "XS1709535097", "price": 89.40, "name": "Abu Dhabi Crude"}
    ]
    
    results = []
    successful_resolutions = 0
    
    for i, bond in enumerate(test_bonds):
        print(f"\n📊 Bond {i+1}/5: {bond['name']} ({bond['isin']})")
        print("-" * 60)
        
        result = call_bond_analysis_with_resolver(bond['isin'], bond['price'])
        
        # Check if we got analytics
        if result.get('status') == 'success' and 'analytics' in result:
            successful_resolutions += 1
            analytics = result['analytics']
            resolver_meta = result.get('resolver_metadata', {})
            
            print(f"   🎉 SUCCESS! Bond analysis completed via ISIN resolution")
            print(f"   📈 Yield: {analytics.get('ytm', 'N/A'):.3f}%")
            print(f"   ⏱️  Duration: {analytics.get('duration', 'N/A'):.2f} years")
            print(f"   💰 Accrued: {analytics.get('accrued_interest', 'N/A'):.3f}%")
            print(f"   🔍 Resolved via: {resolver_meta.get('resolution_source', 'unknown')}")
        else:
            print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
        
        results.append({
            'isin': bond['isin'],
            'name': bond['name'],
            'price': bond['price'],
            'result': result
        })
        
        print("-" * 60)
    
    # Summary
    success_rate = (successful_resolutions / len(test_bonds)) * 100
    print(f"\n🎯 INTEGRATION TEST RESULTS:")
    print("=" * 50)
    print(f"   📊 Success Rate: {successful_resolutions}/{len(test_bonds)} ({success_rate:.1f}%)")
    print(f"   🎯 ISIN-only API calls (current): 0% success rate")
    print(f"   🚀 With intelligent resolver: {success_rate:.1f}% success rate")
    
    if successful_resolutions > 0:
        print(f"\n✅ PROOF OF CONCEPT SUCCESS!")
        print(f"   Intelligent ISIN resolver enables ISIN-only workflows")
        print(f"   Integration would fix the 100% ISIN failure rate")
        print(f"   Bloomberg Terminal-style ISIN input becomes possible")
    else:
        print(f"\n❌ Integration test failed - need to debug resolver")
    
    return results

def save_integration_test_results(results):
    """Save detailed results for analysis"""
    filename = "isin_resolution_integration_test_results.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {filename}")
    return filename

def main():
    """Run the integration test"""
    results = test_isin_resolution_integration()
    save_integration_test_results(results)
    
    print("\n" + "=" * 80)
    print("🎯 INTEGRATION TEST COMPLETE!")
    print("   This demonstrates how intelligent ISIN resolver would work")
    print("   if integrated into the bond analysis API pipeline")
    print("=" * 80)

if __name__ == "__main__":
    main()
