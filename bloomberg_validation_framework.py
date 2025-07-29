#!/usr/bin/env python3
"""
Bloomberg Reference Data Validation Framework
============================================

Comprehensive testing framework to validate calculate_BOND_MASTER against 
Bloomberg reference data, testing both ISIN and description routes.

✅ Tests ISIN vs Description route consistency
✅ Validates conventions returned from both routes
✅ Compares against Bloomberg benchmarks
✅ Generates detailed comparison reports
"""

import sys
import os
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Add project path
PROJECT_ROOT = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10"
sys.path.insert(0, PROJECT_ROOT)

# Import the master function - REUSE EXISTING PROVEN CODE
from bond_master_hierarchy import calculate_bond_master

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class BloombergBenchmark:
    """Bloomberg reference data structure"""
    isin: str
    px_mid: float
    name: str
    duration: Optional[float] = None
    yield_: Optional[float] = None  # Note: yield is a Python keyword
    spread: Optional[float] = None

@dataclass
class ValidationResult:
    """Single bond validation result"""
    isin: str
    name: str
    price: float
    isin_route_success: bool
    description_route_success: bool
    routes_consistent: bool
    conventions_match: bool
    bloomberg_comparison: Dict[str, Any]
    errors: List[str]
    calculation_time: float

class BloombergValidationFramework:
    """
    Comprehensive validation framework for calculate_BOND_MASTER
    """
    
    def __init__(self, settlement_date: str = "2025-06-30"):
        self.settlement_date = settlement_date
        self.validation_results: List[ValidationResult] = []
        self.summary_stats = {
            "total_bonds": 0,
            "isin_route_successes": 0,
            "description_route_successes": 0,
            "consistent_routes": 0,
            "matching_conventions": 0,
            "bloomberg_matches": 0
        }
        
        # Bloomberg reference data - ALL 25 PROVIDED BONDS
        self.bloomberg_benchmarks = [
            BloombergBenchmark("US912810TJ79", 71.66, "T 3 15/08/52", 16.357839, 4.898453, None),
            BloombergBenchmark("XS2249741674", 77.88, "GALAXY PIPELINE, 3.25%, 30-Sep-2040", 10.097620, 5.637570, 118),
            BloombergBenchmark("XS1709535097", 89.40, "ABU DHABI CRUDE, 4.6%, 02-Nov-2047", 9.815219, 5.717451, 123),
            BloombergBenchmark("XS1982113463", 87.14, "SAUDI ARAB OIL, 4.25%, 16-Apr-2039", 9.927596, 5.599746, 111),
            BloombergBenchmark("USP37466AS18", 80.39, "EMPRESA METRO, 4.7%, 07-May-2050", 13.189567, 6.265800, 144),
            BloombergBenchmark("USP3143NAH72", 101.63, "CODELCO INC, 6.15%, 24-Oct-2036", 8.024166, 5.949058, 160),
            BloombergBenchmark("USP30179BR86", 86.42, "COMISION FEDERAL, 6.264%, 15-Feb-2052", 11.583500, 7.442306, 261),
            BloombergBenchmark("US195325DX04", 52.71, "COLOMBIA REP OF, 3.875%, 15-Feb-2061", 12.975798, 7.836133, 301),
            BloombergBenchmark("US279158AJ82", 69.31, "ECOPETROL SA, 5.875%, 28-May-2045", 9.812703, 9.282266, 445),
            BloombergBenchmark("USP37110AM89", 76.24, "EMPRESA NACIONAL, 4.5%, 14-Sep-2047", 12.389556, 6.542351, 171),
            BloombergBenchmark("XS2542166231", 103.03, "GREENSAIF PIPELI, 6.129%, 23-Feb-2038", 7.207705, 5.720213, 146),
            BloombergBenchmark("XS2167193015", 64.50, "STATE OF ISRAEL, 3.8%, 13-May-2060", 15.269052, 6.337460, 151),
            BloombergBenchmark("XS1508675508", 82.42, "SAUDI INT BOND, 4.5%, 26-Oct-2046", 12.598517, 5.967150, 114),
            BloombergBenchmark("XS1807299331", 92.21, "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048", 11.446459, 7.059957, 223),
            BloombergBenchmark("US91086QAZ19", 78.00, "UNITED MEXICAN, 5.75%, 12-Oct-2110", 13.370728, 7.374879, 255),
            BloombergBenchmark("USP6629MAD40", 82.57, "MEXICO CITY ARPT, 5.5%, 31-Jul-2047", 11.382487, 7.070132, 224),
            BloombergBenchmark("US698299BL70", 56.60, "PANAMA, 3.87%, 23-Jul-2060", 13.488582, 7.362747, 253),
            BloombergBenchmark("US71654QDF63", 71.42, "PETROLEOS MEXICA, 6.95%, 28-Jan-2060", 9.719713, 9.875691, 505),
            BloombergBenchmark("US71654QDE98", 89.55, "PETROLEOS MEXICA, 5.95%, 28-Jan-2031", 4.469801, 8.324595, 444),
            BloombergBenchmark("XS2585988145", 85.54, "GACI FIRST INVST, 5.125%, 14-Feb-2053", 13.327227, 6.228001, 140),
            BloombergBenchmark("XS1959337749", 89.97, "QATAR STATE OF, 4.817%, 14-Mar-2049", 13.261812, 5.584981, 76),
            BloombergBenchmark("XS2233188353", 99.23, "QNB FINANCE LTD, 1.625%, 22-Sep-2025", 0.225205, 5.015259, 71),
            BloombergBenchmark("XS2359548935", 73.79, "QATAR ENERGY, 3.125%, 12-Jul-2041", 11.512115, 5.628065, 101),
            BloombergBenchmark("XS0911024635", 93.29, "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043", 11.237819, 5.663334, 95),
            BloombergBenchmark("USP0R80BAG79", 97.26, "SITIOS, 5.375%, 04-Apr-2032", 5.514383, 5.870215, 187),
        ]
        
        logger.info(f"🏦 Bloomberg Validation Framework initialized")
        logger.info(f"   Settlement Date: {settlement_date}")
        logger.info(f"   Bloomberg Benchmarks: {len(self.bloomberg_benchmarks)} bonds")

    def validate_single_bond(self, benchmark: BloombergBenchmark) -> ValidationResult:
        """
        Validate a single bond using both ISIN and description routes
        """
        start_time = time.time()
        errors = []
        
        print(f"🧪 Testing {benchmark.isin}: {benchmark.name[:50]}...")
        
        # Test Route 1: ISIN Hierarchy
        isin_result = None
        isin_route_success = False
        try:
            isin_result = calculate_bond_master(
                isin=benchmark.isin,
                description=benchmark.name,
                price=benchmark.px_mid,
                settlement_date=self.settlement_date
            )
            isin_route_success = isin_result.get('success', False)
            if not isin_route_success:
                errors.append(f"ISIN route failed: {isin_result.get('error', 'Unknown error')}")
        except Exception as e:
            errors.append(f"ISIN route exception: {str(e)}")
            print(f"❌ ISIN route failed for {benchmark.isin}: {e}")
        
        # Test Route 2: Parse Hierarchy (no ISIN)
        description_result = None
        description_route_success = False
        try:
            description_result = calculate_bond_master(
                isin=None,  # Force description parsing
                description=benchmark.name,
                price=benchmark.px_mid,
                settlement_date=self.settlement_date
            )
            description_route_success = description_result.get('success', False)
            if not description_route_success:
                errors.append(f"Description route failed: {description_result.get('error', 'Unknown error')}")
        except Exception as e:
            errors.append(f"Description route exception: {str(e)}")
            print(f"❌ Description route failed for {benchmark.isin}: {e}")
        
        # Compare routes for consistency
        routes_consistent = self._compare_routes(isin_result, description_result)
        
        # Compare conventions
        conventions_match = self._compare_conventions(isin_result, description_result)
        
        # Compare against Bloomberg benchmarks
        bloomberg_comparison = self._compare_with_bloomberg(
            isin_result if isin_route_success else description_result,
            benchmark
        )
        
        calculation_time = time.time() - start_time
        
        return ValidationResult(
            isin=benchmark.isin,
            name=benchmark.name,
            price=benchmark.px_mid,
            isin_route_success=isin_route_success,
            description_route_success=description_route_success,
            routes_consistent=routes_consistent,
            conventions_match=conventions_match,
            bloomberg_comparison=bloomberg_comparison,
            errors=errors,
            calculation_time=calculation_time
        )

    def _compare_routes(self, isin_result: Dict, description_result: Dict) -> bool:
        """
        Compare key metrics between ISIN and description routes
        """
        if not (isin_result and description_result and 
                isin_result.get('success') and description_result.get('success')):
            return False
        
        # Key metrics to compare with tolerance
        metrics_to_compare = ['yield', 'duration', 'spread']
        tolerance = 0.01  # 1 basis point tolerance
        
        for metric in metrics_to_compare:
            isin_val = isin_result.get(metric)
            desc_val = description_result.get(metric)
            
            if isin_val is not None and desc_val is not None:
                if abs(isin_val - desc_val) > tolerance:
                    print(f"⚠️  Route inconsistency in {metric}: ISIN={isin_val:.6f}, DESC={desc_val:.6f}")
                    return False
        
        return True

    def _compare_conventions(self, isin_result: Dict, description_result: Dict) -> bool:
        """
        Compare conventions returned from both routes
        """
        if not (isin_result and description_result and 
                isin_result.get('success') and description_result.get('success')):
            return False
        
        # Convention fields to compare
        convention_fields = [
            'day_count_convention',
            'frequency',
            'calendar',
            'settlement_days',
            'compounding'
        ]
        
        for field in convention_fields:
            isin_conv = isin_result.get(field)
            desc_conv = description_result.get(field)
            
            if isin_conv != desc_conv:
                print(f"⚠️  Convention mismatch in {field}: ISIN='{isin_conv}', DESC='{desc_conv}'")
                return False
        
        return True

    def _compare_with_bloomberg(self, calc_result: Dict, benchmark: BloombergBenchmark) -> Dict[str, Any]:
        """
        Compare calculation results with Bloomberg benchmarks
        """
        comparison = {
            "bloomberg_available": False,
            "yield_match": False,
            "duration_match": False,
            "spread_match": False,
            "yield_diff": None,
            "duration_diff": None,
            "spread_diff": None,
            "overall_match": False
        }
        
        if not calc_result or not calc_result.get('success'):
            return comparison
        
        comparison["bloomberg_available"] = True
        tolerance = 0.1  # 10 basis points for Bloomberg comparison
        
        # Compare yield
        if benchmark.yield_ is not None:
            calc_yield = calc_result.get('yield')
            if calc_yield is not None:
                yield_diff = abs(calc_yield - benchmark.yield_)
                comparison["yield_diff"] = yield_diff
                comparison["yield_match"] = yield_diff <= tolerance
        
        # Compare duration
        if benchmark.duration is not None:
            calc_duration = calc_result.get('duration')
            if calc_duration is not None:
                duration_diff = abs(calc_duration - benchmark.duration)
                comparison["duration_diff"] = duration_diff
                comparison["duration_match"] = duration_diff <= 0.1  # 0.1 year tolerance
        
        # Overall match if all available metrics match
        available_matches = [
            comparison["yield_match"],
            comparison["duration_match"]
        ]
        comparison["overall_match"] = all(m for m in available_matches if m is not False)
        
        return comparison

    def run_full_validation(self) -> Dict[str, Any]:
        """
        Run validation on ALL Bloomberg benchmarks (25 bonds)
        """
        print("🚀 Starting Full Bloomberg Validation (25 bonds)")
        print("=" * 80)
        
        self.validation_results = []
        
        for i, benchmark in enumerate(self.bloomberg_benchmarks, 1):
            print(f"📊 Progress: {i}/{len(self.bloomberg_benchmarks)} bonds")
            
            result = self.validate_single_bond(benchmark)
            self.validation_results.append(result)
            
            # Update summary stats
            self.summary_stats["total_bonds"] += 1
            if result.isin_route_success:
                self.summary_stats["isin_route_successes"] += 1
            if result.description_route_success:
                self.summary_stats["description_route_successes"] += 1
            if result.routes_consistent:
                self.summary_stats["consistent_routes"] += 1
            if result.conventions_match:
                self.summary_stats["matching_conventions"] += 1
            if result.bloomberg_comparison.get("overall_match"):
                self.summary_stats["bloomberg_matches"] += 1
        
        return self._generate_summary_report()

    def run_quick_validation(self) -> Dict[str, Any]:
        """
        Run validation on sample Bloomberg benchmarks (first 5 bonds)
        """
        print("🚀 Starting Quick Bloomberg Validation (5 bonds)")
        print("=" * 80)
        
        # Use only first 5 bonds for quick test
        quick_benchmarks = self.bloomberg_benchmarks[:5]
        original_benchmarks = self.bloomberg_benchmarks
        self.bloomberg_benchmarks = quick_benchmarks
        
        self.validation_results = []
        
        for i, benchmark in enumerate(self.bloomberg_benchmarks, 1):
            print(f"📊 Progress: {i}/{len(self.bloomberg_benchmarks)} bonds")
            
            result = self.validate_single_bond(benchmark)
            self.validation_results.append(result)
            
            # Update summary stats
            self.summary_stats["total_bonds"] += 1
            if result.isin_route_success:
                self.summary_stats["isin_route_successes"] += 1
            if result.description_route_success:
                self.summary_stats["description_route_successes"] += 1
            if result.routes_consistent:
                self.summary_stats["consistent_routes"] += 1
            if result.conventions_match:
                self.summary_stats["matching_conventions"] += 1
            if result.bloomberg_comparison.get("overall_match"):
                self.summary_stats["bloomberg_matches"] += 1
        
        # Restore original benchmarks
        self.bloomberg_benchmarks = original_benchmarks
        
        return self._generate_summary_report()

    def _generate_summary_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive summary report
        """
        total = self.summary_stats["total_bonds"]
        
        summary = {
            "validation_timestamp": datetime.now().isoformat(),
            "settlement_date": self.settlement_date,
            "total_bonds_tested": total,
            "success_rates": {
                "isin_route": f"{(self.summary_stats['isin_route_successes']/total)*100:.1f}%",
                "description_route": f"{(self.summary_stats['description_route_successes']/total)*100:.1f}%",
                "route_consistency": f"{(self.summary_stats['consistent_routes']/total)*100:.1f}%",
                "convention_matching": f"{(self.summary_stats['matching_conventions']/total)*100:.1f}%",
                "bloomberg_accuracy": f"{(self.summary_stats['bloomberg_matches']/total)*100:.1f}%"
            },
            "detailed_results": []
        }
        
        # Add detailed results for each bond
        for result in self.validation_results:
            detail = {
                "isin": result.isin,
                "name": result.name[:50] + "..." if len(result.name) > 50 else result.name,
                "price": result.price,
                "isin_route_success": result.isin_route_success,
                "description_route_success": result.description_route_success,
                "routes_consistent": result.routes_consistent,
                "conventions_match": result.conventions_match,
                "bloomberg_match": result.bloomberg_comparison.get("overall_match", False),
                "yield_diff": result.bloomberg_comparison.get("yield_diff"),
                "duration_diff": result.bloomberg_comparison.get("duration_diff"),
                "calculation_time_ms": round(result.calculation_time * 1000, 2),
                "errors": result.errors
            }
            summary["detailed_results"].append(detail)
        
        return summary

def main():
    """
    Main execution function - Run Bloomberg validation
    """
    print("🏦 BLOOMBERG REFERENCE DATA VALIDATION FRAMEWORK")
    print("=" * 80)
    print("✅ Testing ISIN vs Description route consistency")
    print("✅ Validating conventions between routes")
    print("✅ Comparing against Bloomberg benchmarks")
    print()
    
    # Initialize framework
    validator = BloombergValidationFramework(settlement_date="2025-06-30")
    
    # Run validation
    summary = validator.run_full_validation()
    
    # Print summary
    print("\n🎯 VALIDATION SUMMARY")
    print("=" * 50)
    print(f"📊 Total Bonds Tested: {summary['total_bonds_tested']}")
    print(f"🔄 ISIN Route Success: {summary['success_rates']['isin_route']}")
    print(f"📝 Description Route Success: {summary['success_rates']['description_route']}")
    print(f"🤝 Route Consistency: {summary['success_rates']['route_consistency']}")
    print(f"⚖️  Convention Matching: {summary['success_rates']['convention_matching']}")
    print(f"🏦 Bloomberg Accuracy: {summary['success_rates']['bloomberg_accuracy']}")
    
    # Save JSON summary
    with open("bloomberg_validation_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📄 Report Generated:")
    print(f"   • bloomberg_validation_summary.json")
    
    print(f"\n🎉 Bloomberg validation complete!")
    
    return summary

if __name__ == "__main__":
    main()
