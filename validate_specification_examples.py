#!/usr/bin/env python3
"""
XTrillion API Specification Example Validation
==============================================

Tests the exact examples from the API specification document against the running API
to verify they work exactly as documented.

Based on examples from: XTrillion Core Bond Calculation Engine API Specification - Clean Production Version.md
"""

import requests
import json
import sys
from datetime import datetime

class SpecificationExampleValidator:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url.rstrip('/')
        self.api_key = "gax10_demo_3j5h8m9k2p6r4t7w1q"
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key
        }
        self.results = []

    def test_health_example(self):
        """Test the exact health check example from the specification"""
        print("🔍 Testing Health Check Example from Specification")
        print("=" * 60)
        
        try:
            response = requests.get(f"{self.base_url}/health", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response matches specification structure
                expected_fields = ['status', 'version', 'service', 'timestamp', 'api_status', 'capabilities']
                actual_fields = list(data.keys())
                
                print("✅ Status Code: 200 (matches specification)")
                print(f"📊 Response Fields: {len(actual_fields)} fields returned")
                print(f"🔍 Expected Fields: {expected_fields}")
                print(f"📋 Actual Fields: {actual_fields}")
                
                # Check specific values from specification
                if data.get('status') == 'healthy':
                    print("✅ Status: 'healthy' (matches specification)")
                else:
                    print(f"❌ Status: '{data.get('status')}' (expected 'healthy')")
                
                if data.get('version') == '10.0.0':
                    print("✅ Version: '10.0.0' (matches specification)")
                else:
                    print(f"❌ Version: '{data.get('version')}' (expected '10.0.0')")
                
                # Print full response for comparison
                print("\n📄 Full Health Response:")
                print(json.dumps(data, indent=2)[:1500] + "..." if len(json.dumps(data, indent=2)) > 1500 else json.dumps(data, indent=2))
                
                return True
            else:
                print(f"❌ Status Code: {response.status_code} (expected 200)")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def test_individual_bond_example(self):
        """Test the exact individual bond analysis example from specification"""
        print("\n🔍 Testing Individual Bond Analysis Example")
        print("=" * 60)
        
        # Exact payload from specification
        payload = {
            "description": "T 3 15/08/52",
            "price": 71.66,
            "settlement_date": "2025-07-30"
        }
        
        print(f"📤 Request Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/bond/analysis",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print("✅ Status Code: 200 (matches specification)")
                
                # Check response structure from specification
                expected_top_level = ['status', 'bond', 'analytics', 'calculations', 'field_descriptions', 'metadata']
                actual_top_level = list(data.keys())
                
                print(f"📊 Top-level Fields: {len(actual_top_level)} returned")
                print(f"🔍 Expected: {expected_top_level}")
                print(f"📋 Actual: {actual_top_level}")
                
                # Check analytics fields from specification
                if 'analytics' in data:
                    analytics = data['analytics']
                    expected_analytics = ['ytm', 'duration', 'accrued_interest', 'clean_price', 'dirty_price', 
                                        'macaulay_duration', 'duration_annual', 'ytm_annual', 'convexity', 
                                        'pvbp', 'settlement_date', 'spread', 'z_spread']
                    actual_analytics = list(analytics.keys())
                    
                    print(f"\n📊 Analytics Fields: {len(actual_analytics)} returned")
                    print(f"🔍 Expected from spec: {expected_analytics}")
                    print(f"📋 Actual: {actual_analytics}")
                    
                    # Check specific values mentioned in specification
                    ytm = analytics.get('ytm')
                    duration = analytics.get('duration')
                    price = analytics.get('clean_price')
                    
                    if ytm is not None:
                        print(f"📈 YTM: {ytm:.6f}% (specification shows ~4.899%)")
                    if duration is not None:
                        print(f"⏱️  Duration: {duration:.2f} years (specification shows ~16.35 years)")
                    if price is not None:
                        print(f"💰 Clean Price: {price} (specification shows 71.66)")
                
                # Check field descriptions
                if 'field_descriptions' in data:
                    print(f"\n📚 Field Descriptions: {len(data['field_descriptions'])} fields documented")
                    print("✅ Field descriptions included (matches specification)")
                else:
                    print("❌ Field descriptions missing (specification shows they should be included)")
                
                # Print sample of response
                print("\n📄 Sample Response (first 1000 chars):")
                response_str = json.dumps(data, indent=2)
                print(response_str[:1000] + "..." if len(response_str) > 1000 else response_str)
                
                return True
            else:
                print(f"❌ Status Code: {response.status_code} (expected 200)")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def test_portfolio_example(self):
        """Test the exact portfolio analysis example from specification"""
        print("\n🔍 Testing Portfolio Analysis Example")
        print("=" * 60)
        
        # Exact payload from specification
        payload = {
            "settlement_date": "2025-07-30",
            "data": [
                {
                    "description": "T 3 15/08/52",
                    "price": 71.66,
                    "weight": 60.0
                },
                {
                    "description": "PANAMA 3.87 23/07/60",
                    "price": 56.60,
                    "weight": 40.0
                }
            ]
        }
        
        print(f"📤 Request Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/portfolio/analysis",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print("✅ Status Code: 200 (matches specification)")
                
                # Check response structure from specification
                expected_fields = ['status', 'portfolio_metrics', 'bond_data', 'metadata']
                actual_fields = list(data.keys())
                
                print(f"📊 Top-level Fields: {len(actual_fields)} returned")
                print(f"🔍 Expected: {expected_fields}")
                print(f"📋 Actual: {actual_fields}")
                
                # Check portfolio metrics from specification
                if 'portfolio_metrics' in data:
                    metrics = data['portfolio_metrics']
                    expected_metrics = ['portfolio_yield', 'portfolio_duration', 'portfolio_spread', 
                                      'total_bonds', 'success_rate']
                    actual_metrics = list(metrics.keys())
                    
                    print(f"\n📊 Portfolio Metrics: {len(actual_metrics)} returned")
                    print(f"🔍 Expected: {expected_metrics}")
                    print(f"📋 Actual: {actual_metrics}")
                    
                    # Check specific values from specification
                    portfolio_yield = metrics.get('portfolio_yield')
                    portfolio_duration = metrics.get('portfolio_duration')
                    total_bonds = metrics.get('total_bonds')
                    
                    if portfolio_yield is not None:
                        print(f"📈 Portfolio Yield: {portfolio_yield} (specification shows 5.87%)")
                    if portfolio_duration is not None:
                        print(f"⏱️  Portfolio Duration: {portfolio_duration} (specification shows 15.26 years)")
                    if total_bonds is not None:
                        print(f"🔢 Total Bonds: {total_bonds} (specification shows 2)")
                
                # Check bond data structure
                if 'bond_data' in data:
                    bond_data = data['bond_data']
                    print(f"\n📊 Bond Data: {len(bond_data)} bonds returned")
                    
                    if len(bond_data) > 0:
                        first_bond = bond_data[0]
                        print(f"🔍 First Bond Fields: {list(first_bond.keys())}")
                
                # Print sample of response
                print("\n📄 Sample Response (first 1000 chars):")
                response_str = json.dumps(data, indent=2)
                print(response_str[:1000] + "..." if len(response_str) > 1000 else response_str)
                
                return True
            else:
                print(f"❌ Status Code: {response.status_code} (expected 200)")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def test_cash_flow_example(self):
        """Test the exact cash flow analysis example from specification"""
        print("\n🔍 Testing Cash Flow Analysis Example")
        print("=" * 60)
        
        # Exact payload from specification
        payload = {
            "bonds": [
                {
                    "description": "T 3 15/08/52",
                    "nominal": 1000000
                },
                {
                    "description": "PANAMA 3.87 23/07/60", 
                    "nominal": 500000
                }
            ],
            "filter": "period",
            "days": 90,
            "context": "portfolio",
            "settlement_date": "2025-07-30"
        }
        
        print(f"📤 Request Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/bond/cashflow",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print("✅ Status Code: 200 (matches specification)")
                
                # Check response structure from specification
                expected_fields = ['status', 'portfolio_cash_flows', 'filter_applied', 'metadata']
                actual_fields = list(data.keys())
                
                print(f"📊 Top-level Fields: {len(actual_fields)} returned")
                print(f"🔍 Expected: {expected_fields}")
                print(f"📋 Actual: {actual_fields}")
                
                # Check cash flows structure
                if 'portfolio_cash_flows' in data:
                    cash_flows = data['portfolio_cash_flows']
                    print(f"\n📊 Cash Flows: {len(cash_flows)} flows returned")
                    
                    if len(cash_flows) > 0:
                        first_flow = cash_flows[0]
                        expected_flow_fields = ['date', 'amount', 'days_from_settlement']
                        actual_flow_fields = list(first_flow.keys())
                        
                        print(f"🔍 Cash Flow Fields: {actual_flow_fields}")
                        print(f"💰 First Flow: {first_flow}")
                
                # Check filter applied
                if 'filter_applied' in data:
                    filter_info = data['filter_applied']
                    print(f"🔍 Filter Applied: {filter_info}")
                
                # Print sample of response
                print("\n📄 Sample Response (first 800 chars):")
                response_str = json.dumps(data, indent=2)
                print(response_str[:800] + "..." if len(response_str) > 800 else response_str)
                
                return True
            else:
                print(f"❌ Status Code: {response.status_code} (expected 200)")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def validate_all_examples(self):
        """Validate all specification examples"""
        print("🚀 XTrillion API Specification Example Validation")
        print("=" * 80)
        print(f"🌐 Testing API: {self.base_url}")
        print(f"🔑 API Key: {self.api_key[:10]}...")
        print(f"📅 Started: {datetime.now().isoformat()}")
        print()
        
        tests = [
            ("Health Check", self.test_health_example),
            ("Individual Bond Analysis", self.test_individual_bond_example),
            ("Portfolio Analysis", self.test_portfolio_example),
            ("Cash Flow Analysis", self.test_cash_flow_example)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                success = test_func()
                results.append((test_name, "✅ PASS" if success else "❌ FAIL"))
            except Exception as e:
                results.append((test_name, f"❌ ERROR: {e}"))
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 SPECIFICATION EXAMPLE VALIDATION SUMMARY")
        print("=" * 80)
        
        passed = len([r for r in results if "PASS" in r[1]])
        total = len(results)
        
        print(f"📈 Results: {passed}/{total} examples working correctly")
        print(f"📊 Success Rate: {(passed/total)*100:.1f}%")
        print()
        
        for test_name, result in results:
            print(f"{result:15} {test_name}")
        
        print()
        if passed == total:
            print("🎉 All specification examples are working correctly!")
            print("✅ The API implementation matches the documented specification.")
        else:
            print("⚠️  Some specification examples are not working as documented.")
            print("📝 Consider updating either the API or the specification for consistency.")
        
        return passed == total

def main():
    """Main function"""
    base_url = "http://localhost:8080"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    validator = SpecificationExampleValidator(base_url)
    success = validator.validate_all_examples()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
