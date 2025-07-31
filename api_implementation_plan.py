#!/usr/bin/env python3
"""
XTrillion API Implementation & Testing Plan
Complete testing suite and implementation roadmap for validation enhancement
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import sys
import os

# API Configuration
API_BASE_URL = "https://future-footing-414610.uc.r.appspot.com"
API_KEY = "gax10_demo_3j5h8m9k2p6r4t7w1q"

class XTrillionImplementationTester:
    """Complete testing and implementation validation for XTrillion API"""
    
    def __init__(self):
        self.base_url = API_BASE_URL
        self.api_key = API_KEY
        self.headers = {
            'Content-Type': 'application/json', 
            'X-API-Key': self.api_key
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.test_results = []
        self.implementation_plan = []
        
    def log_result(self, test_name: str, status: str, details: Any, implementation_note: str = None):
        """Log test results and implementation notes"""
        result = {
            "test": test_name,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details
        }
        
        if implementation_note:
            result["implementation_note"] = implementation_note
            
        self.test_results.append(result)
        
        status_icon = {"PASS": "✅", "FAIL": "❌", "PARTIAL": "⚠️", "MISSING": "🔍", "ERROR": "💥"}.get(status, "❓")
        print(f"{status_icon} {test_name}: {status}")
        
        if implementation_note:
            print(f"   💡 Implementation: {implementation_note}")
    
    def comprehensive_api_test(self):
        """Run comprehensive API testing"""
        print("🧪 XTrillion API Comprehensive Test Suite")
        print("="*60)
        
        # Test 1: Health endpoint with detailed validation
        print("\n1️⃣ Testing Health Endpoint...")
        self.test_health_detailed()
        
        # Test 2: Individual bond analysis with validation checks
        print("\n2️⃣ Testing Individual Bond Analysis...")
        self.test_bond_analysis_comprehensive()
        
        # Test 3: Portfolio analysis with data quality assessment
        print("\n3️⃣ Testing Portfolio Analysis...")
        self.test_portfolio_comprehensive()
        
        # Test 4: Error handling and edge cases
        print("\n4️⃣ Testing Error Handling...")
        self.test_error_scenarios()
        
        # Test 5: Performance and reliability
        print("\n5️⃣ Testing Performance...")
        self.test_performance()
        
        # Generate implementation roadmap
        print("\n6️⃣ Generating Implementation Plan...")
        self.generate_implementation_roadmap()
    
    def test_health_detailed(self):
        """Detailed health endpoint testing"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                health_data = response.json()
                
                # Test response structure
                expected_fields = ["status", "version", "service"]
                missing_fields = [f for f in expected_fields if f not in health_data]
                
                if not missing_fields:
                    self.log_result("Health Endpoint Structure", "PASS", 
                                  f"Response time: {response_time:.2f}s")
                else:
                    self.log_result("Health Endpoint Structure", "PARTIAL",
                                  f"Missing fields: {missing_fields}")
                
                # Check for enhanced features we need
                enhancements_needed = []
                if "validation_status" not in str(health_data):
                    enhancements_needed.append("validation_transparency")
                if "data_quality" not in str(health_data):
                    enhancements_needed.append("data_quality_metrics")
                
                if enhancements_needed:
                    self.log_result("Health Enhancement Check", "MISSING",
                                  enhancements_needed,
                                  "Add validation and data quality status to health endpoint")
                else:
                    self.log_result("Health Enhancement Check", "PASS", "All enhancements present")
                    
            else:
                self.log_result("Health Endpoint", "FAIL", 
                              f"HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            self.log_result("Health Endpoint", "ERROR", str(e),
                          "Check network connectivity and API availability")
    
    def test_bond_analysis_comprehensive(self):
        """Comprehensive bond analysis testing"""
        test_bonds = [
            {
                "name": "US Treasury",
                "payload": {"description": "T 3 15/08/52", "price": 71.66},
                "expected_validation": "parsed"
            },
            {
                "name": "Corporate Bond ISIN",
                "payload": {"isin": "US279158AJ82", "price": 69.31},
                "expected_validation": "validated"
            },
            {
                "name": "Emerging Market",
                "payload": {"description": "PANAMA, 3.87%, 23-Jul-2060", "price": 56.60},
                "expected_validation": "parsed"
            }
        ]
        
        for test_bond in test_bonds:
            try:
                start_time = time.time()
                response = self.session.post(
                    f"{self.base_url}/api/v1/bond/analysis",
                    json=test_bond["payload"],
                    timeout=15
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Test core structure
                    required_sections = ["status", "bond", "analytics"]
                    missing_sections = [s for s in required_sections if s not in data]
                    
                    if not missing_sections:
                        self.log_result(f"Bond Analysis - {test_bond['name']}", "PASS",
                                      f"Response time: {response_time:.2f}s")
                    else:
                        self.log_result(f"Bond Analysis - {test_bond['name']}", "PARTIAL",
                                      f"Missing sections: {missing_sections}")
                    
                    # Check for validation enhancement
                    bond_section = data.get("bond", {})
                    if "validation" in bond_section:
                        validation = bond_section["validation"]
                        required_validation_fields = ["status", "confidence", "source"]
                        missing_validation = [f for f in required_validation_fields if f not in validation]
                        
                        if not missing_validation:
                            self.log_result(f"Validation Enhancement - {test_bond['name']}", "PASS",
                                          validation)
                        else:
                            self.log_result(f"Validation Enhancement - {test_bond['name']}", "PARTIAL",
                                          f"Missing validation fields: {missing_validation}")
                    else:
                        self.log_result(f"Validation Enhancement - {test_bond['name']}", "MISSING",
                                      "No validation section found",
                                      "Implement validation section with status, confidence, source")
                    
                    # Test analytics completeness
                    analytics = data.get("analytics", {})
                    expected_analytics = ["ytm", "duration", "accrued_interest", "clean_price"]
                    missing_analytics = [a for a in expected_analytics if a not in analytics]
                    
                    if not missing_analytics:
                        self.log_result(f"Analytics Completeness - {test_bond['name']}", "PASS",
                                      f"Found {len(analytics)} analytics fields")
                    else:
                        self.log_result(f"Analytics Completeness - {test_bond['name']}", "PARTIAL",
                                      f"Missing analytics: {missing_analytics}")
                        
                else:
                    self.log_result(f"Bond Analysis - {test_bond['name']}", "FAIL",
                                  f"HTTP {response.status_code}: {response.text[:200]}")
                    
            except Exception as e:
                self.log_result(f"Bond Analysis - {test_bond['name']}", "ERROR", str(e))
                
            time.sleep(1)  # Rate limiting
    
    def test_portfolio_comprehensive(self):
        """Comprehensive portfolio analysis testing"""
        test_portfolio = {
            "data": [
                {"BOND_CD": "T 3 15/08/52", "CLOSING PRICE": 71.66, "WEIGHTING": 60.0},
                {"BOND_CD": "PANAMA, 3.87%, 23-Jul-2060", "CLOSING PRICE": 56.60, "WEIGHTING": 40.0}
            ]
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/api/v1/portfolio/analysis",
                json=test_portfolio,
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Test core portfolio structure
                required_sections = ["bond_data", "portfolio_metrics"]
                missing_sections = [s for s in required_sections if s not in data]
                
                if not missing_sections:
                    self.log_result("Portfolio Analysis Structure", "PASS",
                                  f"Response time: {response_time:.2f}s")
                else:
                    self.log_result("Portfolio Analysis Structure", "PARTIAL",
                                  f"Missing sections: {missing_sections}")
                
                # Check for enhanced portfolio validation
                portfolio_metrics = data.get("portfolio_metrics", {})
                if "data_quality" in portfolio_metrics:
                    data_quality = portfolio_metrics["data_quality"]
                    self.log_result("Portfolio Data Quality", "PASS", data_quality)
                else:
                    self.log_result("Portfolio Data Quality", "MISSING",
                                  "No data_quality section in portfolio_metrics",
                                  "Add portfolio-level data quality aggregation")
                
                # Check individual bond validation in portfolio
                bond_data = data.get("bond_data", [])
                bonds_with_validation = [b for b in bond_data if "validation" in b]
                
                if bonds_with_validation:
                    self.log_result("Portfolio Bond Validation", "PASS",
                                  f"{len(bonds_with_validation)}/{len(bond_data)} bonds have validation")
                else:
                    self.log_result("Portfolio Bond Validation", "MISSING",
                                  "No individual bond validation in portfolio",
                                  "Add validation section to each bond in portfolio response")
                    
            else:
                self.log_result("Portfolio Analysis", "FAIL",
                              f"HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            self.log_result("Portfolio Analysis", "ERROR", str(e))
    
    def test_error_scenarios(self):
        """Test error handling and edge cases"""
        error_tests = [
            {
                "name": "Invalid API Key",
                "headers": {"Content-Type": "application/json", "X-API-Key": "invalid_key"},
                "payload": {"description": "T 3 15/08/52", "price": 71.66},
                "expected_status": 401
            },
            {
                "name": "Missing Bond Data",
                "headers": self.headers,
                "payload": {"price": 71.66},  # No bond identifier
                "expected_status": 400
            },
            {
                "name": "Invalid Price",
                "headers": self.headers,
                "payload": {"description": "T 3 15/08/52", "price": "invalid"},
                "expected_status": 400
            }
        ]
        
        for test in error_tests:
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/bond/analysis",
                    json=test["payload"],
                    headers=test["headers"],
                    timeout=10
                )
                
                if response.status_code == test["expected_status"]:
                    self.log_result(f"Error Handling - {test['name']}", "PASS",
                                  f"Correct status: {response.status_code}")
                else:
                    self.log_result(f"Error Handling - {test['name']}", "FAIL",
                                  f"Expected {test['expected_status']}, got {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Error Handling - {test['name']}", "ERROR", str(e))
                
            time.sleep(0.5)
    
    def test_performance(self):
        """Test API performance characteristics"""
        # Test response times
        bonds_to_test = [
            {"description": "T 3 15/08/52", "price": 71.66},
            {"isin": "US279158AJ82", "price": 69.31}
        ]
        
        response_times = []
        
        for bond in bonds_to_test:
            try:
                start_time = time.time()
                response = self.session.post(
                    f"{self.base_url}/api/v1/bond/analysis",
                    json=bond,
                    timeout=15
                )
                response_time = time.time() - start_time
                response_times.append(response_time)
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                self.log_result("Performance Test", "ERROR", str(e))
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            
            if avg_response_time < 3.0:
                self.log_result("Performance - Average Response", "PASS",
                              f"Average: {avg_response_time:.2f}s")
            else:
                self.log_result("Performance - Average Response", "PARTIAL",
                              f"Average: {avg_response_time:.2f}s (>3s threshold)")
            
            if max_response_time < 5.0:
                self.log_result("Performance - Max Response", "PASS",
                              f"Max: {max_response_time:.2f}s")
            else:
                self.log_result("Performance - Max Response", "PARTIAL",
                              f"Max: {max_response_time:.2f}s (>5s threshold)")
    
    def generate_implementation_roadmap(self):
        """Generate implementation roadmap based on test results"""
        print("\n" + "="*80)
        print("🗺️ IMPLEMENTATION ROADMAP")
        print("="*80)
        
        # Analyze test results
        total_tests = len(self.test_results)
        status_counts = {}
        for result in self.test_results:
            status = result["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\n📊 Test Summary:")
        for status, count in status_counts.items():
            icon = {"PASS": "✅", "FAIL": "❌", "PARTIAL": "⚠️", "MISSING": "🔍", "ERROR": "💥"}.get(status, "❓")
            print(f"   {icon} {status}: {count}")
        
        # Implementation priorities
        print(f"\n🎯 Implementation Priorities:")
        
        missing_features = [r for r in self.test_results if r["status"] == "MISSING"]
        high_priority = []
        medium_priority = []
        low_priority = []
        
        for feature in missing_features:
            if "validation" in feature["test"].lower():
                high_priority.append(feature)
            elif "enhancement" in feature["test"].lower():
                medium_priority.append(feature)
            else:
                low_priority.append(feature)
        
        print(f"\n🔴 HIGH PRIORITY ({len(high_priority)} items):")
        for item in high_priority:
            print(f"   • {item['test']}")
            if "implementation_note" in item:
                print(f"     → {item['implementation_note']}")
        
        print(f"\n🟡 MEDIUM PRIORITY ({len(medium_priority)} items):")
        for item in medium_priority:
            print(f"   • {item['test']}")
            if "implementation_note" in item:
                print(f"     → {item['implementation_note']}")
        
        print(f"\n🟢 LOW PRIORITY ({len(low_priority)} items):")
        for item in low_priority:
            print(f"   • {item['test']}")
        
        # Generate implementation plan
        self.implementation_plan = {
            "phase_1_critical": [
                "Implement validation section in bond responses",
                "Add confidence scoring (high/medium/low)",
                "Add data source attribution", 
                "Update individual bond analysis endpoint"
            ],
            "phase_2_enhancement": [
                "Add portfolio-level data quality metrics",
                "Implement validation for portfolio bonds",
                "Add field-level validation details",
                "Create Excel xt_validation_*() functions"
            ],
            "phase_3_optimization": [
                "Improve error handling and messaging",
                "Optimize response times",
                "Add advanced validation features",
                "Implement custom validation rules"
            ]
        }
        
        print(f"\n📋 Implementation Plan:")
        for phase, tasks in self.implementation_plan.items():
            print(f"\n{phase.upper().replace('_', ' ')}:")
            for task in tasks:
                print(f"   □ {task}")
        
        return self.implementation_plan
    
    def save_results(self, filename: str = None):
        """Save test results and implementation plan"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"xtrillion_implementation_test_{timestamp}.json"
        
        results = {
            "test_summary": {
                "timestamp": datetime.utcnow().isoformat(),
                "total_tests": len(self.test_results),
                "api_base_url": self.base_url,
                "api_status": "operational" if any(r["status"] == "PASS" for r in self.test_results) else "issues"
            },
            "test_results": self.test_results,
            "implementation_plan": self.implementation_plan,
            "next_steps": [
                "Implement Phase 1 validation enhancements",
                "Update API specification documents",
                "Test enhanced endpoints",
                "Deploy to production"
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {filename}")
        return filename

def main():
    """Main implementation testing"""
    print("🎯 XTrillion API Implementation & Testing Suite")
    print("   Complete testing and roadmap generation")
    print("   For validation enhancement implementation")
    print("="*60)
    
    tester = XTrillionImplementationTester()
    
    # Run comprehensive tests
    tester.comprehensive_api_test()
    
    # Save results
    results_file = tester.save_results()
    
    print(f"\n🚀 Implementation Testing Complete!")
    print(f"📊 Results and roadmap saved to: {results_file}")
    print(f"📋 Ready to implement validation enhancements!")
    
    return tester.test_results, tester.implementation_plan

if __name__ == "__main__":
    main()