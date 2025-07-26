#!/usr/bin/env python3
"""
COMPREHENSIVE 6-WAY BOND TESTING FRAMEWORK
==========================================

Tests all bonds against 6 different calculation methods:
1. Direct Local + ISIN (database lookup)
2. Direct Local - ISIN (parser fallback)  
3. Local API + ISIN (API with database)
4. Local API - ISIN (API with parser fallback)
5. Cloud API + ISIN (when deployed)
6. Cloud API - ISIN (cloud fallback)

Plus comparison against Bloomberg actuals for validation.

Stores all results and provides comprehensive comparison analysis.
"""

import sys
import os
import json
import requests
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
import traceback

# Add current directory to path for imports
sys.path.append('.')

# Import the google_analysis10 calculation engine directly
try:
    from google_analysis10 import (
        process_bonds_without_weightings,
        fetch_latest_trade_date,
        fetch_treasury_yields,
        create_treasury_curve,
        parse_date,
        calculate_bond_metrics_using_shared_engine,
        fetch_bond_data_enhanced
    )
    LOCAL_IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Could not import local calculation engine: {e}")
    LOCAL_IMPORTS_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveBondTester:
    """
    6-way comprehensive bond testing framework
    """
    
    def __init__(self, local_api_url="http://localhost:8080", cloud_api_url=None):
        self.local_api_url = local_api_url
        self.cloud_api_url = cloud_api_url
        self.test_results = {}
        self.bloomberg_actuals = {}
        self.test_timestamp = datetime.now().isoformat()
        
        # Test method definitions
        self.test_methods = {
            "direct_local_with_isin": "Direct Local + ISIN",
            "direct_local_without_isin": "Direct Local - ISIN", 
            "local_api_with_isin": "Local API + ISIN",
            "local_api_without_isin": "Local API - ISIN",
            "cloud_api_with_isin": "Cloud API + ISIN",
            "cloud_api_without_isin": "Cloud API - ISIN"
        }
        
        # Database paths - FIXED: Use correct paths
        self.db_path = "./bonds_data.db"  # Database is in current directory
        self.validated_db_path = "./validated_quantlib_bonds.db"
        
        print(f"📁 Main database: {self.db_path} ✅")
        print(f"📁 Validated database: {self.validated_db_path} ✅")
    
    def _find_database(self, db_name):
        """Find database file in current directory or data subdirectory"""
        for path in [f"./{db_name}", f"./data/{db_name}", f"../{db_name}"]:
            if os.path.exists(path):
                return path
        return f"./{db_name}"  # Default fallback
    
    def load_bloomberg_actuals(self, bloomberg_data: Dict):
        """
        Load Bloomberg actual results for comparison
        Expected format: {"ISIN": {"yield": X, "duration": Y, "spread": Z}, ...}
        """
        self.bloomberg_actuals = bloomberg_data
        print(f"📊 Loaded Bloomberg actuals for {len(bloomberg_data)} bonds")
    
    def test_all_bonds(self, bonds_list: List[Dict], settlement_date: Optional[str] = None):
        """
        Test all bonds using all 6 methods
        
        Args:
            bonds_list: List of dicts with 'isin', 'price', optional 'weighting', 'description'
            settlement_date: Optional settlement date override
        """
        print(f"\n🧪 COMPREHENSIVE 6-WAY TESTING: {len(bonds_list)} BONDS")
        print("=" * 80)
        
        for i, bond in enumerate(bonds_list, 1):
            print(f"\n📋 Testing Bond {i}/{len(bonds_list)}: {bond['isin']}")
            print(f"   Price: {bond['price']}, Description: {bond.get('description', 'N/A')}")
            
            bond_results = self._test_single_bond(bond, settlement_date)
            self.test_results[bond['isin']] = bond_results
            
            # Print quick summary for this bond
            self._print_bond_summary(bond['isin'], bond_results)
        
        print(f"\n✅ COMPLETED TESTING ALL {len(bonds_list)} BONDS")
        return self.test_results
    
    def _test_single_bond(self, bond: Dict, settlement_date: Optional[str] = None) -> Dict:
        """Test a single bond using all 6 methods"""
        isin = bond['isin']
        price = bond['price']
        
        bond_results = {
            "bond_info": bond,
            "test_timestamp": datetime.now().isoformat(),
            "settlement_date": settlement_date,
            "results": {},
            "errors": {}
        }
        
        # Test each method
        for method_key, method_name in self.test_methods.items():
            try:
                print(f"   🔧 {method_name}...")
                result = self._execute_test_method(method_key, bond, settlement_date)
                bond_results["results"][method_key] = result
                
                if result.get("status") == "success":
                    metrics = result.get("metrics", {})
                    y = metrics.get('yield') or 0
                    d = metrics.get('duration') or 0  
                    s = metrics.get('spread') or 0
                    print(f"      ✅ Y:{y:6.2f}% D:{d:6.2f}yr S:{s:6.0f}bp")
                else:
                    error = result.get("error", "Unknown error")
                    print(f"      ❌ Failed: {error}")
                    bond_results["errors"][method_key] = error
                    
            except Exception as e:
                error_msg = f"Exception in {method_name}: {str(e)}"
                print(f"      ❌ Exception: {error_msg}")
                bond_results["errors"][method_key] = error_msg
                bond_results["results"][method_key] = {"status": "error", "error": error_msg}
        
        return bond_results
    
    def _execute_test_method(self, method_key: str, bond: Dict, settlement_date: Optional[str] = None) -> Dict:
        """Execute a specific test method"""
        isin = bond['isin']
        price = bond['price']
        
        if method_key == "direct_local_with_isin":
            return self._test_direct_local(bond, use_isin=True, settlement_date=settlement_date)
        elif method_key == "direct_local_without_isin":
            return self._test_direct_local(bond, use_isin=False, settlement_date=settlement_date)
        elif method_key == "local_api_with_isin":
            return self._test_api(self.local_api_url, bond, use_isin=True, settlement_date=settlement_date)
        elif method_key == "local_api_without_isin":
            return self._test_api(self.local_api_url, bond, use_isin=False, settlement_date=settlement_date)
        elif method_key == "cloud_api_with_isin":
            if not self.cloud_api_url:
                return {"status": "skipped", "error": "Cloud API URL not provided"}
            return self._test_api(self.cloud_api_url, bond, use_isin=True, settlement_date=settlement_date)
        elif method_key == "cloud_api_without_isin":
            if not self.cloud_api_url:
                return {"status": "skipped", "error": "Cloud API URL not provided"}
            return self._test_api(self.cloud_api_url, bond, use_isin=False, settlement_date=settlement_date)
        else:
            return {"status": "error", "error": f"Unknown test method: {method_key}"}
    
    def _test_direct_local(self, bond: Dict, use_isin: bool, settlement_date: Optional[str] = None) -> Dict:
        """Test using direct local code calculation"""
        if not LOCAL_IMPORTS_AVAILABLE:
            return {"status": "error", "error": "Local imports not available"}
        
        try:
            # Prepare bond data
            test_data = {
                "CLOSING PRICE": bond['price']
            }
            
            if use_isin:
                test_data["BOND_CD"] = bond['isin']
            else:
                # Test parser fallback - provide description but no ISIN
                if 'description' in bond:
                    test_data["BOND_ENAME"] = bond['description']
                else:
                    # Create a synthetic description for parser testing
                    test_data["BOND_ENAME"] = f"TEST BOND {bond['isin'][:6]} 5.0% 01/01/2030"
            
            if 'weighting' in bond:
                test_data["WEIGHTING"] = bond['weighting']
            
            if settlement_date:
                test_data["settlement_date"] = settlement_date
            
            # Convert to DataFrame and process
            df = pd.DataFrame([test_data])
            
            results_df = process_bonds_without_weightings(
                df, 
                db_path=self.db_path,
                validated_db_path=self.validated_db_path
            )
            
            if isinstance(results_df, pd.DataFrame) and not results_df.empty:
                result_row = results_df.iloc[0].to_dict()
                
                # Extract metrics with multiple possible field names
                metrics = {
                    "yield": self._extract_metric(result_row, ["Yield (%)", "yield", "bond_yield", "YTM"]),
                    "duration": self._extract_metric(result_row, ["Duration (years)", "duration", "bond_duration", "Duration"]),
                    "spread": self._extract_metric(result_row, ["Spread (bps)", "spread", "bond_spread", "Spread"])
                }
                
                return {
                    "status": "success",
                    "metrics": metrics,
                    "raw_result": result_row,
                    "method": "direct_local",
                    "used_isin": use_isin
                }
            else:
                return {"status": "error", "error": "Empty results from direct calculation"}
                
        except Exception as e:
            return {"status": "error", "error": f"Direct calculation failed: {str(e)}"}
    
    def _test_api(self, api_url: str, bond: Dict, use_isin: bool, settlement_date: Optional[str] = None) -> Dict:
        """Test using API call"""
        try:
            # Check API health first
            health_response = requests.get(f"{api_url}/health", timeout=10)
            if health_response.status_code != 200:
                return {"status": "error", "error": f"API health check failed: {health_response.status_code}"}
            
            # Prepare API request data
            api_data = {
                "data": [{}]
            }
            
            bond_data = {"CLOSING PRICE": bond['price']}
            
            if use_isin:
                bond_data["BOND_CD"] = bond['isin']
            else:
                # Test API parser fallback
                if 'description' in bond:
                    bond_data["BOND_ENAME"] = bond['description']
                else:
                    bond_data["BOND_ENAME"] = f"TEST BOND {bond['isin'][:6]} 5.0% 01/01/2030"
            
            if 'weighting' in bond:
                bond_data["WEIGHTING"] = bond['weighting']
            
            api_data["data"][0] = bond_data
            
            if settlement_date:
                api_data["settlement_date"] = settlement_date
            
            # Make API call
            api_endpoint = f"{api_url}/api/v1/portfolio/analyze"
            response = requests.post(
                api_endpoint,
                json=api_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                api_result = response.json()
                
                # Extract bond metrics from API response
                metrics = self._extract_api_metrics(api_result)
                
                return {
                    "status": "success",
                    "metrics": metrics,
                    "raw_result": api_result,
                    "method": "api",
                    "used_isin": use_isin,
                    "api_url": api_url
                }
            else:
                return {
                    "status": "error", 
                    "error": f"API returned {response.status_code}: {response.text}",
                    "api_url": api_url
                }
                
        except Exception as e:
            return {"status": "error", "error": f"API call failed: {str(e)}", "api_url": api_url}
    
    def _extract_metric(self, data: Dict, field_names: List[str]) -> Optional[float]:
        """Extract a metric value trying multiple field names"""
        for field_name in field_names:
            if field_name in data:
                value = data[field_name]
                if value is not None and str(value).strip() != "":
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        continue
        return None
    
    def _extract_api_metrics(self, api_result: Dict) -> Dict:
        """Extract metrics from API response"""
        metrics = {"yield": None, "duration": None, "spread": None}
        
        # Try different API response structures
        if "bond_analytics" in api_result:
            bonds = api_result["bond_analytics"]
        elif "bonds" in api_result:
            bonds = api_result["bonds"]
        elif "results" in api_result:
            bonds = api_result["results"]
        elif isinstance(api_result, list):
            bonds = api_result
        else:
            return metrics
        
        if bonds and len(bonds) > 0:
            bond_data = bonds[0]
            metrics["yield"] = self._extract_metric(bond_data, ["yield", "Yield (%)", "bond_yield", "YTM"])
            metrics["duration"] = self._extract_metric(bond_data, ["duration", "Duration (years)", "bond_duration"])
            metrics["spread"] = self._extract_metric(bond_data, ["spread", "Spread (bps)", "bond_spread"])
        
        return metrics
    
    def _print_bond_summary(self, isin: str, bond_results: Dict):
        """Print quick summary for a single bond"""
        print(f"   📊 Summary for {isin}:")
        
        for method_key, method_name in self.test_methods.items():
            if method_key in bond_results["results"]:
                result = bond_results["results"][method_key]
                if result.get("status") == "success":
                    metrics = result.get("metrics", {})
                    y = metrics.get("yield") or 0
                    d = metrics.get("duration") or 0
                    s = metrics.get("spread") or 0
                    print(f"      {method_name:20}: Y:{y:6.2f}% D:{d:6.2f}yr S:{s:6.0f}bp")
                else:
                    print(f"      {method_name:20}: ❌ {result.get('error', 'Failed')}")
    
    def generate_comprehensive_report(self) -> Dict:
        """Generate comprehensive comparison report"""
        report = {
            "test_summary": {
                "timestamp": self.test_timestamp,
                "total_bonds": len(self.test_results),
                "test_methods": list(self.test_methods.keys()),
                "bloomberg_baseline_available": len(self.bloomberg_actuals) > 0
            },
            "success_rates": {},
            "cross_method_comparison": {},
            "bloomberg_comparison": {},
            "discrepancy_analysis": {}
        }
        
        # Calculate success rates for each method
        for method_key, method_name in self.test_methods.items():
            successful = 0
            total = 0
            for isin, bond_result in self.test_results.items():
                if method_key in bond_result["results"]:
                    total += 1
                    if bond_result["results"][method_key].get("status") == "success":
                        successful += 1
            
            report["success_rates"][method_key] = {
                "name": method_name,
                "successful": successful,
                "total": total,
                "rate": (successful / total * 100) if total > 0 else 0
            }
        
        # Cross-method comparison (compare local vs API, with vs without ISIN)
        report["cross_method_comparison"] = self._analyze_cross_method_discrepancies()
        
        # Bloomberg comparison (if available)
        if self.bloomberg_actuals:
            report["bloomberg_comparison"] = self._analyze_bloomberg_discrepancies()
        
        return report
    
    def _analyze_cross_method_discrepancies(self) -> Dict:
        """Analyze discrepancies between different test methods"""
        comparisons = {
            "local_direct_vs_api": [],
            "with_isin_vs_without_isin": [],
            "local_vs_cloud": []
        }
        
        for isin, bond_result in self.test_results.items():
            results = bond_result["results"]
            
            # Compare local direct vs local API (both with ISIN)
            if ("direct_local_with_isin" in results and 
                "local_api_with_isin" in results and
                results["direct_local_with_isin"].get("status") == "success" and
                results["local_api_with_isin"].get("status") == "success"):
                
                comparison = self._compare_metrics(
                    results["direct_local_with_isin"]["metrics"],
                    results["local_api_with_isin"]["metrics"],
                    isin, "Direct Local", "Local API"
                )
                if comparison["has_discrepancies"]:
                    comparisons["local_direct_vs_api"].append(comparison)
            
            # Compare with ISIN vs without ISIN for local API
            if ("local_api_with_isin" in results and 
                "local_api_without_isin" in results and
                results["local_api_with_isin"].get("status") == "success" and
                results["local_api_without_isin"].get("status") == "success"):
                
                comparison = self._compare_metrics(
                    results["local_api_with_isin"]["metrics"],
                    results["local_api_without_isin"]["metrics"],
                    isin, "With ISIN", "Without ISIN"
                )
                if comparison["has_discrepancies"]:
                    comparisons["with_isin_vs_without_isin"].append(comparison)
        
        return comparisons
    
    def _analyze_bloomberg_discrepancies(self) -> Dict:
        """Analyze discrepancies vs Bloomberg actuals"""
        bloomberg_analysis = {
            "total_comparisons": 0,
            "method_accuracy": {},
            "significant_discrepancies": []
        }
        
        for method_key, method_name in self.test_methods.items():
            accurate_count = 0
            total_count = 0
            
            for isin, bond_result in self.test_results.items():
                if (isin in self.bloomberg_actuals and 
                    method_key in bond_result["results"] and
                    bond_result["results"][method_key].get("status") == "success"):
                    
                    total_count += 1
                    our_metrics = bond_result["results"][method_key]["metrics"]
                    bloomberg_metrics = self.bloomberg_actuals[isin]
                    
                    comparison = self._compare_metrics(
                        our_metrics, bloomberg_metrics, 
                        isin, method_name, "Bloomberg"
                    )
                    
                    if not comparison["has_discrepancies"]:
                        accurate_count += 1
                    else:
                        bloomberg_analysis["significant_discrepancies"].append(comparison)
            
            if total_count > 0:
                bloomberg_analysis["method_accuracy"][method_key] = {
                    "name": method_name,
                    "accurate": accurate_count,
                    "total": total_count,
                    "accuracy_rate": (accurate_count / total_count * 100)
                }
        
        bloomberg_analysis["total_comparisons"] = len([
            isin for isin in self.test_results.keys() 
            if isin in self.bloomberg_actuals
        ])
        
        return bloomberg_analysis
    
    def _compare_metrics(self, metrics1: Dict, metrics2: Dict, isin: str, 
                        label1: str, label2: str) -> Dict:
        """Compare two sets of metrics"""
        comparison = {
            "isin": isin,
            "method1": label1,
            "method2": label2,
            "has_discrepancies": False,
            "metric_comparisons": {}
        }
        
        # Define tolerances
        tolerances = {
            "yield": 0.05,    # 5bp tolerance
            "duration": 0.1,  # 0.1 year tolerance
            "spread": 5.0     # 5bp tolerance
        }
        
        for metric in ["yield", "duration", "spread"]:
            val1 = metrics1.get(metric)
            val2 = metrics2.get(metric)
            
            if val1 is not None and val2 is not None:
                diff = abs(val1 - val2)
                tolerance = tolerances[metric]
                matches = diff <= tolerance
                
                comparison["metric_comparisons"][metric] = {
                    "value1": val1,
                    "value2": val2,
                    "difference": diff,
                    "tolerance": tolerance,
                    "matches": matches
                }
                
                if not matches:
                    comparison["has_discrepancies"] = True
            else:
                comparison["metric_comparisons"][metric] = {
                    "value1": val1,
                    "value2": val2,
                    "matches": False,
                    "error": "Missing data"
                }
                comparison["has_discrepancies"] = True
        
        return comparison
    
    def save_results(self, filename_prefix: str = "bond_test_comprehensive"):
        """Save all results to JSON files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        results_file = f"{filename_prefix}_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        # Save comprehensive report
        report = self.generate_comprehensive_report()
        report_file = f"{filename_prefix}_report_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n💾 Results saved:")
        print(f"   📋 Detailed results: {results_file}")
        print(f"   📊 Comprehensive report: {report_file}")
        
        return results_file, report_file
    
    def print_executive_summary(self):
        """Print executive summary of all tests"""
        report = self.generate_comprehensive_report()
        
        print("\n" + "="*100)
        print("🏆 EXECUTIVE SUMMARY: 6-WAY COMPREHENSIVE BOND TESTING")
        print("="*100)
        
        print(f"\n📊 TEST OVERVIEW:")
        print(f"   • Total Bonds Tested: {report['test_summary']['total_bonds']}")
        print(f"   • Test Methods: {len(report['test_summary']['test_methods'])}")
        print(f"   • Bloomberg Baseline: {'✅ Available' if report['test_summary']['bloomberg_baseline_available'] else '❌ Not Available'}")
        
        print(f"\n📈 SUCCESS RATES BY METHOD:")
        for method_key, data in report["success_rates"].items():
            rate = data["rate"]
            status = "✅" if rate >= 95 else "⚠️" if rate >= 80 else "❌"
            print(f"   {status} {data['name']:25}: {data['successful']:2d}/{data['total']:2d} ({rate:5.1f}%)")
        
        print(f"\n🔍 CROSS-METHOD DISCREPANCIES:")
        cross_comp = report["cross_method_comparison"]
        print(f"   • Direct vs API: {len(cross_comp['local_direct_vs_api'])} discrepancies")
        print(f"   • With vs Without ISIN: {len(cross_comp['with_isin_vs_without_isin'])} discrepancies")
        print(f"   • Local vs Cloud: {len(cross_comp['local_vs_cloud'])} discrepancies")
        
        if report["test_summary"]["bloomberg_baseline_available"]:
            print(f"\n📊 BLOOMBERG ACCURACY:")
            bloomberg_comp = report["bloomberg_comparison"]
            print(f"   • Total Bloomberg Comparisons: {bloomberg_comp['total_comparisons']}")
            for method_key, data in bloomberg_comp["method_accuracy"].items():
                accuracy = data["accuracy_rate"]
                status = "✅" if accuracy >= 95 else "⚠️" if accuracy >= 80 else "❌"
                print(f"   {status} {data['name']:25}: {accuracy:5.1f}% accurate vs Bloomberg")
        
        # Recommendation
        print(f"\n🎯 DEPLOYMENT RECOMMENDATION:")
        success_rates = [data["rate"] for data in report["success_rates"].values()]
        avg_success = sum(success_rates) / len(success_rates) if success_rates else 0
        discrepancy_count = (len(cross_comp['local_direct_vs_api']) + 
                           len(cross_comp['with_isin_vs_without_isin']))
        
        if avg_success >= 95 and discrepancy_count <= 2:
            print("   ✅ READY FOR CLOUD DEPLOYMENT - Excellent consistency")
        elif avg_success >= 80 and discrepancy_count <= 5:
            print("   ⚠️  PROCEED WITH CAUTION - Monitor cloud results closely")
        else:
            print("   ❌ FIX ISSUES BEFORE DEPLOYMENT - Significant discrepancies found")
        
        print("="*100)

def main():
    """Main testing function"""
    print("🧪 COMPREHENSIVE 6-WAY BOND TESTING FRAMEWORK")
    print("============================================")
    
    # You need to provide the 25 bond list here
    # Format: [{"isin": "...", "price": ..., "weighting": ..., "description": "..."}, ...]
    
    # ACTUAL 25-BOND PORTFOLIO WITH CORRECTED BASELINE DATA
    bonds_to_test = [
        {"isin": "US912810TJ79", "price": 71.66, "description": "US TREASURY N/B, 3%, 15-Aug-2052"},
        {"isin": "XS2249741674", "price": 77.88, "description": "GALAXY PIPELINE, 3.25%, 30-Sep-2040"},
        {"isin": "XS1709535097", "price": 89.40, "description": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047"},
        {"isin": "XS1982113463", "price": 87.14, "description": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039"},
        {"isin": "USP37466AS18", "price": 80.39, "description": "EMPRESA METRO, 4.7%, 07-May-2050"},
        {"isin": "USP3143NAH72", "price": 101.63, "description": "CODELCO INC, 6.15%, 24-Oct-2036"},
        {"isin": "USP30179BR86", "price": 86.42, "description": "COMISION FEDERAL, 6.264%, 15-Feb-2052"},
        {"isin": "US195325DX04", "price": 52.71, "description": "COLOMBIA REP OF, 3.875%, 15-Feb-2061"},
        {"isin": "US279158AJ82", "price": 69.31, "description": "ECOPETROL SA, 5.875%, 28-May-2045"},
        {"isin": "USP37110AM89", "price": 76.24, "description": "EMPRESA NACIONAL, 4.5%, 14-Sep-2047"},
        {"isin": "XS2542166231", "price": 103.03, "description": "GREENSAIF PIPELI, 6.129%, 23-Feb-2038"},
        {"isin": "XS2167193015", "price": 64.50, "description": "STATE OF ISRAEL, 3.8%, 13-May-2060"},
        {"isin": "XS1508675508", "price": 82.42, "description": "SAUDI INT BOND, 4.5%, 26-Oct-2046"},
        {"isin": "XS1807299331", "price": 92.21, "description": "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048"},
        {"isin": "US91086QAZ19", "price": 78.00, "description": "UNITED MEXICAN, 5.75%, 12-Oct-2110"},
        {"isin": "USP6629MAD40", "price": 82.57, "description": "MEXICO CITY ARPT, 5.5%, 31-Jul-2047"},
        {"isin": "US698299BL70", "price": 56.60, "description": "PANAMA, 3.87%, 23-Jul-2060"},
        {"isin": "US71654QDF63", "price": 71.42, "description": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060"},
        {"isin": "US71654QDE98", "price": 89.55, "description": "PETROLEOS MEXICA, 5.95%, 28-Jan-2031"},
        {"isin": "XS2585988145", "price": 85.54, "description": "GACI FIRST INVST, 5.125%, 14-Feb-2053"},
        {"isin": "XS1959337749", "price": 89.97, "description": "QATAR STATE OF, 4.817%, 14-Mar-2049"},
        {"isin": "XS2233188353", "price": 99.23, "description": "QNB FINANCE LTD, 1.625%, 22-Sep-2025"},
        {"isin": "XS2359548935", "price": 73.79, "description": "QATAR ENERGY, 3.125%, 12-Jul-2041"},
        {"isin": "XS0911024635", "price": 93.29, "description": "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043"},
        {"isin": "USP0R80BAG79", "price": 97.26, "description": "SITIOS, 5.375%, 04-Apr-2032"}
    ]
    
    # Load your corrected Bloomberg baseline data
    bloomberg_actuals = {
        "US912810TJ79": {"yield": 4.90, "duration": 16.36, "spread": 0},
        "XS2249741674": {"yield": 5.64, "duration": 10.10, "spread": 118},
        "XS1709535097": {"yield": 5.72, "duration": 9.82, "spread": 123},
        "XS1982113463": {"yield": 5.60, "duration": 9.93, "spread": 111},
        "USP37466AS18": {"yield": 6.27, "duration": 13.19, "spread": 144},
        "USP3143NAH72": {"yield": 5.95, "duration": 8.02, "spread": 160},
        "USP30179BR86": {"yield": 7.44, "duration": 11.58, "spread": 261},
        "US195325DX04": {"yield": 7.84, "duration": 12.98, "spread": 301},
        "US279158AJ82": {"yield": 9.28, "duration": 9.81, "spread": 445},
        "USP37110AM89": {"yield": 6.54, "duration": 12.39, "spread": 171},
        "XS2542166231": {"yield": 5.72, "duration": 7.21, "spread": 146},
        "XS2167193015": {"yield": 6.34, "duration": 15.27, "spread": 151},
        "XS1508675508": {"yield": 5.97, "duration": 12.60, "spread": 114},
        "XS1807299331": {"yield": 7.06, "duration": 11.45, "spread": 223},
        "US91086QAZ19": {"yield": 7.37, "duration": 13.37, "spread": 255},
        "USP6629MAD40": {"yield": 7.07, "duration": 11.38, "spread": 224},
        "US698299BL70": {"yield": 7.36, "duration": 13.49, "spread": 253},
        "US71654QDF63": {"yield": 9.88, "duration": 9.72, "spread": 505},
        "US71654QDE98": {"yield": 8.32, "duration": 4.47, "spread": 444},
        "XS2585988145": {"yield": 6.23, "duration": 13.33, "spread": 140},
        "XS1959337749": {"yield": 5.58, "duration": 13.26, "spread": 76},
        "XS2233188353": {"yield": 5.02, "duration": 0.23, "spread": 71},
        "XS2359548935": {"yield": 5.63, "duration": 11.51, "spread": 101},
        "XS0911024635": {"yield": 5.66, "duration": 11.24, "spread": 95},
        "USP0R80BAG79": {"yield": 5.87, "duration": 5.51, "spread": 187}
    }
    
    print("✅ TESTING 25-BOND PORTFOLIO AGAINST BLOOMBERG BASELINES")
    print(f"   Settlement Date: 2025-06-30 (Corrected)")
    print(f"   Total Bonds: {len(bonds_to_test)}")
    print(f"   Bloomberg Baselines: {len(bloomberg_actuals)} bonds")
    print("=" * 80)
    
    # Initialize tester
    tester = ComprehensiveBondTester(
        local_api_url="http://localhost:8080",
        cloud_api_url=None  # Set when cloud is deployed
    )
    
    tester.load_bloomberg_actuals(bloomberg_actuals)
    
    # Run comprehensive tests
    print(f"\n🚀 Starting comprehensive testing of {len(bonds_to_test)} bonds...")
    results = tester.test_all_bonds(bonds_to_test)
    
    # Generate and save reports
    results_file, report_file = tester.save_results()
    
    # Print executive summary
    tester.print_executive_summary()
    
    return tester

if __name__ == "__main__":
    tester = main()
