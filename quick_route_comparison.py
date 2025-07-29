#!/usr/bin/env python3
"""
Quick Route Comparison Testing Tool
==================================

Lightweight testing tool for rapid debugging of ISIN vs Description route differences.
Perfect for quick validation during development.

Usage:
    python quick_route_comparison.py
    python quick_route_comparison.py --bond US912810TJ79  
    python quick_route_comparison.py --sample 3
"""

import sys
import argparse
import json
from typing import Dict, Any, Optional

# Add project path
PROJECT_ROOT = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10"
sys.path.insert(0, PROJECT_ROOT)

from bond_master_hierarchy import calculate_bond_master

class QuickRouteTester:
    """
    Quick testing for route comparison and convention validation
    """
    
    def __init__(self, settlement_date: str = "2025-06-30"):
        self.settlement_date = settlement_date
        
        # Sample bonds for quick testing - working bonds only
        self.test_bonds = [
            {"isin": "XS2249741674", "name": "GALAXY PIPELINE, 3.25%, 30-Sep-2040", "price": 77.88},
            {"isin": "XS1709535097", "name": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047", "price": 89.40},
            {"isin": "XS1982113463", "name": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039", "price": 87.14},
            {"isin": "USP37466AS18", "name": "EMPRESA METRO, 4.7%, 07-May-2050", "price": 80.39},
            {"isin": "XS1959337749", "name": "QATAR STATE OF, 4.817%, 14-Mar-2049", "price": 89.97},
        ]

    def test_single_bond_routes(self, isin: str, description: str, price: float) -> Dict[str, Any]:
        """
        Test a single bond using both routes and compare results
        """
        print(f"\n🧪 TESTING BOND: {isin}")
        print(f"📝 Description: {description}")
        print(f"💰 Price: ${price}")
        print("=" * 80)
        
        results = {
            "isin": isin,
            "description": description,
            "price": price,
            "isin_route": None,
            "description_route": None,
            "comparison": {}
        }
        
        # Test Route 1: ISIN Hierarchy
        print("\n🔍 Route 1: ISIN Hierarchy (WITH ISIN)")
        print("-" * 50)
        try:
            isin_result = calculate_bond_master(
                isin=isin,
                description=description,
                price=price,
                settlement_date=self.settlement_date
            )
            results["isin_route"] = isin_result
            
            if isin_result.get('success'):
                print(f"✅ SUCCESS - Route: {isin_result.get('route_used', 'Unknown')}")
                print(f"   💹 Yield: {isin_result.get('yield', 'N/A'):.4f}%")
                print(f"   ⏱️  Duration: {isin_result.get('duration', 'N/A'):.4f} years")
                print(f"   📊 Spread: {isin_result.get('spread', 'N/A')} bps")
                print(f"   📅 Day Count: {isin_result.get('day_count_convention', 'N/A')}")
                print(f"   🔄 Frequency: {isin_result.get('frequency', 'N/A')}")
            else:
                print(f"❌ FAILED: {isin_result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            results["isin_route"] = {"success": False, "error": str(e)}
        
        # Test Route 2: Parse Hierarchy
        print("\n🔍 Route 2: Parse Hierarchy (NO ISIN)")
        print("-" * 50)
        try:
            desc_result = calculate_bond_master(
                isin=None,  # Force description parsing
                description=description,
                price=price,
                settlement_date=self.settlement_date
            )
            results["description_route"] = desc_result
            
            if desc_result.get('success'):
                print(f"✅ SUCCESS - Route: {desc_result.get('route_used', 'Unknown')}")
                print(f"   💹 Yield: {desc_result.get('yield', 'N/A'):.4f}%")
                print(f"   ⏱️  Duration: {desc_result.get('duration', 'N/A'):.4f} years")
                print(f"   📊 Spread: {desc_result.get('spread', 'N/A')} bps")
                print(f"   📅 Day Count: {desc_result.get('day_count_convention', 'N/A')}")
                print(f"   🔄 Frequency: {desc_result.get('frequency', 'N/A')}")
            else:
                print(f"❌ FAILED: {desc_result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            results["description_route"] = {"success": False, "error": str(e)}
        
        # Compare Results
        results["comparison"] = self._compare_routes(results["isin_route"], results["description_route"])
        self._print_comparison(results["comparison"])
        
        return results

    def _compare_routes(self, isin_result: Dict, desc_result: Dict) -> Dict[str, Any]:
        """
        Compare results from both routes
        """
        comparison = {
            "both_successful": False,
            "metrics_consistent": False,
            "conventions_match": False,
            "differences": [],
            "convention_differences": []
        }
        
        if not (isin_result and desc_result and 
                isin_result.get('success') and desc_result.get('success')):
            comparison["differences"].append("One or both routes failed")
            return comparison
        
        comparison["both_successful"] = True
        
        # Compare key metrics
        metrics = ['yield', 'duration', 'spread']
        tolerance = 0.01  # 1 basis point
        metrics_match = True
        
        for metric in metrics:
            isin_val = isin_result.get(metric)
            desc_val = desc_result.get(metric)
            
            if isin_val is not None and desc_val is not None:
                diff = abs(isin_val - desc_val)
                if diff > tolerance:
                    metrics_match = False
                    comparison["differences"].append(
                        f"{metric}: ISIN={isin_val:.6f}, DESC={desc_val:.6f} (diff={diff:.6f})"
                    )
        
        comparison["metrics_consistent"] = metrics_match
        
        # Compare conventions
        convention_fields = [
            'day_count_convention',
            'frequency', 
            'calendar',
            'settlement_days',
            'compounding'
        ]
        
        conventions_match = True
        for field in convention_fields:
            isin_conv = isin_result.get(field)
            desc_conv = desc_result.get(field)
            
            if isin_conv != desc_conv:
                conventions_match = False
                comparison["convention_differences"].append(
                    f"{field}: ISIN='{isin_conv}', DESC='{desc_conv}'"
                )
        
        comparison["conventions_match"] = conventions_match
        
        return comparison

    def _print_comparison(self, comparison: Dict[str, Any]):
        """
        Print comparison results in a readable format
        """
        print("\n📊 ROUTE COMPARISON RESULTS")
        print("-" * 50)
        
        if comparison["both_successful"]:
            print("✅ Both routes successful")
            
            if comparison["metrics_consistent"]:
                print("✅ Metrics are consistent between routes")
            else:
                print("❌ METRICS DIFFER between routes:")
                for diff in comparison["differences"]:
                    print(f"   ⚠️  {diff}")
            
            if comparison["conventions_match"]:
                print("✅ Conventions match between routes")
            else:
                print("❌ CONVENTIONS DIFFER between routes:")
                for diff in comparison["convention_differences"]:
                    print(f"   ⚠️  {diff}")
        else:
            print("❌ Route comparison failed:")
            for diff in comparison["differences"]:
                print(f"   • {diff}")

    def test_sample_bonds(self, count: int = 3):
        """
        Test a sample of bonds for quick validation
        """
        print(f"🚀 QUICK SAMPLE TEST - {count} BONDS")
        print("=" * 80)
        
        bonds_to_test = self.test_bonds[:count]
        results = []
        
        for i, bond in enumerate(bonds_to_test, 1):
            print(f"\n📍 Bond {i}/{count}")
            result = self.test_single_bond_routes(
                bond["isin"], 
                bond["name"], 
                bond["price"]
            )
            results.append(result)
        
        # Summary
        print(f"\n🎯 SAMPLE TEST SUMMARY")
        print("=" * 50)
        
        successful_both = sum(1 for r in results if r["comparison"]["both_successful"])
        consistent_metrics = sum(1 for r in results if r["comparison"]["metrics_consistent"])
        matching_conventions = sum(1 for r in results if r["comparison"]["conventions_match"])
        
        print(f"✅ Both routes successful: {successful_both}/{count}")
        print(f"🤝 Consistent metrics: {consistent_metrics}/{count}")
        print(f"⚖️  Matching conventions: {matching_conventions}/{count}")
        
        if successful_both == count and consistent_metrics == count and matching_conventions == count:
            print("\n🎉 ALL TESTS PASSED! Routes are consistent!")
        else:
            print(f"\n⚠️  Issues detected - investigate failing bonds")
        
        return results

    def find_bond_by_isin(self, target_isin: str) -> Optional[Dict]:
        """
        Find a bond in our test set by ISIN
        """
        for bond in self.test_bonds:
            if bond["isin"] == target_isin:
                return bond
        return None

def main():
    """
    Main execution with command line options
    """
    parser = argparse.ArgumentParser(description="Quick Route Comparison Testing")
    parser.add_argument("--bond", help="Test specific bond by ISIN")
    parser.add_argument("--sample", type=int, default=3, help="Test N sample bonds")
    parser.add_argument("--settlement", default="2025-06-30", help="Settlement date")
    
    args = parser.parse_args()
    
    tester = QuickRouteTester(settlement_date=args.settlement)
    
    if args.bond:
        # Test specific bond
        bond_data = tester.find_bond_by_isin(args.bond)
        if bond_data:
            tester.test_single_bond_routes(
                bond_data["isin"],
                bond_data["name"], 
                bond_data["price"]
            )
        else:
            print(f"❌ Bond {args.bond} not found in test set")
            print("Available ISINs:")
            for bond in tester.test_bonds:
                print(f"  • {bond['isin']}: {bond['name'][:50]}...")
    else:
        # Test sample bonds
        tester.test_sample_bonds(args.sample)

if __name__ == "__main__":
    main()
