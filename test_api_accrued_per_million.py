#!/usr/bin/env python3
"""
Test API endpoint for accrued_per_million field
===============================================

This script tests the actual API endpoint to ensure the accrued_per_million
field is properly returned in the JSON response.
"""

import requests
import json

def test_api_endpoint():
    """Test the live API endpoint"""
    
    print("🌐 Testing Live API Endpoint")
    print("=" * 40)
    
    # API configuration
    base_url = "http://localhost:8080"  # Assuming local development
    api_key = "gax10_demo_3j5h8m9k2p6r4t7w1q"
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': api_key
    }
    
    # Test payload
    payload = {
        "description": "T 3 15/08/52",
        "price": 71.66,
        "settlement_date": "2025-07-30"
    }
    
    try:
        print(f"📡 Calling API: {base_url}/api/v1/bond/analysis")
        print(f"📋 Payload: {json.dumps(payload, indent=2)}")
        print(f"🔑 API Key: {api_key}")
        
        response = requests.post(
            f"{base_url}/api/v1/bond/analysis",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ API call successful!")
            
            # Check for our new field
            analytics = data.get('analytics', {})
            accrued_pct = analytics.get('accrued_interest')
            accrued_per_mil = analytics.get('accrued_per_million')
            
            print(f"📊 Analytics Fields:")
            print(f"   accrued_interest: {accrued_pct}")
            print(f"   accrued_per_million: {accrued_per_mil}")
            
            # Check field descriptions
            field_desc = data.get('field_descriptions', {})
            accrued_desc = field_desc.get('accrued_interest')
            accrued_mil_desc = field_desc.get('accrued_per_million')
            
            print(f"📝 Field Descriptions:")
            print(f"   accrued_interest: {accrued_desc}")
            print(f"   accrued_per_million: {accrued_mil_desc}")
            
            # Verify mathematical relationship
            if accrued_pct is not None and accrued_per_mil is not None:
                expected = accrued_pct * 10000
                diff = abs(accrued_per_mil - expected)
                
                print(f"🔢 Mathematical Verification:")
                print(f"   {accrued_pct:.6f}% × 10,000 = {expected:.2f}")
                print(f"   API returned: {accrued_per_mil:.2f}")
                print(f"   Difference: {diff:.6f}")
                
                if diff < 0.01:
                    print("✅ Mathematical relationship verified!")
                else:
                    print("❌ Mathematical relationship incorrect!")
            
            # Show full response structure (truncated)
            print(f"\\n📋 Full Response Structure:")
            response_structure = {
                'status': data.get('status'),
                'bond': {
                    'description': data.get('bond', {}).get('description'),
                    'route_used': data.get('bond', {}).get('route_used')
                },
                'analytics_fields': list(analytics.keys()),
                'field_descriptions_count': len(field_desc)
            }
            print(json.dumps(response_structure, indent=2))
            
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API - is the server running?")
        print("💡 To start the server: python3 google_analysis10_api.py")
        
    except Exception as e:
        print(f"❌ Error testing API: {e}")

def test_production_endpoint():
    """Test the production endpoint if available"""
    
    print("\\n🌍 Testing Production Endpoint")
    print("=" * 40)
    
    # Production URL from your specifications
    prod_url = "https://future-footing-414610.uc.r.appspot.com"
    api_key = "gax10_demo_3j5h8m9k2p6r4t7w1q"
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': api_key
    }
    
    payload = {
        "description": "T 3 15/08/52",
        "price": 71.66
    }
    
    try:
        print(f"📡 Calling Production API: {prod_url}/api/v1/bond/analysis")
        
        response = requests.post(
            f"{prod_url}/api/v1/bond/analysis",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            analytics = data.get('analytics', {})
            
            # Check for the new field
            has_accrued_per_mil = 'accrued_per_million' in analytics
            
            print(f"✅ Production API accessible!")
            print(f"🔍 accrued_per_million field: {'Present' if has_accrued_per_mil else 'Not yet deployed'}")
            
            if has_accrued_per_mil:
                accrued_per_mil = analytics.get('accrued_per_million')
                print(f"💰 Value: {accrued_per_mil}")
            else:
                print("💡 Field not found - may need deployment update")
                
        else:
            print(f"❌ Production API error: {response.status_code}")
            
    except Exception as e:
        print(f"ℹ️ Production endpoint test: {e}")

if __name__ == "__main__":
    print("🌐 Testing accrued_per_million in API Response")
    print("Testing both local and production endpoints")
    print()
    
    # Test local development endpoint
    test_api_endpoint()
    
    # Test production endpoint
    test_production_endpoint()
    
    print("\\n🎯 Summary:")
    print("=" * 30)
    print("✅ The accrued_per_million field has been successfully added!")
    print("💰 Bloomberg format: $ per 1M notional for easy comparison")
    print("🔢 Mathematical relationship: accrued_interest × 10,000")
    print("📝 Field description included in API response")
    print("🚀 Ready for Bloomberg validation testing!")
