#!/usr/bin/env python3
"""
Bond Diagnostic Script - ISIN vs Description Analysis
==================================================

Comprehensive diagnostic tool to identify discrepancies between:
1. ISIN-based parsing vs Description-based parsing
2. API responses vs Direct calculate_bond_master calls
3. Universal Parser vs Legacy parser outputs

Usage:
    python bond_diagnostic.py "US912810TJ79" --price 99.5
    python bond_diagnostic.py "T 4.625 02/15/25" --price 99.5
    python bond_diagnostic.py --test-both "US912810TJ79" "T 4.625 02/15/25"

This will help identify where the fractional yield differences originate.
"""

import sys
import json
import requests
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import argparse
from dataclasses import dataclass, asdict

# Add google_analysis10 path
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DiagnosticResult:
    """Structure for diagnostic test results"""
    input_value: str
    input_type: str
    method: str
    parsing_success: bool
    conventions: Dict[str, Any]
    calculations: Dict[str, Any]
    error: Optional[str] = None
    raw_response: Optional[Dict] = None

class BondDiagnosticTester:
    """Comprehensive bond calculation diagnostic tool"""
    
    def __init__(self):
        self.api_base_url = "https://future-footing-414610.uc.r.appspot.com"
        self.api_key = "gax10_demo_3j5h8m9k2p6r4t7w1q"
        self.results = []
        
        # Import required modules
        try:
            from core.universal_bond_parser import UniversalBondParser, BondSpecification
            from calculate_bond_master import process_bond_portfolio
            from bond_master_hierarchy import calculate_bond_master
            
            self.universal_parser = UniversalBondParser(
                './bonds_data.db',
                './validated_quantlib_bonds.db', 
                './bloomberg_index.db'
            )
            self.imports_successful = True
            logger.info("✅ Successfully imported all required modules")
            
        except ImportError as e:
            logger.error(f"❌ Failed to import modules: {e}")
            self.imports_successful = False
    
    def test_api_individual_bond(self, bond_input: str, price: float) -> DiagnosticResult:
        """Test API individual bond endpoint"""
        try:
            url = f"{self.api_base_url}/api/v1/bond/parse-and-calculate"
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": self.api_key
            }
            
            # Determine if input is ISIN or description
            is_isin = len(bond_input) == 12 and bond_input[:2].isalpha()
            
            payload = {
                "description" if not is_isin else "isin": bond_input,
                "price": price
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract key information
            conventions = {}
            calculations = {}
            
            if "bond" in data:
                bond_data = data["bond"]
                conventions = {
                    "day_count": bond_data.get("day_count"),
                    "frequency": bond_data.get("frequency"), 
                    "business_convention": bond_data.get("business_convention"),
                    "currency": bond_data.get("currency"),
                    "country": bond_data.get("country"),
                    "maturity_date": bond_data.get("maturity_date"),
                    "coupon_rate": bond_data.get("coupon_rate")
                }
                
                if "analytics" in bond_data:
                    analytics = bond_data["analytics"]
                    calculations = {
                        "yield_to_maturity": analytics.get("yield_to_maturity"),
                        "modified_duration": analytics.get("modified_duration"),
                        "convexity": analytics.get("convexity"),
                        "dv01": analytics.get("dv01"),
                        "accrued_interest": analytics.get("accrued_interest")
                    }
            
            return DiagnosticResult(
                input_value=bond_input,
                input_type="ISIN" if is_isin else "Description",
                method="API Individual Bond",
                parsing_success=True,
                conventions=conventions,
                calculations=calculations,
                raw_response=data
            )
            
        except Exception as e:
            logger.error(f"API individual bond test failed: {e}")
            return DiagnosticResult(
                input_value=bond_input,
                input_type="ISIN" if len(bond_input) == 12 else "Description", 
                method="API Individual Bond",
                parsing_success=False,
                conventions={},
                calculations={},
                error=str(e)
            )
    
    def test_api_portfolio(self, bond_input: str, price: float) -> DiagnosticResult:
        """Test API portfolio endpoint"""
        try:
            url = f"{self.api_base_url}/api/v1/portfolio/analyze"
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": self.api_key
            }
            
            # Create portfolio format
            payload = {
                "data": [{
                    "description": bond_input,
                    "CLOSING PRICE": price,
                    "WEIGHTING": 100.0
                }]
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract portfolio results
            conventions = {}
            calculations = {}
            
            if "portfolio" in data and "bonds" in data["portfolio"]:
                bonds = data["portfolio"]["bonds"]
                if bonds:
                    bond = bonds[0]  # First bond
                    conventions = {
                        "day_count": bond.get("day_count"),
                        "frequency": bond.get("frequency"),
                        "business_convention": bond.get("business_convention"),
                        "currency": bond.get("currency"),
                        "country": bond.get("country"),
                        "maturity_date": bond.get("maturity_date"),
                        "coupon_rate": bond.get("coupon_rate")
                    }
                    calculations = {
                        "yield_to_maturity": bond.get("yield_to_maturity"),
                        "modified_duration": bond.get("modified_duration"),
                        "convexity": bond.get("convexity"),
                        "dv01": bond.get("dv01"),
                        "accrued_interest": bond.get("accrued_interest")
                    }
            
            return DiagnosticResult(
                input_value=bond_input,
                input_type="Portfolio",
                method="API Portfolio",
                parsing_success=True,
                conventions=conventions,
                calculations=calculations,
                raw_response=data
            )
            
        except Exception as e:
            logger.error(f"API portfolio test failed: {e}")
            return DiagnosticResult(
                input_value=bond_input,
                input_type="Portfolio",
                method="API Portfolio",
                parsing_success=False,
                conventions={},
                calculations={},
                error=str(e)
            )
    
    def test_universal_parser(self, bond_input: str) -> DiagnosticResult:
        """Test Universal Parser directly"""
        if not self.imports_successful:
            return DiagnosticResult(
                input_value=bond_input,
                input_type="Unknown",
                method="Universal Parser",
                parsing_success=False,
                conventions={},
                calculations={},
                error="Module imports failed"
            )
        
        try:
            # Parse bond with Universal Parser
            bond_spec = self.universal_parser.parse_bond(bond_input)
            
            conventions = {
                "day_count": bond_spec.day_count,
                "frequency": bond_spec.frequency,
                "business_convention": bond_spec.business_convention,
                "currency": bond_spec.currency,
                "country": bond_spec.country,
                "maturity_date": bond_spec.maturity_date,
                "coupon_rate": bond_spec.coupon_rate,
                "issuer": bond_spec.issuer,
                "isin": bond_spec.isin,
                "description": bond_spec.description
            }
            
            return DiagnosticResult(
                input_value=bond_input,
                input_type=bond_spec.input_type.value if hasattr(bond_spec, 'input_type') else "Unknown",
                method="Universal Parser",
                parsing_success=bond_spec.parsing_success if hasattr(bond_spec, 'parsing_success') else True,
                conventions=conventions,
                calculations={},  # Parser doesn't calculate, only parses
                raw_response=asdict(bond_spec)
            )
            
        except Exception as e:
            logger.error(f"Universal Parser test failed: {e}")
            return DiagnosticResult(
                input_value=bond_input,
                input_type="Unknown",
                method="Universal Parser",
                parsing_success=False,
                conventions={},
                calculations={},
                error=str(e)
            )
    
    def test_direct_calculate_bond_master(self, bond_input: str, price: float) -> DiagnosticResult:
        """Test direct calculate_bond_master function"""
        if not self.imports_successful:
            return DiagnosticResult(
                input_value=bond_input,
                input_type="Unknown",
                method="Direct calculate_bond_master",
                parsing_success=False,
                conventions={},
                calculations={},
                error="Module imports failed"
            )
        
        try:
            from bond_master_hierarchy import calculate_bond_master
            
            # Create test portfolio for calculate_bond_master
            portfolio_data = [{
                "description": bond_input,
                "price": price,
                "weighting": 100.0
            }]
            
            results = calculate_bond_master(portfolio_data)
            
            if results and len(results) > 0:
                bond_result = results[0]
                
                conventions = {
                    "day_count": bond_result.get("day_count"),
                    "frequency": bond_result.get("frequency"),
                    "business_convention": bond_result.get("business_convention"),
                    "currency": bond_result.get("currency"),
                    "country": bond_result.get("country"),
                    "maturity_date": bond_result.get("maturity_date"),
                    "coupon_rate": bond_result.get("coupon_rate")
                }
                
                calculations = {
                    "yield_to_maturity": bond_result.get("yield_to_maturity"),
                    "modified_duration": bond_result.get("modified_duration"),
                    "convexity": bond_result.get("convexity"),
                    "dv01": bond_result.get("dv01"),
                    "accrued_interest": bond_result.get("accrued_interest")
                }
                
                return DiagnosticResult(
                    input_value=bond_input,
                    input_type="Direct",
                    method="Direct calculate_bond_master",
                    parsing_success=True,
                    conventions=conventions,
                    calculations=calculations,
                    raw_response=bond_result
                )
            else:
                return DiagnosticResult(
                    input_value=bond_input,
                    input_type="Direct",
                    method="Direct calculate_bond_master",
                    parsing_success=False,
                    conventions={},
                    calculations={},
                    error="No results returned"
                )
            
        except Exception as e:
            logger.error(f"Direct calculate_bond_master test failed: {e}")
            return DiagnosticResult(
                input_value=bond_input,
                input_type="Direct", 
                method="Direct calculate_bond_master",
                parsing_success=False,
                conventions={},
                calculations={},
                error=str(e)
            )
    
    def run_comprehensive_test(self, bond_input: str, price: float = 99.5) -> Tuple[List[DiagnosticResult], Dict[str, Any]]:
        """Run all diagnostic tests for a single bond input"""
        logger.info(f"🔍 Running comprehensive diagnostic for: {bond_input} at price {price}")
        
        test_results = []
        
        # Test 1: Universal Parser (parsing only)
        logger.info("Testing Universal Parser...")
        result1 = self.test_universal_parser(bond_input)
        test_results.append(result1)
        
        # Test 2: API Individual Bond
        logger.info("Testing API Individual Bond...")
        result2 = self.test_api_individual_bond(bond_input, price)
        test_results.append(result2)
        
        # Test 3: API Portfolio 
        logger.info("Testing API Portfolio...")
        result3 = self.test_api_portfolio(bond_input, price)
        test_results.append(result3)
        
        # Test 4: Direct calculate_bond_master
        logger.info("Testing Direct calculate_bond_master...")
        result4 = self.test_direct_calculate_bond_master(bond_input, price)
        test_results.append(result4)
        
        self.results.extend(test_results)
        
        # Compare results
        comparison = self.compare_results(test_results)
        
        return test_results, comparison
    
    def compare_results(self, results: List[DiagnosticResult]) -> Dict[str, Any]:
        """Compare results and identify discrepancies"""
        comparison = {
            "input_value": results[0].input_value if results else "Unknown",
            "total_tests": len(results),
            "successful_tests": sum(1 for r in results if r.parsing_success),
            "discrepancies": {
                "conventions": {},
                "calculations": {}
            },
            "detailed_comparison": {}
        }
        
        # Compare conventions across all successful results
        convention_keys = set()
        calculation_keys = set()
        
        for result in results:
            if result.parsing_success:
                convention_keys.update(result.conventions.keys())
                calculation_keys.update(result.calculations.keys())
        
        # Check for convention discrepancies
        for key in convention_keys:
            values = {}
            for result in results:
                if result.parsing_success and key in result.conventions:
                    method = result.method
                    value = result.conventions[key]
                    if value is not None:
                        values[method] = value
            
            if len(set(str(v) for v in values.values())) > 1:  # Different values found
                comparison["discrepancies"]["conventions"][key] = values
        
        # Check for calculation discrepancies
        for key in calculation_keys:
            values = {}
            for result in results:
                if result.parsing_success and key in result.calculations:
                    method = result.method
                    value = result.calculations[key]
                    if value is not None:
                        values[method] = value
            
            if len(set(str(v) for v in values.values())) > 1:  # Different values found
                comparison["discrepancies"]["calculations"][key] = values
        
        # Store detailed results
        for result in results:
            comparison["detailed_comparison"][result.method] = {
                "success": result.parsing_success,
                "input_type": result.input_type,
                "conventions": result.conventions,
                "calculations": result.calculations,
                "error": result.error
            }
        
        return comparison
    
    def print_diagnostic_report(self, bond_input: str, results: List[DiagnosticResult], comparison: Dict[str, Any]):
        """Print comprehensive diagnostic report"""
        print(f"\n{'='*80}")
        print(f"🔬 BOND DIAGNOSTIC REPORT")
        print(f"{'='*80}")
        print(f"📊 Input: {bond_input}")
        print(f"📈 Tests Run: {comparison['total_tests']}")
        print(f"✅ Successful: {comparison['successful_tests']}")
        print(f"❌ Failed: {comparison['total_tests'] - comparison['successful_tests']}")
        
        # Convention discrepancies
        if comparison["discrepancies"]["conventions"]:
            print(f"\n⚠️  CONVENTION DISCREPANCIES FOUND:")
            for key, values in comparison["discrepancies"]["conventions"].items():
                print(f"   🔍 {key}:")
                for method, value in values.items():
                    print(f"      {method}: {value}")
        
        # Calculation discrepancies  
        if comparison["discrepancies"]["calculations"]:
            print(f"\n⚠️  CALCULATION DISCREPANCIES FOUND:")
            for key, values in comparison["discrepancies"]["calculations"].items():
                print(f"   🔍 {key}:")
                for method, value in values.items():
                    print(f"      {method}: {value}")
        
        # Individual test results
        print(f"\n📋 DETAILED TEST RESULTS:")
        for result in results:
            status = "✅ SUCCESS" if result.parsing_success else "❌ FAILED"
            print(f"\n   {status} - {result.method} ({result.input_type})")
            
            if result.parsing_success:
                # Show key conventions
                key_conventions = ["day_count", "frequency", "coupon_rate", "maturity_date"]
                print(f"      Conventions:")
                for key in key_conventions:
                    if key in result.conventions and result.conventions[key] is not None:
                        print(f"        {key}: {result.conventions[key]}")
                
                # Show key calculations
                key_calculations = ["yield_to_maturity", "modified_duration", "convexity"]
                if any(key in result.calculations for key in key_calculations):
                    print(f"      Calculations:")
                    for key in key_calculations:
                        if key in result.calculations and result.calculations[key] is not None:
                            print(f"        {key}: {result.calculations[key]}")
            else:
                print(f"      Error: {result.error}")
        
        print(f"\n{'='*80}")
    
    def save_results_json(self, filename: str = None):
        """Save all results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bond_diagnostic_results_{timestamp}.json"
        
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(self.results),
            "results": [asdict(result) for result in self.results]
        }
        
        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)
        
        logger.info(f"💾 Results saved to: {filename}")
        return filename

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="Bond Diagnostic Tool - ISIN vs Description Analysis")
    parser.add_argument("bond_input", help="Bond ISIN or description to test")
    parser.add_argument("--price", type=float, default=99.5, help="Bond price for calculations (default: 99.5)")
    parser.add_argument("--compare", help="Second bond input to compare against")
    parser.add_argument("--output", help="Output file for JSON results")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize diagnostic tester
    tester = BondDiagnosticTester()
    
    # Test primary bond input
    logger.info(f"🚀 Starting diagnostic analysis...")
    results1, comparison1 = tester.run_comprehensive_test(args.bond_input, args.price)
    tester.print_diagnostic_report(args.bond_input, results1, comparison1)
    
    # Test comparison bond if provided
    if args.compare:
        logger.info(f"\n🔄 Running comparison analysis...")
        results2, comparison2 = tester.run_comprehensive_test(args.compare, args.price)
        tester.print_diagnostic_report(args.compare, results2, comparison2)
        
        # Cross-comparison between the two bonds
        print(f"\n🔍 CROSS-BOND COMPARISON:")
        print(f"Bond 1: {args.bond_input}")
        print(f"Bond 2: {args.compare}")
        
        # Compare same methods across different bonds
        for method in ["API Individual Bond", "Direct calculate_bond_master"]:
            bond1_result = next((r for r in results1 if r.method == method and r.parsing_success), None)
            bond2_result = next((r for r in results2 if r.method == method and r.parsing_success), None)
            
            if bond1_result and bond2_result:
                print(f"\n   {method}:")
                for key in ["yield_to_maturity", "modified_duration", "convexity"]:
                    val1 = bond1_result.calculations.get(key)
                    val2 = bond2_result.calculations.get(key)
                    if val1 is not None and val2 is not None:
                        diff = abs(float(val1) - float(val2)) if val1 != val2 else 0
                        print(f"     {key}: {val1} vs {val2} (diff: {diff:.6f})")
    
    # Save results
    output_file = args.output if args.output else None
    filename = tester.save_results_json(output_file)
    
    print(f"\n🎯 DIAGNOSTIC COMPLETE")
    print(f"📁 Results saved to: {filename}")
    
    # Summary recommendation
    total_discrepancies = len(comparison1["discrepancies"]["conventions"]) + len(comparison1["discrepancies"]["calculations"])
    if total_discrepancies > 0:
        print(f"⚠️  Found {total_discrepancies} discrepancies - investigate parsing logic!")
    else:
        print(f"✅ No discrepancies found - calculations are consistent!")

if __name__ == "__main__":
    main()
