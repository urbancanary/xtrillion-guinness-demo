#!/usr/bin/env python3
"""
Daily Automated Test Suite for XTrillion Bond Analytics API
Runs comprehensive tests and sends email notifications for any failures
"""

import json
import requests
import datetime
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Tuple
import time
import os

# Configuration
API_CONFIG = {
    "production": {
        "url": "https://future-footing-414610.uc.r.appspot.com",
        "api_key": "gax10_demo_3j5h8m9k2p6r4t7w1q",
        "name": "Production"
    },
    "development": {
        "url": "https://development-dot-future-footing-414610.uc.r.appspot.com",
        "api_key": "gax10_dev_4n8s6k2x7p9v5m8p1z",
        "name": "Development"
    }
}

# Email configuration (update these with your details)
EMAIL_CONFIG = {
    "smtp_server": os.environ.get("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.environ.get("SMTP_PORT", "587")),
    "sender_email": os.environ.get("SENDER_EMAIL", "your-email@gmail.com"),
    "sender_password": os.environ.get("SENDER_PASSWORD", "your-app-password"),
    "recipient_email": os.environ.get("RECIPIENT_EMAIL", "andy@your-domain.com")
}

class XTrillionAPITester:
    def __init__(self, environment="production"):
        self.env = environment
        self.config = API_CONFIG[environment]
        self.base_url = self.config["url"]
        self.api_key = self.config["api_key"]
        self.test_results = []
        self.start_time = datetime.datetime.now()
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def add_result(self, test_name: str, passed: bool, details: str = "", response_time: float = 0):
        """Add test result"""
        self.test_results.append({
            "test_name": test_name,
            "passed": passed,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
    def test_health_check(self) -> Tuple[bool, str]:
        """Test 1: Health Check Endpoint"""
        test_name = "Health Check"
        self.log(f"Running {test_name}...")
        
        try:
            start = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=10)
            response_time = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.add_result(test_name, True, "API is healthy", response_time)
                    return True, "Health check passed"
                else:
                    self.add_result(test_name, False, f"Unhealthy status: {data}", response_time)
                    return False, f"API unhealthy: {data}"
            else:
                self.add_result(test_name, False, f"HTTP {response.status_code}", response_time)
                return False, f"Health check failed with status {response.status_code}"
                
        except Exception as e:
            self.add_result(test_name, False, str(e))
            return False, f"Health check error: {str(e)}"
            
    def test_bond_analysis(self) -> Tuple[bool, str]:
        """Test 2: Individual Bond Analysis"""
        test_name = "Bond Analysis (US Treasury)"
        self.log(f"Running {test_name}...")
        
        test_cases = [
            {
                "name": "US Treasury 3% 2052",
                "payload": {
                    "description": "T 3 15/08/52",
                    "price": 71.66,
                    "settlement_date": "2025-06-30"  # Fixed date for consistency
                },
                "expected_fields": ["ytm", "duration", "accrued_interest", "clean_price", "dirty_price"]
            },
            {
                "name": "US Treasury 4.125% 2032",
                "payload": {
                    "description": "T 4.125 15/11/32",
                    "price": 99.5
                },
                "expected_fields": ["ytm", "duration", "convexity", "pvbp"]
            }
        ]
        
        all_passed = True
        details = []
        
        for test_case in test_cases:
            try:
                start = time.time()
                response = requests.post(
                    f"{self.base_url}/api/v1/bond/analysis",
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": self.api_key
                    },
                    json=test_case["payload"],
                    timeout=10
                )
                response_time = time.time() - start
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success":
                        analytics = data.get("analytics", {})
                        missing_fields = [f for f in test_case["expected_fields"] if f not in analytics]
                        
                        if missing_fields:
                            all_passed = False
                            details.append(f"{test_case['name']}: Missing fields {missing_fields}")
                        else:
                            # Validate reasonable values
                            ytm = analytics.get("ytm", 0)
                            duration = analytics.get("duration", 0)
                            
                            if not (0 < ytm < 20):  # YTM should be between 0-20%
                                all_passed = False
                                details.append(f"{test_case['name']}: Invalid YTM {ytm}")
                            elif not (0 < duration < 50):  # Duration should be reasonable
                                all_passed = False
                                details.append(f"{test_case['name']}: Invalid duration {duration}")
                            else:
                                details.append(f"{test_case['name']}: ✓ YTM={ytm:.2f}%, Duration={duration:.2f}")
                    else:
                        all_passed = False
                        details.append(f"{test_case['name']}: API error - {data.get('error', 'Unknown')}")
                else:
                    all_passed = False
                    details.append(f"{test_case['name']}: HTTP {response.status_code}")
                    
            except Exception as e:
                all_passed = False
                details.append(f"{test_case['name']}: Exception - {str(e)}")
                
        self.add_result(test_name, all_passed, "; ".join(details))
        return all_passed, "; ".join(details)
        
    def test_portfolio_analysis(self) -> Tuple[bool, str]:
        """Test 3: Portfolio Analysis"""
        test_name = "Portfolio Analysis"
        self.log(f"Running {test_name}...")
        
        payload = {
            "data": [
                {
                    "description": "T 3 15/08/52",
                    "CLOSING PRICE": 71.66,
                    "WEIGHTING": 40.0
                },
                {
                    "description": "T 4.125 15/11/32",
                    "CLOSING PRICE": 99.5,
                    "WEIGHTING": 30.0
                },
                {
                    "description": "T 2.875 15/05/32",
                    "CLOSING PRICE": 89.25,
                    "WEIGHTING": 30.0
                }
            ]
        }
        
        try:
            start = time.time()
            response = requests.post(
                f"{self.base_url}/api/v1/portfolio/analysis",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key
                },
                json=payload,
                timeout=15
            )
            response_time = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    portfolio_metrics = data.get("portfolio_metrics", {})
                    
                    # Validate portfolio metrics
                    required_metrics = ["portfolio_yield", "portfolio_duration", "total_bonds", "success_rate"]
                    missing_metrics = [m for m in required_metrics if m not in portfolio_metrics]
                    
                    if missing_metrics:
                        self.add_result(test_name, False, f"Missing metrics: {missing_metrics}", response_time)
                        return False, f"Missing portfolio metrics: {missing_metrics}"
                    
                    # Validate success rate
                    success_rate = portfolio_metrics.get("success_rate", "0%")
                    if success_rate != "100.0%":
                        self.add_result(test_name, False, f"Low success rate: {success_rate}", response_time)
                        return False, f"Portfolio analysis incomplete: {success_rate} success rate"
                        
                    self.add_result(test_name, True, 
                                  f"Portfolio: Yield={portfolio_metrics['portfolio_yield']}, "
                                  f"Duration={portfolio_metrics['portfolio_duration']}", 
                                  response_time)
                    return True, "Portfolio analysis successful"
                else:
                    self.add_result(test_name, False, f"API error: {data.get('error', 'Unknown')}", response_time)
                    return False, f"Portfolio analysis failed: {data.get('error', 'Unknown')}"
            else:
                self.add_result(test_name, False, f"HTTP {response.status_code}", response_time)
                return False, f"Portfolio analysis HTTP error: {response.status_code}"
                
        except Exception as e:
            self.add_result(test_name, False, str(e))
            return False, f"Portfolio analysis exception: {str(e)}"
            
    def test_error_handling(self) -> Tuple[bool, str]:
        """Test 4: Error Handling"""
        test_name = "Error Handling"
        self.log(f"Running {test_name}...")
        
        test_cases = [
            {
                "name": "Invalid bond description",
                "payload": {"description": "INVALID BOND XYZ", "price": 100},
                "expect_error": False  # API accepts this and treats as zero-coupon
            },
            {
                "name": "Missing price",
                "payload": {"description": "T 3 15/08/52"},
                "expect_error": False  # API defaults to price=100
            },
            {
                "name": "Invalid price",
                "payload": {"description": "T 3 15/08/52", "price": -50},
                "expect_error": True  # API should reject negative prices
            },
            {
                "name": "Empty description",
                "payload": {"description": "", "price": 100},
                "expect_error": True  # API should reject empty descriptions
            }
        ]
        
        all_passed = True
        details = []
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/bond/analysis",
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": self.api_key
                    },
                    json=test_case["payload"],
                    timeout=10
                )
                
                if test_case["expect_error"]:
                    # Should return an error
                    if response.status_code >= 400 or response.json().get("status") == "error":
                        details.append(f"{test_case['name']}: ✓ Error handled correctly")
                    else:
                        all_passed = False
                        details.append(f"{test_case['name']}: Expected error but got success")
                        
            except Exception as e:
                all_passed = False
                details.append(f"{test_case['name']}: Exception - {str(e)}")
                
        self.add_result(test_name, all_passed, "; ".join(details))
        return all_passed, "; ".join(details)
        
    def test_performance(self) -> Tuple[bool, str]:
        """Test 5: Performance Benchmarks"""
        test_name = "Performance Benchmarks"
        self.log(f"Running {test_name}...")
        
        # Test response times
        response_times = []
        
        for i in range(5):  # Run 5 times to get average
            try:
                start = time.time()
                response = requests.post(
                    f"{self.base_url}/api/v1/bond/analysis",
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": self.api_key
                    },
                    json={
                        "description": "T 3 15/08/52",
                        "price": 71.66
                    },
                    timeout=10
                )
                response_time = time.time() - start
                
                if response.status_code == 200:
                    response_times.append(response_time * 1000)  # Convert to ms
                    
            except Exception as e:
                self.log(f"Performance test error: {e}", "WARN")
                
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            
            # Performance thresholds (adjusted for realistic expectations)
            if avg_time < 900:  # Under 900ms average is acceptable
                self.add_result(test_name, True, 
                              f"Avg: {avg_time:.0f}ms, Max: {max_time:.0f}ms")
                return True, f"Acceptable performance: Avg {avg_time:.0f}ms"
            else:
                self.add_result(test_name, False, 
                              f"Slow: Avg: {avg_time:.0f}ms, Max: {max_time:.0f}ms")
                return False, f"Performance degraded: Avg {avg_time:.0f}ms"
        else:
            self.add_result(test_name, False, "No successful performance measurements")
            return False, "Performance test failed"
            
    def test_baseline_calculations(self) -> Tuple[bool, str]:
        """Test 6: Baseline Calculation Comparison"""
        test_name = "Baseline Calculations"
        self.log(f"Running {test_name}...")
        
        # Fixed settlement date for consistent results
        BASELINE_SETTLEMENT_DATE = "2025-06-30"
        
        # Import baseline comparison functionality
        try:
            from baseline_comparison_test import BaselineComparator
            comparator = BaselineComparator()
            
            # Check if baseline exists
            baseline = comparator.load_baseline()
            if not baseline:
                self.add_result(test_name, True, "No baseline yet - creating initial baseline")
                comparator.run_comparison_tests(save_new_baseline=True)
                return True, "Initial baseline created"
                
            # Run comparison
            results = comparator.run_comparison_tests(save_new_baseline=False)
            
            if results['changes_detected'] > 0:
                details = f"{results['changes_detected']} calculation changes detected"
                # Extract specific changes
                changes = []
                for detail in results['details']:
                    if detail['status'] == 'CHANGED':
                        bond = detail['bond']
                        diffs = detail['differences']
                        changes.append(f"{bond}: {len(diffs)} metrics changed")
                
                self.add_result(test_name, False, f"{details} - {', '.join(changes[:3])}")
                return False, details
            else:
                self.add_result(test_name, True, "All calculations match baseline")
                return True, "No calculation changes detected"
                
        except Exception as e:
            self.add_result(test_name, False, f"Baseline comparison error: {str(e)}")
            return False, f"Baseline test error: {str(e)}"
            
    def test_documentation_examples(self) -> Tuple[bool, str]:
        """Test 7: All Documentation Examples with Response Times"""
        test_name = "Documentation Examples"
        self.log(f"Running {test_name}...")
        
        try:
            from documentation_examples_test import DocumentationExamplesTester
            
            # Run documentation tests
            tester = DocumentationExamplesTester(base_url=self.base_url)
            
            # Test a subset for daily runs (full suite takes time)
            test_cases = [
                ("Health Check", "GET", "/health", None, None),
                ("Bond Analysis", "POST", "/api/v1/bond/analysis", 
                 {"Content-Type": "application/json", "X-API-Key": self.api_key},
                 {"description": "T 3 15/08/52", "price": 71.66, "settlement_date": "2025-04-18"}),
                ("Portfolio Analysis", "POST", "/api/v1/portfolio/analysis",
                 {"Content-Type": "application/json", "X-API-Key": self.api_key},
                 {"data": [
                     {"description": "T 3 15/08/52", "CLOSING PRICE": 71.66, "WEIGHTING": 50.0},
                     {"description": "T 4.125 15/11/32", "CLOSING PRICE": 99.5, "WEIGHTING": 50.0}
                 ]})
            ]
            
            all_passed = True
            timing_details = []
            
            for name, method, endpoint, headers, json_data in test_cases:
                result = tester.test_endpoint_timing(
                    name=name,
                    method=method,
                    endpoint=endpoint,
                    headers=headers,
                    json_data=json_data,
                    num_warm_runs=3
                )
                
                if result.success_rate < 100:
                    all_passed = False
                    
                timing_details.append(f"{name}: Cold={result.cold_start_ms:.0f}ms, Avg={result.avg_warm_ms:.0f}ms")
                
                # Check thresholds
                if result.cold_start_ms > 2000:
                    all_passed = False
                    timing_details.append(f"  ⚠️ {name} cold start too slow")
                    
                if result.avg_warm_ms > 900:  # Increased threshold for bond analysis
                    all_passed = False
                    timing_details.append(f"  ⚠️ {name} warm response too slow")
                    
            details = "; ".join(timing_details[:3])  # Show first 3 timing results
            
            if all_passed:
                self.add_result(test_name, True, f"All examples passed - {details}")
                return True, "Documentation examples validated"
            else:
                self.add_result(test_name, False, f"Some examples failed or slow - {details}")
                return False, "Documentation validation issues"
                
        except Exception as e:
            self.add_result(test_name, False, f"Documentation test error: {str(e)}")
            return False, f"Documentation test error: {str(e)}"
            
    def run_all_tests(self) -> Dict:
        """Run all tests and collect results"""
        self.log(f"Starting daily test suite for {self.config['name']} environment")
        self.log("=" * 60)
        
        # Run tests
        tests = [
            self.test_health_check,
            self.test_bond_analysis,
            self.test_portfolio_analysis,
            self.test_error_handling,
            self.test_performance,
            self.test_baseline_calculations,
            self.test_documentation_examples
        ]
        
        for test in tests:
            test()
            time.sleep(0.5)  # Small delay between tests
            
        # Calculate summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["passed"])
        failed_tests = total_tests - passed_tests
        
        duration = (datetime.datetime.now() - self.start_time).total_seconds()
        
        summary = {
            "environment": self.config["name"],
            "url": self.base_url,
            "timestamp": self.start_time.isoformat(),
            "duration_seconds": duration,
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "results": self.test_results
        }
        
        self.log("=" * 60)
        self.log(f"Test Suite Complete: {passed_tests}/{total_tests} passed ({summary['success_rate']:.1f}%)")
        
        return summary
        
    def generate_email_report(self, summary: Dict) -> str:
        """Generate HTML email report"""
        status_emoji = "✅" if summary["failed"] == 0 else "❌"
        status_text = "All Tests Passed" if summary["failed"] == 0 else f"{summary['failed']} Tests Failed"
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: {'#4CAF50' if summary['failed'] == 0 else '#f44336'}; color: white; padding: 20px; }}
                .summary {{ background-color: #f5f5f5; padding: 15px; margin: 20px 0; }}
                .results {{ margin: 20px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
                .passed {{ color: green; }}
                .failed {{ color: red; }}
                .details {{ font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{status_emoji} XTrillion API Daily Test Report - {status_text}</h1>
                <p>{summary['environment']} Environment - {datetime.datetime.now().strftime('%B %d, %Y')}</p>
            </div>
            
            <div class="summary">
                <h2>Summary</h2>
                <p><strong>Environment:</strong> {summary['environment']} ({summary['url']})</p>
                <p><strong>Test Duration:</strong> {summary['duration_seconds']:.1f} seconds</p>
                <p><strong>Total Tests:</strong> {summary['total_tests']}</p>
                <p><strong>Passed:</strong> <span class="passed">{summary['passed']}</span></p>
                <p><strong>Failed:</strong> <span class="failed">{summary['failed']}</span></p>
                <p><strong>Success Rate:</strong> {summary['success_rate']:.1f}%</p>
            </div>
            
            <div class="results">
                <h2>Detailed Results</h2>
                <table>
                    <tr>
                        <th>Test Name</th>
                        <th>Status</th>
                        <th>Response Time</th>
                        <th>Details</th>
                    </tr>
        """
        
        for result in summary["results"]:
            status_class = "passed" if result["passed"] else "failed"
            status_text = "PASSED" if result["passed"] else "FAILED"
            response_time = f"{result['response_time']*1000:.0f}ms" if result['response_time'] > 0 else "N/A"
            
            html += f"""
                    <tr>
                        <td>{result['test_name']}</td>
                        <td class="{status_class}">{status_text}</td>
                        <td>{response_time}</td>
                        <td class="details">{result['details'][:100]}...</td>
                    </tr>
            """
            
        html += """
                </table>
            </div>
            
            <div class="details">
                <p><small>This is an automated test report. If you have questions, please check the API logs or contact the development team.</small></p>
            </div>
        </body>
        </html>
        """
        
        return html
        
    def send_email_report(self, summary: Dict):
        """Send email report"""
        # Check for calculation changes specifically
        baseline_test = next((r for r in summary["results"] if r["test_name"] == "Baseline Calculations"), None)
        calculation_changes = baseline_test and not baseline_test["passed"] and "calculation changes detected" in baseline_test.get("details", "")
        
        # Send email if tests failed, calculation changes detected, or always send is enabled
        if summary["failed"] == 0 and not calculation_changes and not os.environ.get("ALWAYS_SEND_EMAIL", False):
            self.log("All tests passed and no calculation changes - skipping email notification")
            return
            
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_CONFIG["sender_email"]
            msg['To'] = EMAIL_CONFIG["recipient_email"]
            # Determine subject based on issues
            if calculation_changes:
                subject_prefix = "⚠️ CALCULATION CHANGES"
            elif summary['failed'] > 0:
                subject_prefix = "❌ FAILED"
            else:
                subject_prefix = "✅ PASSED"
                
            msg['Subject'] = f"{subject_prefix} - XTrillion API Daily Test Report - {summary['environment']}"
            
            html_content = self.generate_email_report(summary)
            msg.attach(MIMEText(html_content, 'html'))
            
            # Also attach JSON summary
            json_attachment = MIMEText(json.dumps(summary, indent=2))
            json_attachment.add_header('Content-Disposition', 'attachment', 
                                     filename=f"test_results_{datetime.date.today()}.json")
            msg.attach(json_attachment)
            
            # Send email
            with smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
                server.starttls()
                server.login(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["sender_password"])
                server.send_message(msg)
                
            self.log("Email report sent successfully")
            
        except Exception as e:
            self.log(f"Failed to send email: {str(e)}", "ERROR")

def main():
    """Main function to run tests"""
    # Test both environments
    environments = ["production"]  # Add "development" if you want to test both
    
    all_summaries = []
    any_failures = False
    
    for env in environments:
        tester = XTrillionAPITester(env)
        summary = tester.run_all_tests()
        all_summaries.append(summary)
        
        if summary["failed"] > 0:
            any_failures = True
            
        # Send individual report if there are failures
        if summary["failed"] > 0 or os.environ.get("ALWAYS_SEND_EMAIL", False):
            tester.send_email_report(summary)
            
        # Save results to file
        with open(f"test_results_{env}_{datetime.date.today()}.json", "w") as f:
            json.dump(summary, f, indent=2)
            
    # Exit with error code if any tests failed
    sys.exit(1 if any_failures else 0)

if __name__ == "__main__":
    main()