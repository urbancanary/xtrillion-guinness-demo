#!/usr/bin/env python3
"""
Comprehensive Test: Local Code vs Local API
==========================================

Tests bond yield, spread, and duration calculations using:
1. Direct local code execution 
2. Local API calls
3. Side-by-side comparison of results

This will help identify any discrepancies before cloud deployment.
"""

import sys
import os
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
import logging

# Add current directory to path for imports
sys.path.append('.')

# Import the google_analysis10 calculation engine directly
from google_analysis10 import (
    process_bonds_without_weightings,
    fetch_latest_trade_date,
    fetch_treasury_yields,
    create_treasury_curve,
    parse_date
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LocalVsAPITester:
    """
    Comprehensive testing framework for comparing local calculations vs API results
    """
    
    def __init__(self, api_base_url="http://localhost:8080"):
        self.api_base_url = api_base_url
        self.results = []
        
    def test_bonds(self, test_bonds, settlement_date=None, test_name="Bond Test"):
        """
        Test a list of bonds using both local code and API
        
        Args:
            test_bonds: List of dicts with 'isin', 'price', 'weighting' (optional)
            settlement_date: Settlement date to use (defaults to prior month end)
            test_name: Name for this test run
        """
        logger.info(f"🧪 Starting {test_name}")
        logger.info(f"📊 Testing {len(test_bonds)} bonds")
        
        # Prepare test data
        test_data = {
            "data": []
        }
        
        for bond in test_bonds:
            bond_data = {
                "BOND_CD": bond["isin"],
                "CLOSING PRICE": bond["price"]
            }
            if "weighting" in bond:
                bond_data["WEIGHTING"] = bond["weighting"]
            test_data["data"].append(bond_data)
        
        if settlement_date:
            test_data["settlement_date"] = settlement_date
            
        logger.info(f"📋 Test data prepared: {json.dumps(test_data, indent=2)}")
        
        # Test 1: Direct local code calculation
        logger.info("🔧 Testing direct local code calculation...")
        local_results = self._test_local_direct(test_data, test_name)
        
        # Test 2: Local API call
        logger.info("🌐 Testing local API call...")
        api_results = self._test_local_api(test_data, test_name)
        
        # Test 3: Compare results
        logger.info("📊 Comparing results...")
        comparison = self._compare_results(local_results, api_results, test_name)
        
        return {
            "test_name": test_name,
            "local_results": local_results,
            "api_results": api_results,
            "comparison": comparison,
            "test_data": test_data
        }
    
    def _test_local_direct(self, test_data, test_name):
        """Test using direct local code execution"""
        try:
            logger.info("🔧 Executing direct local calculation...")
            
            # Convert test data to DataFrame format expected by local code
            df = pd.DataFrame(test_data["data"])
            
            # Use the database path from google_analysis10
            db_path = "./bonds_data.db"
            validated_db_path = "./validated_quantlib_bonds.db"
            
            if not os.path.exists(db_path):
                db_path = "./data/bonds_data.db"
            if not os.path.exists(validated_db_path):
                validated_db_path = "./data/validated_quantlib_bonds.db"
                
            logger.info(f"📁 Using database: {db_path}")
            logger.info(f"📁 Using validated database: {validated_db_path}")
            
            # Process bonds using local code
            results_df = process_bonds_without_weightings(
                df, 
                db_path=db_path,
                validated_db_path=validated_db_path
            )
            
            # Convert results to dictionary format
            if isinstance(results_df, pd.DataFrame) and not results_df.empty:
                results = results_df.to_dict('records')
                logger.info(f"✅ Local direct calculation successful: {len(results)} bonds processed")
                return {
                    "status": "success",
                    "results": results,
                    "method": "local_direct",
                    "bonds_processed": len(results)
                }
            else:
                logger.error("❌ Local direct calculation returned empty results")
                return {
                    "status": "error",
                    "error": "Empty results from local calculation",
                    "method": "local_direct"
                }
                
        except Exception as e:
            logger.error(f"❌ Local direct calculation failed: {e}")
            return {
                "status": "error", 
                "error": str(e),
                "method": "local_direct"
            }
    
    def _test_local_api(self, test_data, test_name):
        """Test using local API call"""
        try:
            logger.info(f"🌐 Calling local API at {self.api_base_url}")
            
            # Test API health first
            health_response = requests.get(f"{self.api_base_url}/health", timeout=10)
            if health_response.status_code != 200:
                raise Exception(f"API health check failed: {health_response.status_code}")
            
            logger.info("✅ API health check passed")
            
            # Make API call for bond analysis
            api_endpoint = f"{self.api_base_url}/api/v1/portfolio/analyze"
            
            response = requests.post(
                api_endpoint,
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                api_result = response.json()
                logger.info("✅ Local API call successful")
                return {
                    "status": "success",
                    "results": api_result,
                    "method": "local_api",
                    "response_status": response.status_code
                }
            else:
                logger.error(f"❌ API call failed with status {response.status_code}")
                logger.error(f"Response: {response.text}")
                return {
                    "status": "error",
                    "error": f"API returned status {response.status_code}: {response.text}",
                    "method": "local_api",
                    "response_status": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Local API call failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "method": "local_api"
            }
    
    def _compare_results(self, local_results, api_results, test_name):
        """Compare results from local code vs API"""
        comparison = {
            "test_name": test_name,
            "timestamp": datetime.now().isoformat(),
            "local_status": local_results.get("status"),
            "api_status": api_results.get("status"),
            "discrepancies": [],
            "summary": {}
        }
        
        if local_results.get("status") != "success":
            comparison["summary"]["local_error"] = local_results.get("error")
            
        if api_results.get("status") != "success":
            comparison["summary"]["api_error"] = api_results.get("error")
            
        if local_results.get("status") == "success" and api_results.get("status") == "success":
            # Both succeeded - compare detailed results
            local_data = local_results.get("results", [])
            api_data = api_results.get("results", {})
            
            # Extract bond-level results from API response
            api_bonds = []
            if "bond_analytics" in api_data:
                api_bonds = api_data["bond_analytics"]
            elif "bonds" in api_data:
                api_bonds = api_data["bonds"]
            elif isinstance(api_data, list):
                api_bonds = api_data
                
            comparison["summary"]["local_bonds"] = len(local_data)
            comparison["summary"]["api_bonds"] = len(api_bonds)
            
            # Compare bond by bond
            for i, local_bond in enumerate(local_data):
                if i < len(api_bonds):
                    api_bond = api_bonds[i]
                    bond_comparison = self._compare_bond_metrics(local_bond, api_bond, i)
                    if bond_comparison["has_discrepancies"]:
                        comparison["discrepancies"].append(bond_comparison)
            
            # Calculate overall match rate
            total_comparisons = len(local_data)
            discrepancy_count = len(comparison["discrepancies"])
            match_rate = ((total_comparisons - discrepancy_count) / total_comparisons * 100) if total_comparisons > 0 else 0
            
            comparison["summary"]["match_rate"] = f"{match_rate:.1f}%"
            comparison["summary"]["discrepancy_count"] = discrepancy_count
            comparison["summary"]["total_bonds"] = total_comparisons
            
        return comparison
    
    def _compare_bond_metrics(self, local_bond, api_bond, bond_index):
        """Compare metrics for a single bond"""
        bond_comparison = {
            "bond_index": bond_index,
            "isin": local_bond.get("ISIN") or local_bond.get("isin") or f"Bond_{bond_index}",
            "has_discrepancies": False,
            "metrics": {}
        }
        
        # Define metric mappings and tolerances
        metric_mappings = [
            ("yield", ["Yield (%)", "yield", "bond_yield"], 0.01),  # 1bp tolerance
            ("duration", ["Duration (years)", "duration", "bond_duration"], 0.01),  # 0.01 year tolerance  
            ("spread", ["Spread (bps)", "spread", "bond_spread"], 1.0),  # 1bp tolerance
        ]
        
        for metric_name, field_names, tolerance in metric_mappings:
            local_value = self._extract_metric_value(local_bond, field_names)
            api_value = self._extract_metric_value(api_bond, field_names)
            
            if local_value is not None and api_value is not None:
                diff = abs(local_value - api_value)
                matches = diff <= tolerance
                
                bond_comparison["metrics"][metric_name] = {
                    "local": local_value,
                    "api": api_value,
                    "difference": diff,
                    "tolerance": tolerance,
                    "matches": matches
                }
                
                if not matches:
                    bond_comparison["has_discrepancies"] = True
            else:
                bond_comparison["metrics"][metric_name] = {
                    "local": local_value,
                    "api": api_value,
                    "matches": False,
                    "error": "Missing data"
                }
                bond_comparison["has_discrepancies"] = True
        
        return bond_comparison
    
    def _extract_metric_value(self, bond_data, field_names):
        """Extract a metric value from bond data using various field name attempts"""
        for field_name in field_names:
            if field_name in bond_data:
                value = bond_data[field_name]
                if value is not None and str(value).strip() != "":
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        continue
        return None
    
    def print_comparison_summary(self, test_result):
        """Print a formatted summary of test results"""
        print("\n" + "="*80)
        print(f"🧪 TEST RESULTS: {test_result['test_name']}")
        print("="*80)
        
        comparison = test_result["comparison"]
        
        print(f"📊 Local Status: {comparison['local_status']}")
        print(f"🌐 API Status: {comparison['api_status']}")
        
        if comparison.get("summary"):
            summary = comparison["summary"]
            if "match_rate" in summary:
                print(f"✅ Match Rate: {summary['match_rate']}")
                print(f"📈 Bonds Compared: {summary['total_bonds']}")
                print(f"⚠️  Discrepancies: {summary['discrepancy_count']}")
            
            if "local_error" in summary:
                print(f"❌ Local Error: {summary['local_error']}")
            if "api_error" in summary:
                print(f"❌ API Error: {summary['api_error']}")
        
        # Print detailed discrepancies
        if comparison.get("discrepancies"):
            print(f"\n🔍 DETAILED DISCREPANCIES:")
            for disc in comparison["discrepancies"]:
                print(f"\n📋 Bond: {disc['isin']}")
                for metric, data in disc["metrics"].items():
                    if not data.get("matches", True):
                        if "error" in data:
                            print(f"   ❌ {metric}: {data['error']}")
                        else:
                            print(f"   ⚠️  {metric}: Local={data['local']:.4f}, API={data['api']:.4f}, Diff={data['difference']:.4f} (tol={data['tolerance']})")
        
        print("="*80)

def main():
    """Main testing function"""
    print("🧪 LOCAL vs API COMPREHENSIVE TESTING")
    print("=====================================")
    
    # Initialize tester
    tester = LocalVsAPITester()
    
    # Define test bonds - you can modify this list
    test_bonds = [
        {
            "isin": "US912810TJ79", 
            "price": 71.66,
            "weighting": 8.09,
            "description": "US TREASURY N/B, 3%, 15-Aug-2052"
        },
        {
            "isin": "XS2249741674",
            "price": 77.88, 
            "weighting": 3.88,
            "description": "GALAXY PIPELINE, 3.25%, 30-Sep-2040"
        },
        {
            "isin": "XS1709535097",
            "price": 89.40,
            "weighting": 4.12,
            "description": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047"
        }
    ]
    
    print(f"📋 Testing {len(test_bonds)} bonds:")
    for bond in test_bonds:
        print(f"   • {bond['isin']} @ {bond['price']} - {bond.get('description', 'Unknown')}")
    
    # Run the test
    result = tester.test_bonds(test_bonds, test_name="Pre-Deploy Validation")
    
    # Print results
    tester.print_comparison_summary(result)
    
    # Save detailed results
    output_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    
    # Return success/failure for scripting
    comparison = result["comparison"]
    if comparison["local_status"] == "success" and comparison["api_status"] == "success":
        if comparison.get("summary", {}).get("discrepancy_count", 0) == 0:
            print("🎉 ALL TESTS PASSED - No discrepancies found!")
            return True
        else:
            print("⚠️  TESTS COMPLETED WITH DISCREPANCIES - Review before deploying")
            return False
    else:
        print("❌ TESTS FAILED - Fix errors before proceeding")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
