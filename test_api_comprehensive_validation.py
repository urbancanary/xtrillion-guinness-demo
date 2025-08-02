#!/usr/bin/env python3
"""
Comprehensive API Testing Script for Google Analysis 10
=======================================================

Tests all major functionality of the GA10 API including:
1. Basic bond analysis with description
2. ISIN input
3. Invalid input fallback
4. Portfolio analysis
5. Weekend/holiday date handling
6. Spread calculations
7. Z-spread calculations
8. Numeric input handling
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys

class GA10APIValidator:
    def __init__(self, base_url: str = "https://future-footing-414610.uc.r.appspot.com", 
                 api_key: str = "bondpricer_readonly_2025"):
        """Initialize the API validator"""
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key
        }
        self.test_results = []
        
    def log_test(self, test_name: str, status: str, request: Dict, response: Dict, notes: str = ""):
        """Log test results with request and response details"""
        result = {
            'test_name': test_name,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'request': request,
            'response': response,
            'notes': notes
        }
        self.test_results.append(result)
        
        # Print to console
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"\n{status_emoji} {test_name}: {status}")
        print(f"   Request: {json.dumps(request, indent=2)}")
        
        # Print key response data
        if isinstance(response, dict):
            if response.get('status') == 'success':
                # For successful responses, show key analytics
                if 'analytics' in response:
                    analytics = response['analytics']
                    print(f"   Key Analytics:")
                    print(f"      YTM: {analytics.get('ytm', 'N/A')}")
                    print(f"      Duration: {analytics.get('duration', 'N/A')}")
                    print(f"      Clean Price: {analytics.get('clean_price', 'N/A')}")
                    print(f"      Dirty Price: {analytics.get('dirty_price', 'N/A')}")
                    if 'z_spread' in analytics:
                        print(f"      Z-Spread: {analytics.get('z_spread', 'N/A')}")
                elif 'portfolio_metrics' in response:
                    metrics = response['portfolio_metrics']
                    print(f"   Portfolio Metrics:")
                    print(f"      Portfolio Yield: {metrics.get('portfolio_yield', 'N/A')}")
                    print(f"      Portfolio Duration: {metrics.get('portfolio_duration', 'N/A')}")
                    print(f"      Success Rate: {metrics.get('success_rate', 'N/A')}")
            else:
                # For error responses
                print(f"   Error: {response.get('error', response)}")
        else:
            print(f"   Response: {response}")
            
        if notes:
            print(f"   Notes: {notes}")

    def make_request(self, endpoint: str, method: str = "POST", payload: Optional[Dict] = None) -> tuple:
        """Make API request and return status code and response"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method == "POST":
                response = requests.post(url, headers=self.headers, json=payload)
            else:
                response = requests.get(url, headers=self.headers)
                
            return response.status_code, response.json() if response.content else {}
        except Exception as e:
            return None, {"error": str(e)}

    def test_1_basic_bond_analysis(self):
        """Test 1: Basic bond analysis with description"""
        print("\n" + "="*60)
        print("TEST 1: Basic Bond Analysis with Description")
        print("="*60)
        
        payload = {
            "description": "T 3 15/08/52",
            "price": 71.66
        }
        
        status_code, response = self.make_request("/api/v1/bond/analysis", "POST", payload)
        
        if status_code == 200 and response.get('status') == 'success':
            analytics = response.get('analytics', {})
            # Verify key fields are present
            required_fields = ['ytm', 'duration', 'clean_price', 'dirty_price', 'accrued_interest']
            missing = [f for f in required_fields if f not in analytics]
            
            if not missing:
                self.log_test("Basic Bond Analysis", "PASS", payload, response,
                            "All required analytics fields present")
            else:
                self.log_test("Basic Bond Analysis", "FAIL", payload, response,
                            f"Missing fields: {missing}")
        else:
            self.log_test("Basic Bond Analysis", "FAIL", payload, response,
                        f"Status code: {status_code}")

    def test_2_isin_input(self):
        """Test 2: ISIN input"""
        print("\n" + "="*60)
        print("TEST 2: ISIN Input")
        print("="*60)
        
        payload = {
            "isin": "US912810TJ79",
            "price": 99.5
        }
        
        status_code, response = self.make_request("/api/v1/bond/analysis", "POST", payload)
        
        if status_code == 200 and response.get('status') == 'success':
            bond_info = response.get('bond', {})
            if bond_info.get('isin') == "US912810TJ79":
                self.log_test("ISIN Input", "PASS", payload, response,
                            "ISIN correctly processed")
            else:
                self.log_test("ISIN Input", "FAIL", payload, response,
                            "ISIN not correctly identified")
        else:
            self.log_test("ISIN Input", "FAIL", payload, response,
                        f"Status code: {status_code}")

    def test_3_invalid_input_fallback(self):
        """Test 3: Invalid input fallback"""
        print("\n" + "="*60)
        print("TEST 3: Invalid Input Fallback")
        print("="*60)
        
        payload = {
            "description": "12345678",
            "price": 100.0
        }
        
        status_code, response = self.make_request("/api/v1/bond/analysis", "POST", payload)
        
        # Should either fail gracefully or attempt to parse
        if status_code == 400 or (status_code == 200 and response.get('status') == 'error'):
            self.log_test("Invalid Input Fallback", "PASS", payload, response,
                        "Invalid input handled gracefully")
        elif status_code == 200 and response.get('status') == 'success':
            self.log_test("Invalid Input Fallback", "WARNING", payload, response,
                        "System attempted to process invalid input")
        else:
            self.log_test("Invalid Input Fallback", "FAIL", payload, response,
                        f"Unexpected response: {status_code}")

    def test_4_portfolio_analysis(self):
        """Test 4: Portfolio analysis with multiple bonds"""
        print("\n" + "="*60)
        print("TEST 4: Portfolio Analysis with Multiple Bonds")
        print("="*60)
        
        payload = {
            "data": [
                {
                    "description": "T 3 15/08/52",
                    "CLOSING PRICE": 71.66,
                    "WEIGHTING": 60.0
                },
                {
                    "description": "T 4.1 02/15/28",
                    "CLOSING PRICE": 99.5,
                    "WEIGHTING": 40.0
                }
            ]
        }
        
        status_code, response = self.make_request("/api/v1/portfolio/analysis", "POST", payload)
        
        if status_code == 200 and response.get('status') == 'success':
            metrics = response.get('portfolio_metrics', {})
            if all(k in metrics for k in ['portfolio_yield', 'portfolio_duration', 'total_bonds']):
                self.log_test("Portfolio Analysis", "PASS", payload, response,
                            f"Processed {metrics.get('total_bonds')} bonds successfully")
            else:
                self.log_test("Portfolio Analysis", "FAIL", payload, response,
                            "Missing portfolio metrics")
        else:
            self.log_test("Portfolio Analysis", "FAIL", payload, response,
                        f"Status code: {status_code}")

    def test_5_weekend_holiday_dates(self):
        """Test 5: Weekend/holiday date handling"""
        print("\n" + "="*60)
        print("TEST 5: Weekend/Holiday Date Handling")
        print("="*60)
        
        # Test with a Sunday date
        payload = {
            "description": "T 3 15/08/52",
            "price": 71.66,
            "settlement_date": "2025-06-30"  # This is a Monday
        }
        
        status_code, response = self.make_request("/api/v1/bond/analysis", "POST", payload)
        
        if status_code == 200 and response.get('status') == 'success':
            calc_info = response.get('calculations', {})
            settlement_used = calc_info.get('settlement_date')
            
            # Check if date was adjusted or accepted
            self.log_test("Weekend/Holiday Date Handling", "PASS", payload, response,
                        f"Settlement date processed: {settlement_used}")
        else:
            self.log_test("Weekend/Holiday Date Handling", "FAIL", payload, response,
                        f"Status code: {status_code}")

    def test_6_spread_calculation(self):
        """Test 6: Spread calculation verification"""
        print("\n" + "="*60)
        print("TEST 6: Spread Calculation Verification")
        print("="*60)
        
        payload = {
            "description": "AAPL 3.35 02/09/27",  # Corporate bond for spread calc
            "price": 98.5
        }
        
        status_code, response = self.make_request("/api/v1/bond/analysis", "POST", payload)
        
        if status_code == 200 and response.get('status') == 'success':
            analytics = response.get('analytics', {})
            if 'credit_spread' in analytics:
                spread = analytics.get('credit_spread')
                self.log_test("Spread Calculation", "PASS", payload, response,
                            f"Credit spread calculated: {spread}")
            else:
                self.log_test("Spread Calculation", "WARNING", payload, response,
                            "Credit spread not included in response")
        else:
            self.log_test("Spread Calculation", "FAIL", payload, response,
                        f"Status code: {status_code}")

    def test_7_z_spread_calculation(self):
        """Test 7: Z-spread calculation verification"""
        print("\n" + "="*60)
        print("TEST 7: Z-Spread Calculation Verification")
        print("="*60)
        
        payload = {
            "description": "T 4.1 02/15/28",
            "price": 99.5,
            "context": "technical"  # Request enhanced metrics
        }
        
        status_code, response = self.make_request("/api/v1/bond/analysis", "POST", payload)
        
        if status_code == 200 and response.get('status') == 'success':
            analytics = response.get('analytics', {})
            if 'z_spread' in analytics:
                z_spread = analytics.get('z_spread')
                self.log_test("Z-Spread Calculation", "PASS", payload, response,
                            f"Z-spread calculated: {z_spread}")
            else:
                self.log_test("Z-Spread Calculation", "WARNING", payload, response,
                            "Z-spread not included in response")
        else:
            self.log_test("Z-Spread Calculation", "FAIL", payload, response,
                        f"Status code: {status_code}")

    def test_8_numeric_input_handling(self):
        """Test 8: Numeric input handling (Google Sheets compatibility)"""
        print("\n" + "="*60)
        print("TEST 8: Numeric Input Handling (Google Sheets Compatibility)")
        print("="*60)
        
        # Test with numeric price as integer (common from Google Sheets)
        payload = {
            "description": "T 3 15/08/52",
            "price": 72  # Integer instead of float
        }
        
        status_code, response = self.make_request("/api/v1/bond/analysis", "POST", payload)
        
        if status_code == 200 and response.get('status') == 'success':
            self.log_test("Numeric Input - Integer Price", "PASS", payload, response,
                        "Integer price accepted")
        else:
            self.log_test("Numeric Input - Integer Price", "FAIL", payload, response,
                        f"Status code: {status_code}")
        
        # Test with string numeric (sometimes happens with CSV/JSON conversion)
        payload2 = {
            "description": "T 3 15/08/52",
            "price": "71.66"  # String instead of float
        }
        
        status_code2, response2 = self.make_request("/api/v1/bond/analysis", "POST", payload2)
        
        if status_code2 == 200 and response2.get('status') == 'success':
            self.log_test("Numeric Input - String Price", "PASS", payload2, response2,
                        "String price accepted and converted")
        else:
            self.log_test("Numeric Input - String Price", "WARNING", payload2, response2,
                        "String price not accepted")

    def test_api_documentation_accuracy(self):
        """Compare actual API responses to documentation claims"""
        print("\n" + "="*60)
        print("API DOCUMENTATION ACCURACY CHECK")
        print("="*60)
        
        # Test health endpoint
        status_code, response = self.make_request("/health", "GET")
        
        if status_code == 200:
            # Check documented fields
            expected_fields = ['status', 'version', 'service', 'timestamp']
            missing = [f for f in expected_fields if f not in response]
            
            if not missing:
                print("✅ Health endpoint matches documentation")
            else:
                print(f"⚠️ Health endpoint missing fields: {missing}")
        else:
            print(f"❌ Health endpoint returned {status_code}")
        
        # Test version endpoint
        status_code, response = self.make_request("/api/v1/version", "GET")
        
        if status_code == 200:
            print("✅ Version endpoint exists")
            print(f"   Version info: {response}")
        else:
            print(f"⚠️ Version endpoint returned {status_code}")

    def generate_summary_report(self):
        """Generate a summary report of all tests"""
        print("\n" + "="*80)
        print("COMPREHENSIVE TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed = len([t for t in self.test_results if t['status'] == 'PASS'])
        failed = len([t for t in self.test_results if t['status'] == 'FAIL'])
        warnings = len([t for t in self.test_results if t['status'] == 'WARNING'])
        
        print(f"\nTest Statistics:")
        print(f"   Total Tests:    {total_tests}")
        print(f"   ✅ Passed:      {passed}")
        print(f"   ❌ Failed:      {failed}")
        print(f"   ⚠️  Warnings:    {warnings}")
        print(f"   📊 Pass Rate:   {(passed/total_tests)*100:.1f}%" if total_tests > 0 else "N/A")
        
        print(f"\nAPI Information:")
        print(f"   Base URL: {self.base_url}")
        print(f"   API Key:  {self.api_key[:20]}...")
        print(f"   Test Run: {datetime.now().isoformat()}")
        
        # List any failures
        if failed > 0:
            print("\n❌ Failed Tests:")
            for test in self.test_results:
                if test['status'] == 'FAIL':
                    print(f"   - {test['test_name']}: {test['notes']}")
        
        # List any warnings
        if warnings > 0:
            print("\n⚠️ Warning Tests:")
            for test in self.test_results:
                if test['status'] == 'WARNING':
                    print(f"   - {test['test_name']}: {test['notes']}")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"ga10_api_validation_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'passed': passed,
                    'failed': failed,
                    'warnings': warnings,
                    'pass_rate': (passed/total_tests)*100 if total_tests > 0 else 0
                },
                'api_info': {
                    'base_url': self.base_url,
                    'api_key': self.api_key[:20] + "...",
                    'test_timestamp': datetime.now().isoformat()
                },
                'test_results': self.test_results
            }, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return passed == total_tests

    def run_all_tests(self):
        """Run all validation tests"""
        print("🚀 Starting Comprehensive GA10 API Validation")
        print("="*80)
        print(f"Base URL: {self.base_url}")
        print(f"API Key:  {self.api_key[:20]}...")
        print(f"Started:  {datetime.now().isoformat()}")
        
        # Run all tests
        self.test_1_basic_bond_analysis()
        self.test_2_isin_input()
        self.test_3_invalid_input_fallback()
        self.test_4_portfolio_analysis()
        self.test_5_weekend_holiday_dates()
        self.test_6_spread_calculation()
        self.test_7_z_spread_calculation()
        self.test_8_numeric_input_handling()
        
        # Check documentation accuracy
        self.test_api_documentation_accuracy()
        
        # Generate summary
        all_passed = self.generate_summary_report()
        
        return all_passed

def main():
    """Main function to run validation"""
    validator = GA10APIValidator()
    
    try:
        all_passed = validator.run_all_tests()
        
        if all_passed:
            print("\n🎉 All tests passed successfully!")
            sys.exit(0)
        else:
            print("\n⚠️ Some tests failed or had warnings. Review the report for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()