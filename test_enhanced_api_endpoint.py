#!/usr/bin/env python3
"""
Test Enhanced API with Fixed Metrics
====================================

Test the API endpoint to verify the enhanced metrics are served correctly
with the accrued interest fix and new metrics (convexity, PVBP).
"""

import requests
import json

def test_enhanced_api():
    """Test the enhanced API endpoint"""
    
    print("🚀 TESTING ENHANCED API ENDPOINT")
    print("=" * 60)
    
    # API endpoint
    url = "https://future-footing-414610.uc.r.appspot.com/api/v1/bond/parse-and-calculate"
    
    # Request payload
    payload = {
        "description": "T 3 15/08/52",
        "price": 71.66
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "gax10_demo_3j5h8m9k2p6r4t7w1q"
    }
    
    print(f"📊 Test Bond: {payload['description']}")
    print(f"💰 Price: {payload['price']}")
    print(f"🌐 URL: {url}")
    print()
    
    try:
        print("🔧 Making API request...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ API REQUEST SUCCESSFUL!")
            print()
            
            # Extract analytics section
            analytics = data.get('bond', {}).get('analytics', {})
            
            if analytics:
                print("📈 ENHANCED METRICS FROM API:")
                
                # Core metrics
                core_metrics = ['yield', 'duration', 'accrued_interest']
                print("Core Metrics:")
                for metric in core_metrics:
                    value = analytics.get(metric)
                    if value is not None:
                        print(f"  ✅ {metric}: {value}")
                    else:
                        print(f"  ❌ {metric}: Missing")
                
                print()
                
                # Enhanced metrics
                enhanced_metrics = [
                    'mac_dur_semi', 'clean_price', 'dirty_price', 
                    'ytm_annual', 'mod_dur_annual', 'mac_dur_annual'
                ]
                print("Enhanced Metrics:")
                for metric in enhanced_metrics:
                    value = analytics.get(metric)
                    if value is not None:
                        print(f"  ✅ {metric}: {value}")
                    else:
                        print(f"  ❌ {metric}: Missing")
                
                print()
                
                # NEW metrics from our fix
                new_metrics = ['convexity_semi', 'pvbp']
                print("New Metrics (From Fix):")
                for metric in new_metrics:
                    value = analytics.get(metric)
                    if value is not None:
                        print(f"  ✅ {metric}: {value}")
                    else:
                        print(f"  ❌ {metric}: Missing")
                
                print()
                print("🧪 CRITICAL TESTS:")
                
                # Test dirty price calculation
                clean = analytics.get('clean_price', 0)
                dirty = analytics.get('dirty_price', 0)
                accrued = analytics.get('accrued_interest', 0)
                
                if clean and dirty:
                    expected_dirty = clean + accrued
                    if abs(dirty - expected_dirty) < 0.01:
                        print(f"  ✅ Dirty Price Formula: {dirty:.6f} = {clean:.6f} + {accrued:.6f}")
                    else:
                        print(f"  ❌ Dirty Price Error: {dirty:.6f} ≠ {expected_dirty:.6f}")
                
                # Test new metrics presence
                convexity = analytics.get('convexity_semi')
                pvbp = analytics.get('pvbp')
                
                if convexity is not None and pvbp is not None:
                    print(f"  ✅ New Metrics Present: Convexity={convexity:.6f}, PVBP={pvbp:.6f}")
                else:
                    print(f"  ❌ New Metrics Missing: Convexity={convexity}, PVBP={pvbp}")
                
                # Count total metrics
                total_metrics = sum(1 for v in analytics.values() if v is not None and isinstance(v, (int, float)))
                print(f"  📊 Total Numeric Metrics: {total_metrics}")
                
                print()
                
                if total_metrics >= 15 and convexity is not None and pvbp is not None:
                    print("🎉 SUCCESS! Enhanced API serving full metrics!")
                    return True
                else:
                    print("⚠️  PARTIAL SUCCESS - Some metrics still missing from API")
                    return False
                
            else:
                print("❌ No analytics found in response")
                print(f"Response structure: {list(data.keys())}")
                return False
        
        else:
            print(f"❌ API Request Failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request Error: {e}")
        return False

if __name__ == "__main__":
    success = test_enhanced_api()
    if success:
        print("\n🚀 Enhanced API is ready for production!")
    else:
        print("\n🔧 API needs deployment or additional fixes.")
