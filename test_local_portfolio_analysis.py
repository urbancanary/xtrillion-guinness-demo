#!/usr/bin/env python3
"""
Test 25-Bond Portfolio with New /analysis Endpoint - LOCAL VERSION
================================================================

Test the new /api/v1/portfolio/analysis endpoint locally with:
1. ISIN-based lookup
2. Description-based lookup  
3. Mixed ISIN/description portfolio

Compare results and validate portfolio-level calculations.
"""

import requests
import json
from datetime import datetime
import time

# LOCAL API Configuration
BASE_URL = "http://localhost:8080"
API_KEY = "gax10_demo_3j5h8m9k2p6r4t7w1q"

headers = {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
}

# Test Portfolio Data - 25 Bonds with ISIN, Price, Name, Expected Metrics
portfolio_bonds = [
    {"isin": "US912810TJ79", "price": 71.66, "name": "T 3 15/08/52", "exp_duration": 16.36, "exp_yield": 4.90},
    {"isin": "XS2249741674", "price": 77.88, "name": "GALAXY PIPELINE, 3.25%, 30-Sep-2040", "exp_duration": 10.10, "exp_yield": 5.64},
    {"isin": "XS1709535097", "price": 89.40, "name": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047", "exp_duration": 9.82, "exp_yield": 5.72},
    {"isin": "XS1982113463", "price": 87.14, "name": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039", "exp_duration": 9.93, "exp_yield": 5.60},
    {"isin": "USP37466AS18", "price": 80.39, "name": "EMPRESA METRO, 4.7%, 07-May-2050", "exp_duration": 13.19, "exp_yield": 6.27},
    {"isin": "USP3143NAH72", "price": 101.63, "name": "CODELCO INC, 6.15%, 24-Oct-2036", "exp_duration": 8.02, "exp_yield": 5.95},
    {"isin": "USP30179BR86", "price": 86.42, "name": "COMISION FEDERAL, 6.264%, 15-Feb-2052", "exp_duration": 11.58, "exp_yield": 7.44},
    {"isin": "US195325DX04", "price": 52.71, "name": "COLOMBIA REP OF, 3.875%, 15-Feb-2061", "exp_duration": 12.98, "exp_yield": 7.84},
    {"isin": "US279158AJ82", "price": 69.31, "name": "ECOPETROL SA, 5.875%, 28-May-2045", "exp_duration": 9.81, "exp_yield": 9.28},
    {"isin": "USP37110AM89", "price": 76.24, "name": "EMPRESA NACIONAL, 4.5%, 14-Sep-2047", "exp_duration": 12.39, "exp_yield": 6.54},
    {"isin": "XS2542166231", "price": 103.03, "name": "GREENSAIF PIPELI, 6.129%, 23-Feb-2038", "exp_duration": 7.21, "exp_yield": 5.72},
    {"isin": "XS2167193015", "price": 64.50, "name": "STATE OF ISRAEL, 3.8%, 13-May-2060", "exp_duration": 15.27, "exp_yield": 6.34},
    {"isin": "XS1508675508", "price": 82.42, "name": "SAUDI INT BOND, 4.5%, 26-Oct-2046", "exp_duration": 12.60, "exp_yield": 5.97},
    {"isin": "XS1807299331", "price": 92.21, "name": "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048", "exp_duration": 11.45, "exp_yield": 7.06},
    {"isin": "US91086QAZ19", "price": 78.00, "name": "UNITED MEXICAN, 5.75%, 12-Oct-2110", "exp_duration": 13.37, "exp_yield": 7.37},
    {"isin": "USP6629MAD40", "price": 82.57, "name": "MEXICO CITY ARPT, 5.5%, 31-Jul-2047", "exp_duration": 11.38, "exp_yield": 7.07},
    {"isin": "US698299BL70", "price": 56.60, "name": "PANAMA, 3.87%, 23-Jul-2060", "exp_duration": 13.49, "exp_yield": 7.36},
    {"isin": "US71654QDF63", "price": 71.42, "name": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060", "exp_duration": 9.72, "exp_yield": 9.88},
    {"isin": "US71654QDE98", "price": 89.55, "name": "PETROLEOS MEXICA, 5.95%, 28-Jan-2031", "exp_duration": 4.47, "exp_yield": 8.32},
    {"isin": "XS2585988145", "price": 85.54, "name": "GACI FIRST INVST, 5.125%, 14-Feb-2053", "exp_duration": 13.33, "exp_yield": 6.23},
    {"isin": "XS1959337749", "price": 89.97, "name": "QATAR STATE OF, 4.817%, 14-Mar-2049", "exp_duration": 13.26, "exp_yield": 5.58},
    {"isin": "XS2233188353", "price": 99.23, "name": "QNB FINANCE LTD, 1.625%, 22-Sep-2025", "exp_duration": 0.23, "exp_yield": 5.02},
    {"isin": "XS2359548935", "price": 73.79, "name": "QATAR ENERGY, 3.125%, 12-Jul-2041", "exp_duration": 11.51, "exp_yield": 5.63},
    {"isin": "XS0911024635", "price": 93.29, "name": "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043", "exp_duration": 11.24, "exp_yield": 5.66},
    {"isin": "USP0R80BAG79", "price": 97.26, "name": "SITIOS, 5.375%, 04-Apr-2032", "exp_duration": 5.51, "exp_yield": 5.87}
]

def test_api_health():
    """Test if the local API is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", headers=headers, timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ API Health: {health_data['status']}")
            print(f"📊 Universal Parser: {health_data['universal_parser']['status']}")
            return True
        else:
            print(f"❌ API Health Check Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Connection Failed: {e}")
        return False

def create_isin_portfolio():
    """Create portfolio using ISIN codes"""
    portfolio = {
        "data": []
    }
    
    for i, bond in enumerate(portfolio_bonds):
        portfolio["data"].append({
            "BOND_CD": bond["isin"],
            "CLOSING PRICE": bond["price"],
            "WEIGHTING": 4.0  # Equal weight: 100% / 25 bonds = 4%
        })
    
    return portfolio

def create_description_portfolio():
    """Create portfolio using bond descriptions"""
    portfolio = {
        "data": []
    }
    
    for i, bond in enumerate(portfolio_bonds):
        portfolio["data"].append({
            "BOND_CD": bond["name"],
            "CLOSING PRICE": bond["price"],
            "WEIGHTING": 4.0  # Equal weight: 100% / 25 bonds = 4%
        })
    
    return portfolio

def create_mixed_portfolio():
    """Create portfolio mixing ISIN codes and descriptions"""
    portfolio = {
        "data": []
    }
    
    for i, bond in enumerate(portfolio_bonds):
        # Alternate between ISIN and description
        if i % 2 == 0:
            bond_id = bond["isin"]
            id_type = "ISIN"
        else:
            bond_id = bond["name"]
            id_type = "Description"
            
        portfolio["data"].append({
            "BOND_CD": bond_id,
            "CLOSING PRICE": bond["price"],
            "WEIGHTING": 4.0,
            "_test_info": f"{id_type}: {bond_id[:30]}..."
        })
    
    return portfolio

def test_portfolio_analysis(portfolio_data, test_name):
    """Test portfolio analysis endpoint"""
    print(f"\n🚀 Testing {test_name}")
    print("=" * 60)
    
    try:
        # Test NEW endpoint
        response = requests.post(
            f"{BASE_URL}/api/v1/portfolio/analysis",
            headers=headers,
            json=portfolio_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ NEW /analysis endpoint successful")
            
            # Analyze results
            bond_data = result.get('bond_data', [])
            portfolio_metrics = result.get('portfolio_metrics', {})
            
            successful_bonds = [b for b in bond_data if b.get('status') == 'success']
            failed_bonds = [b for b in bond_data if b.get('status') != 'success']
            
            print(f"📊 Portfolio Results:")
            print(f"   Total Bonds: {len(bond_data)}")
            print(f"   Successful: {len(successful_bonds)}")
            print(f"   Failed: {len(failed_bonds)}")
            
            if portfolio_metrics:
                print(f"📈 Portfolio Metrics:")
                print(f"   Portfolio Yield: {portfolio_metrics.get('portfolio_yield', 'N/A')}")
                print(f"   Portfolio Duration: {portfolio_metrics.get('portfolio_duration', 'N/A')}")
                print(f"   Portfolio Spread: {portfolio_metrics.get('portfolio_spread', 'N/A')}")
                print(f"   Success Rate: {portfolio_metrics.get('success_rate', 'N/A')}")
            
            # Show first few successful bonds
            print(f"\n📋 Sample Successful Bonds:")
            for i, bond in enumerate(successful_bonds[:5]):
                print(f"   {i+1}. {bond.get('name', 'Unknown')[:40]}...")
                print(f"      Yield: {bond.get('yield', 'N/A')}, Duration: {bond.get('duration', 'N/A')}")
            
            # Show failed bonds if any
            if failed_bonds:
                print(f"\n❌ Failed Bonds:")
                for i, bond in enumerate(failed_bonds[:3]):
                    print(f"   {i+1}. {bond.get('name', 'Unknown')[:40]}...")
                    print(f"      Status: {bond.get('status', 'Unknown error')}")
            
            return result
            
        else:
            print(f"❌ NEW /analysis endpoint failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text[:200]}...")
            return None
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return None

def test_backward_compatibility(portfolio_data, test_name):
    """Test that old /analyze endpoint still works"""
    print(f"\n🔄 Testing Backward Compatibility for {test_name}")
    print("=" * 60)
    
    try:
        # Test OLD endpoint (should still work with deprecation warning)
        response = requests.post(
            f"{BASE_URL}/api/v1/portfolio/analyze",
            headers=headers,
            json=portfolio_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ OLD /analyze endpoint still works (backward compatibility)")
            return result
        else:
            print(f"❌ OLD /analyze endpoint failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
        return None

def compare_results(result1, result2, test1_name, test2_name):
    """Compare two portfolio analysis results"""
    print(f"\n🔍 Comparing {test1_name} vs {test2_name}")
    print("=" * 60)
    
    if not result1 or not result2:
        print("❌ Cannot compare - one or both results missing")
        return
    
    # Compare portfolio metrics
    metrics1 = result1.get('portfolio_metrics', {})
    metrics2 = result2.get('portfolio_metrics', {})
    
    if metrics1 and metrics2:
        print(f"📈 Portfolio Metrics Comparison:")
        
        # Extract numeric values for comparison
        yield1 = float(metrics1.get('portfolio_yield', '0%').replace('%', ''))
        yield2 = float(metrics2.get('portfolio_yield', '0%').replace('%', ''))
        
        duration1 = float(metrics1.get('portfolio_duration', '0 years').replace(' years', ''))
        duration2 = float(metrics2.get('portfolio_duration', '0 years').replace(' years', ''))
        
        print(f"   Portfolio Yield: {yield1:.2f}% vs {yield2:.2f}% (diff: {abs(yield1-yield2):.3f}%)")
        print(f"   Portfolio Duration: {duration1:.2f} vs {duration2:.2f} (diff: {abs(duration1-duration2):.3f})")
        
        # Compare success rates
        success1 = len([b for b in result1.get('bond_data', []) if b.get('status') == 'success'])
        success2 = len([b for b in result2.get('bond_data', []) if b.get('status') == 'success'])
        
        print(f"   Successful Bonds: {success1}/25 vs {success2}/25")
        
        if success1 == success2:
            print("✅ Both methods have same success rate")
        else:
            print(f"⚠️  Different success rates - investigate failed bonds")

def main():
    """Run comprehensive portfolio analysis tests"""
    print("🚀 Google Analysis 10 - Portfolio Analysis Test Suite")
    print("=" * 80)
    print("Testing new /api/v1/portfolio/analysis endpoint with 25-bond portfolio")
    print(f"Local API: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check API health first
    if not test_api_health():
        print("\n❌ Local API is not running. Please start it with:")
        print("   cd /Users/andyseaman/Notebooks/json_receiver_project/google_analysis10")
        print("   python3 google_analysis10_api.py")
        return
    
    # Create test portfolios
    isin_portfolio = create_isin_portfolio()
    description_portfolio = create_description_portfolio()
    mixed_portfolio = create_mixed_portfolio()
    
    print(f"\n📋 Created test portfolios:")
    print(f"   ISIN Portfolio: {len(isin_portfolio['data'])} bonds")
    print(f"   Description Portfolio: {len(description_portfolio['data'])} bonds")
    print(f"   Mixed Portfolio: {len(mixed_portfolio['data'])} bonds")
    
    # Test 1: ISIN-based portfolio
    isin_result = test_portfolio_analysis(isin_portfolio, "ISIN-Based Portfolio")
    
    # Test 2: Description-based portfolio  
    description_result = test_portfolio_analysis(description_portfolio, "Description-Based Portfolio")
    
    # Test 3: Mixed portfolio
    mixed_result = test_portfolio_analysis(mixed_portfolio, "Mixed ISIN/Description Portfolio")
    
    # Test 4: Backward compatibility
    backward_result = test_backward_compatibility(isin_portfolio, "ISIN Portfolio (Old Endpoint)")
    
    # Compare results
    if isin_result and description_result:
        compare_results(isin_result, description_result, "ISIN-Based", "Description-Based")
    
    if isin_result and backward_result:
        compare_results(isin_result, backward_result, "NEW /analysis", "OLD /analyze")
    
    print(f"\n🎯 Test Summary:")
    print("=" * 40)
    print(f"✅ ISIN Portfolio: {'PASS' if isin_result else 'FAIL'}")
    print(f"✅ Description Portfolio: {'PASS' if description_result else 'FAIL'}")  
    print(f"✅ Mixed Portfolio: {'PASS' if mixed_result else 'FAIL'}")
    print(f"✅ Backward Compatibility: {'PASS' if backward_result else 'FAIL'}")
    
    # Save detailed results
    test_results = {
        'timestamp': datetime.now().isoformat(),
        'api_base_url': BASE_URL,
        'total_bonds_tested': 25,
        'results': {
            'isin_portfolio': isin_result,
            'description_portfolio': description_result,
            'mixed_portfolio': mixed_result,
            'backward_compatibility': backward_result
        }
    }
    
    results_file = f"portfolio_analysis_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {results_file}")

if __name__ == "__main__":
    main()
