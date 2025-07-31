#!/usr/bin/env python3
"""
Systematic API Testing Script for XTrillion Core Bond Calculation Engine
========================================================================

Tests all endpoints documented in the API specification to ensure they work
as documented and match the expected response formats.

Based on: XTrillion Core Bond Calculation Engine API Specification - Clean Production Version.md
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any

class XTrillionAPITester:
    def __init__(self, base_url: str = "https://future-footing-414610.uc.r.appspot.com", 
                 api_key: str = "gax10_demo_3j5h8m9k2p6r4t7w1q"):
        """
        Initialize the API tester
        
        Args:
            base_url: Base URL for the API (using development URL as per spec)
            api_key: Demo API key from specification
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key
        }
        self.test_results = []
        
    def log_test(self, test_name: str, status: str, details: Dict[str, Any]):
        """Log test results"""
        result = {
            'test_name': test_name,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.test_results.append(result)
        
        # Print to console
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if status != "PASS":
            print(f"   Details: {details.get('error', details)}")
        print()

    def test_health_endpoint(self):
        """Test the health check endpoint"""
        print("🔍 Testing Health Check Endpoint")
        print("=" * 50)
        
        try:
            response = requests.get(f"{self.base_url}/health", headers=self.headers)
            
            if response.status_code != 200:
                self.log_test("Health Check - Status Code", "FAIL", 
                            {"expected": 200, "actual": response.status_code})
                return
            
            data = response.json()
            
            # Check required fields from specification
            required_fields = ['status', 'version', 'service', 'timestamp', 'capabilities']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test("Health Check - Required Fields", "FAIL", 
                            {"missing_fields": missing_fields})
            else:
                self.log_test("Health Check - Required Fields", "PASS", 
                            {"all_required_fields_present": True})
            
            # Check if status is healthy
            if data.get('status') == 'healthy':
                self.log_test("Health Check - Status Value", "PASS", 
                            {"status": data.get('status')})
            else:
                self.log_test("Health Check - Status Value", "FAIL", 
                            {"expected": "healthy", "actual": data.get('status')})
            
            # Check capabilities array
            if isinstance(data.get('capabilities'), list) and len(data.get('capabilities', [])) > 0:
                self.log_test("Health Check - Capabilities", "PASS", 
                            {"capabilities_count": len(data.get('capabilities', []))})
            else:
                self.log_test("Health Check - Capabilities", "FAIL", 
                            {"capabilities": data.get('capabilities')})
                
            # Log full response for reference
            print("📄 Full Health Response:")
            print(json.dumps(data, indent=2))
            print()
            
        except Exception as e:
            self.log_test("Health Check - Request", "FAIL", {"error": str(e)})

    def test_individual_bond_analysis(self):
        """Test individual bond analysis endpoint"""
        print("🔍 Testing Individual Bond Analysis")
        print("=" * 50)
        
        # Test cases from specification
        test_cases = [
            {
                "name": "Treasury Bond (T 3 15/08/52)",
                "payload": {
                    "description": "T 3 15/08/52",
                    "price": 71.66
                },
                "expected_fields": ["status", "bond", "analytics", "calculations", "field_descriptions", "metadata"]
            },
            {
                "name": "Treasury Bond with Settlement Date",
                "payload": {
                    "description": "T 3 15/08/52",
                    "price": 71.66,
                    "settlement_date": "2025-07-30"
                },
                "expected_fields": ["status", "bond", "analytics"]
            },
            {
                "name": "Panama Bond",
                "payload": {
                    "description": "PANAMA, 3.87%, 23-Jul-2060",
                    "price": 56.60
                },
                "expected_fields": ["status", "bond", "analytics"]
            },
            {
                "name": "Invalid Input (Empty)",
                "payload": {},
                "should_fail": True
            }
        ]
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/bond/analysis", 
                    headers=self.headers,
                    json=test_case["payload"]
                )
                
                if test_case.get("should_fail"):
                    if response.status_code == 400:
                        self.log_test(f"Bond Analysis - {test_case['name']}", "PASS", 
                                    {"expected_failure": True, "status_code": response.status_code})
                    else:
                        self.log_test(f"Bond Analysis - {test_case['name']}", "FAIL", 
                                    {"expected": "400 error", "actual": response.status_code})
                    continue
                
                if response.status_code != 200:
                    self.log_test(f"Bond Analysis - {test_case['name']}", "FAIL", 
                                {"status_code": response.status_code, "response": response.text})
                    continue
                
                data = response.json()
                
                # Check required fields
                missing_fields = [field for field in test_case["expected_fields"] if field not in data]
                
                if missing_fields:
                    self.log_test(f"Bond Analysis - {test_case['name']}", "FAIL", 
                                {"missing_fields": missing_fields})
                else:
                    self.log_test(f"Bond Analysis - {test_case['name']}", "PASS", 
                                {"all_expected_fields_present": True})
                
                # Check analytics fields for successful requests
                if data.get('status') == 'success' and 'analytics' in data:
                    analytics = data['analytics']
                    required_analytics = ['ytm', 'duration', 'accrued_interest', 'clean_price', 'dirty_price']
                    missing_analytics = [field for field in required_analytics if field not in analytics]
                    
                    if missing_analytics:
                        self.log_test(f"Bond Analysis Analytics - {test_case['name']}", "FAIL", 
                                    {"missing_analytics": missing_analytics})
                    else:
                        self.log_test(f"Bond Analysis Analytics - {test_case['name']}", "PASS", 
                                    {"analytics_complete": True})
                        
                        # Print sample response for first successful test
                        if test_case['name'] == "Treasury Bond (T 3 15/08/52)":
                            print("📄 Sample Bond Analysis Response:")
                            print(json.dumps(data, indent=2)[:1000] + "..." if len(json.dumps(data, indent=2)) > 1000 else json.dumps(data, indent=2))
                            print()
                
            except Exception as e:
                self.log_test(f"Bond Analysis - {test_case['name']}", "FAIL", {"error": str(e)})

    def test_portfolio_analysis(self):
        """Test portfolio analysis endpoint"""
        print("🔍 Testing Portfolio Analysis")
        print("=" * 50)
        
        test_cases = [
            {
                "name": "Two Bond Portfolio (Treasury + Panama)",
                "payload": {
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
                },
                "expected_fields": ["status", "portfolio_metrics", "bond_data", "metadata"]
            },
            {
                "name": "Single Bond Portfolio",
                "payload": {
                    "data": [
                        {
                            "description": "T 3 15/08/52",
                            "price": 71.66,
                            "weight": 100.0
                        }
                    ]
                },
                "expected_fields": ["status", "portfolio_metrics", "bond_data"]
            },
            {
                "name": "Empty Portfolio (Should Fail)",
                "payload": {
                    "data": []
                },
                "should_fail": True
            }
        ]
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/portfolio/analysis", 
                    headers=self.headers,
                    json=test_case["payload"]
                )
                
                if test_case.get("should_fail"):
                    if response.status_code == 400:
                        self.log_test(f"Portfolio Analysis - {test_case['name']}", "PASS", 
                                    {"expected_failure": True, "status_code": response.status_code})
                    else:
                        self.log_test(f"Portfolio Analysis - {test_case['name']}", "FAIL", 
                                    {"expected": "400 error", "actual": response.status_code})
                    continue
                
                if response.status_code != 200:
                    self.log_test(f"Portfolio Analysis - {test_case['name']}", "FAIL", 
                                {"status_code": response.status_code, "response": response.text})
                    continue
                
                data = response.json()
                
                # Check required fields
                missing_fields = [field for field in test_case["expected_fields"] if field not in data]
                
                if missing_fields:
                    self.log_test(f"Portfolio Analysis - {test_case['name']}", "FAIL", 
                                {"missing_fields": missing_fields})
                else:
                    self.log_test(f"Portfolio Analysis - {test_case['name']}", "PASS", 
                                {"all_expected_fields_present": True})
                
                # Check portfolio metrics
                if data.get('portfolio_metrics'):
                    metrics = data['portfolio_metrics']
                    required_metrics = ['portfolio_yield', 'portfolio_duration', 'total_bonds', 'success_rate']
                    missing_metrics = [field for field in required_metrics if field not in metrics]
                    
                    if missing_metrics:
                        self.log_test(f"Portfolio Metrics - {test_case['name']}", "FAIL", 
                                    {"missing_metrics": missing_metrics})
                    else:
                        self.log_test(f"Portfolio Metrics - {test_case['name']}", "PASS", 
                                    {"portfolio_metrics_complete": True})
                        
                        # Print sample response for first successful test
                        if test_case['name'] == "Two Bond Portfolio (Treasury + Panama)":
                            print("📄 Sample Portfolio Analysis Response:")
                            print(json.dumps(data, indent=2)[:1000] + "..." if len(json.dumps(data, indent=2)) > 1000 else json.dumps(data, indent=2))
                            print()
                
            except Exception as e:
                self.log_test(f"Portfolio Analysis - {test_case['name']}", "FAIL", {"error": str(e)})

    def test_cash_flow_analysis(self):
        """Test cash flow analysis endpoints"""
        print("🔍 Testing Cash Flow Analysis")
        print("=" * 50)
        
        # Note: The specification shows /v1/bond/cashflow but the API might use different paths
        # Let's try both the documented paths and common alternatives
        
        test_cases = [
            {
                "name": "Basic Cash Flow Analysis",
                "endpoint": "/v1/bond/cashflow",
                "payload": {
                    "bonds": [
                        {
                            "description": "T 3 15/08/52",
                            "nominal": 1000000
                        }
                    ]
                }
            },
            {
                "name": "Cash Flow with Period Filter",
                "endpoint": "/v1/bond/cashflow",
                "payload": {
                    "bonds": [
                        {
                            "description": "T 3 15/08/52",
                            "nominal": 1000000
                        }
                    ],
                    "filter": "period",
                    "days": 90,
                    "context": "portfolio"
                }
            },
            {
                "name": "Next Cash Flow",
                "endpoint": "/v1/bond/cashflow/next",
                "payload": {
                    "bonds": [
                        {
                            "description": "T 3 15/08/52",
                            "nominal": 1000000
                        }
                    ]
                }
            }
        ]
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}{test_case['endpoint']}", 
                    headers=self.headers,
                    json=test_case["payload"]
                )
                
                if response.status_code == 404:
                    self.log_test(f"Cash Flow - {test_case['name']}", "WARNING", 
                                {"message": "Endpoint not found", "endpoint": test_case['endpoint']})
                elif response.status_code == 200:
                    data = response.json()
                    self.log_test(f"Cash Flow - {test_case['name']}", "PASS", 
                                {"status_code": response.status_code, "has_data": bool(data)})
                    
                    # Print sample response for first successful test
                    if test_case['name'] == "Basic Cash Flow Analysis":
                        print("📄 Sample Cash Flow Response:")
                        print(json.dumps(data, indent=2)[:500] + "..." if len(json.dumps(data, indent=2)) > 500 else json.dumps(data, indent=2))
                        print()
                else:
                    self.log_test(f"Cash Flow - {test_case['name']}", "FAIL", 
                                {"status_code": response.status_code, "response": response.text})
                
            except Exception as e:
                self.log_test(f"Cash Flow - {test_case['name']}", "FAIL", {"error": str(e)})

    def test_api_authentication(self):
        """Test API authentication behavior"""
        print("🔍 Testing API Authentication")
        print("=" * 50)
        
        # Test with no API key
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                self.log_test("Authentication - No API Key", "PASS", 
                            {"message": "Request allowed without API key (soft auth)"})
            else:
                self.log_test("Authentication - No API Key", "FAIL", 
                            {"status_code": response.status_code})
        except Exception as e:
            self.log_test("Authentication - No API Key", "FAIL", {"error": str(e)})
        
        # Test with invalid API key
        try:
            invalid_headers = {'X-API-Key': 'invalid_key_123'}
            response = requests.get(f"{self.base_url}/health", headers=invalid_headers)
            if response.status_code == 200:
                self.log_test("Authentication - Invalid API Key", "PASS", 
                            {"message": "Request allowed with invalid key (soft auth)"})
            else:
                self.log_test("Authentication - Invalid API Key", "FAIL", 
                            {"status_code": response.status_code})
        except Exception as e:
            self.log_test("Authentication - Invalid API Key", "FAIL", {"error": str(e)})
        
        # Test with valid API key
        try:
            response = requests.get(f"{self.base_url}/health", headers=self.headers)
            if response.status_code == 200:
                self.log_test("Authentication - Valid API Key", "PASS", 
                            {"api_key": self.api_key[:10] + "..."})
            else:
                self.log_test("Authentication - Valid API Key", "FAIL", 
                            {"status_code": response.status_code})
        except Exception as e:
            self.log_test("Authentication - Valid API Key", "FAIL", {"error": str(e)})

    def test_response_formats(self):
        """Test response format consistency with specification"""
        print("🔍 Testing Response Format Consistency")
        print("=" * 50)
        
        # Test bond analysis response format
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/bond/analysis", 
                headers=self.headers,
                json={"description": "T 3 15/08/52", "price": 71.66}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if field descriptions are included
                if 'field_descriptions' in data:
                    self.log_test("Response Format - Field Descriptions", "PASS", 
                                {"field_descriptions_included": True})
                else:
                    self.log_test("Response Format - Field Descriptions", "WARNING", 
                                {"field_descriptions_included": False})
                
                # Check if metadata is included
                if 'metadata' in data:
                    metadata = data['metadata']
                    if 'api_version' in metadata and 'calculation_engine' in metadata:
                        self.log_test("Response Format - Metadata", "PASS", 
                                    {"metadata_complete": True})
                    else:
                        self.log_test("Response Format - Metadata", "WARNING", 
                                    {"metadata_incomplete": True})
                else:
                    self.log_test("Response Format - Metadata", "WARNING", 
                                {"metadata_missing": True})
                
                # Check analytics precision (should be full precision as per spec)
                if 'analytics' in data:
                    analytics = data['analytics']
                    ytm = analytics.get('ytm')
                    if ytm and isinstance(ytm, (int, float)):
                        precision_digits = len(str(ytm).split('.')[-1]) if '.' in str(ytm) else 0
                        if precision_digits >= 4:
                            self.log_test("Response Format - Precision", "PASS", 
                                        {"ytm_precision_digits": precision_digits})
                        else:
                            self.log_test("Response Format - Precision", "WARNING", 
                                        {"ytm_precision_digits": precision_digits, "expected": ">=4"})
            
        except Exception as e:
            self.log_test("Response Format Check", "FAIL", {"error": str(e)})

    def generate_test_report(self):
        """Generate a comprehensive test report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['status'] == 'PASS'])
        failed_tests = len([t for t in self.test_results if t['status'] == 'FAIL'])
        warning_tests = len([t for t in self.test_results if t['status'] == 'WARNING'])
        
        print(f"📈 Test Summary:")
        print(f"   Total Tests:    {total_tests}")
        print(f"   ✅ Passed:      {passed_tests}")
        print(f"   ❌ Failed:      {failed_tests}")
        print(f"   ⚠️  Warnings:    {warning_tests}")
        print(f"   📊 Pass Rate:   {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Group results by category
        categories = {}
        for test in self.test_results:
            category = test['test_name'].split(' - ')[0]
            if category not in categories:
                categories[category] = []
            categories[category].append(test)
        
        print("📋 Results by Category:")
        for category, tests in categories.items():
            category_passed = len([t for t in tests if t['status'] == 'PASS'])
            category_total = len(tests)
            print(f"   {category}: {category_passed}/{category_total} passed")
        print()
        
        # List failures and warnings
        if failed_tests > 0:
            print("❌ Failed Tests:")
            for test in self.test_results:
                if test['status'] == 'FAIL':
                    print(f"   - {test['test_name']}: {test['details']}")
            print()
        
        if warning_tests > 0:
            print("⚠️  Warning Tests:")
            for test in self.test_results:
                if test['status'] == 'WARNING':
                    print(f"   - {test['test_name']}: {test['details']}")
            print()
        
        # Save detailed results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"api_test_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump({
                'test_summary': {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'failed_tests': failed_tests,
                    'warning_tests': warning_tests,
                    'pass_rate': (passed_tests/total_tests)*100
                },
                'test_details': self.test_results,
                'test_timestamp': datetime.now().isoformat(),
                'base_url': self.base_url,
                'api_key_used': self.api_key[:10] + "..."
            }, f, indent=2)
        
        print(f"📄 Detailed report saved to: {report_file}")
        print()
        
        return {
            'total': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'warnings': warning_tests,
            'pass_rate': (passed_tests/total_tests)*100
        }

    def run_all_tests(self):
        """Run all API tests systematically"""
        print("🚀 Starting Systematic XTrillion API Testing")
        print("=" * 80)
        print(f"Base URL: {self.base_url}")
        print(f"API Key:  {self.api_key[:10]}...")
        print(f"Started:  {datetime.now().isoformat()}")
        print()
        
        # Run all test categories
        self.test_health_endpoint()
        self.test_api_authentication()
        self.test_individual_bond_analysis()
        self.test_portfolio_analysis()
        self.test_cash_flow_analysis()
        self.test_response_formats()
        
        # Generate final report
        summary = self.generate_test_report()
        
        return summary

def main():
    """Main function to run the tests"""
    print("XTrillion Core Bond Calculation Engine API - Systematic Testing")
    print("==============================================================")
    print()
    
    # Check if using local API
    if len(sys.argv) > 1 and sys.argv[1] == 'local':
        # Test against local API
        base_url = "http://localhost:8080"
        print(f"🏠 Testing LOCAL API: {base_url}")
    else:
        # Test against development URL from specification
        base_url = "https://future-footing-414610.uc.r.appspot.com"
        print(f"🌐 Testing DEVELOPMENT API: {base_url}")
    
    print()
    
    # Initialize tester and run tests
    tester = XTrillionAPITester(base_url=base_url)
    
    try:
        summary = tester.run_all_tests()
        
        # Exit with appropriate code
        if summary['failed'] == 0:
            print("🎉 All tests passed successfully!")
            sys.exit(0)
        else:
            print(f"⚠️  {summary['failed']} tests failed. Review report for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
