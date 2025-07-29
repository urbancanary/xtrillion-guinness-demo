#!/usr/bin/env python3
"""
Route Comparison Debugger
=========================

This script tests both ISIN and description routes for the same bond
to identify convention differences that cause yield discrepancies.

If conventions were truly identical, yields should match exactly.
Any differences indicate convention mismatches between routes.
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

class RouteComparisonDebugger:
    def __init__(self, api_url: str = "http://localhost:8080"):
        self.api_url = api_url.rstrip('/')
        self.api_key = "gax10_demo_3j5h8m9k2p6r4t7w1q"
        
    def test_bond_routes(self, isin: str, description: str, price: float) -> Dict[str, Any]:
        """Test both ISIN and description routes for the same bond"""
        
        print(f"\n{'='*80}")
        print(f"🔬 ROUTE COMPARISON ANALYSIS")
        print(f"{'='*80}")
        print(f"ISIN: {isin}")
        print(f"Description: {description}")
        print(f"Price: {price}")
        print(f"{'='*80}")
        
        results = {
            "bond_info": {
                "isin": isin,
                "description": description,
                "price": price
            },
            "isin_route": self._test_isin_route(isin, price),
            "description_route": self._test_description_route(description, price),
            "comparison": {}
        }
        
        # Compare results
        results["comparison"] = self._compare_routes(
            results["isin_route"], 
            results["description_route"]
        )
        
        return results
    
    def _test_isin_route(self, isin: str, price: float) -> Dict[str, Any]:
        """Test ISIN route"""
        print(f"\n📋 TESTING ISIN ROUTE")
        print(f"   Input: ISIN={isin}, Price={price}")
        
        try:
            # Test individual bond endpoint with ISIN
            response = requests.post(
                f"{self.api_url}/api/v1/bond/parse-and-calculate",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key
                },
                json={
                    "isin": isin,
                    "price": price
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    "status": "success",
                    "response": data,
                    "yield": self._extract_yield(data),
                    "duration": self._extract_duration(data),
                    "conventions": self._extract_conventions(data),
                    "accrued": self._extract_accrued(data)
                }
                print(f"   ✅ Success: Yield={result['yield']:.6f}%")
                return result
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print(f"   ❌ Failed: {error_msg}")
                return {"status": "failed", "error": error_msg}
                
        except Exception as e:
            error_msg = f"Exception: {str(e)}"
            print(f"   ❌ Exception: {error_msg}")
            return {"status": "failed", "error": error_msg}
    
    def _test_description_route(self, description: str, price: float) -> Dict[str, Any]:
        """Test description route"""
        print(f"\n📝 TESTING DESCRIPTION ROUTE")
        print(f"   Input: Description='{description}', Price={price}")
        
        try:
            # Test individual bond endpoint with description
            response = requests.post(
                f"{self.api_url}/api/v1/bond/parse-and-calculate",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key
                },
                json={
                    "description": description,
                    "price": price
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    "status": "success",
                    "response": data,
                    "yield": self._extract_yield(data),
                    "duration": self._extract_duration(data),
                    "conventions": self._extract_conventions(data),
                    "accrued": self._extract_accrued(data)
                }
                print(f"   ✅ Success: Yield={result['yield']:.6f}%")
                return result
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print(f"   ❌ Failed: {error_msg}")
                return {"status": "failed", "error": error_msg}
                
        except Exception as e:
            error_msg = f"Exception: {str(e)}"
            print(f"   ❌ Exception: {error_msg}")
            return {"status": "failed", "error": error_msg}
    
    def _extract_yield(self, data: Dict) -> Optional[float]:
        """Extract yield from API response"""
        try:
            return float(data.get("bond", {}).get("analytics", {}).get("yield", 0))
        except:
            return None
    
    def _extract_duration(self, data: Dict) -> Optional[float]:
        """Extract duration from API response"""
        try:
            return float(data.get("bond", {}).get("analytics", {}).get("duration", 0))
        except:
            return None
    
    def _extract_conventions(self, data: Dict) -> Dict[str, Any]:
        """Extract conventions from API response"""
        try:
            bond_data = data.get("bond", {})
            return {
                "day_count": bond_data.get("day_count"),
                "frequency": bond_data.get("frequency"),
                "business_convention": bond_data.get("business_convention"),
                "parsing_method": bond_data.get("parsing_method"),
                "conventions_source": bond_data.get("conventions_source")
            }
        except:
            return {}
    
    def _extract_accrued(self, data: Dict) -> Optional[float]:
        """Extract accrued interest from API response"""
        try:
            return float(data.get("bond", {}).get("analytics", {}).get("accrued_interest", 0))
        except:
            return None
    
    def _compare_routes(self, isin_result: Dict, desc_result: Dict) -> Dict[str, Any]:
        """Compare results from both routes"""
        print(f"\n🔍 ROUTE COMPARISON")
        print(f"{'='*80}")
        
        comparison = {
            "both_successful": False,
            "yield_difference": None,
            "duration_difference": None,
            "accrued_difference": None,
            "convention_differences": [],
            "identical_results": False
        }
        
        if (isin_result.get("status") == "success" and 
            desc_result.get("status") == "success"):
            
            comparison["both_successful"] = True
            
            # Compare yields
            isin_yield = isin_result.get("yield")
            desc_yield = desc_result.get("yield")
            
            if isin_yield is not None and desc_yield is not None:
                yield_diff = abs(isin_yield - desc_yield)
                comparison["yield_difference"] = yield_diff
                
                print(f"📊 YIELD COMPARISON:")
                print(f"   ISIN Route:        {isin_yield:.8f}%")
                print(f"   Description Route: {desc_yield:.8f}%")
                print(f"   Absolute Diff:     {yield_diff:.8f}%")
                print(f"   Diff in bp:        {yield_diff*100:.4f} bp")
                
                if yield_diff < 0.000001:  # 0.0001 bp tolerance
                    print(f"   ✅ IDENTICAL (diff < 0.0001 bp)")
                    comparison["identical_results"] = True
                elif yield_diff < 0.001:   # 0.1 bp tolerance
                    print(f"   ⚠️  VERY CLOSE (diff < 0.1 bp)")
                elif yield_diff < 0.01:    # 1 bp tolerance
                    print(f"   ⚠️  CLOSE (diff < 1 bp)")
                else:
                    print(f"   ❌ SIGNIFICANT DIFFERENCE (diff >= 1 bp)")
            
            # Compare durations
            isin_duration = isin_result.get("duration")
            desc_duration = desc_result.get("duration")
            
            if isin_duration is not None and desc_duration is not None:
                duration_diff = abs(isin_duration - desc_duration)
                comparison["duration_difference"] = duration_diff
                
                print(f"\n📏 DURATION COMPARISON:")
                print(f"   ISIN Route:        {isin_duration:.6f}")
                print(f"   Description Route: {desc_duration:.6f}")
                print(f"   Absolute Diff:     {duration_diff:.6f}")
            
            # Compare accrued interest
            isin_accrued = isin_result.get("accrued")
            desc_accrued = desc_result.get("accrued")
            
            if isin_accrued is not None and desc_accrued is not None:
                accrued_diff = abs(isin_accrued - desc_accrued)
                comparison["accrued_difference"] = accrued_diff
                
                print(f"\n💰 ACCRUED INTEREST COMPARISON:")
                print(f"   ISIN Route:        {isin_accrued:.6f}")
                print(f"   Description Route: {desc_accrued:.6f}")
                print(f"   Absolute Diff:     {accrued_diff:.6f}")
            
            # Compare conventions
            isin_conv = isin_result.get("conventions", {})
            desc_conv = desc_result.get("conventions", {})
            
            print(f"\n⚙️  CONVENTION COMPARISON:")
            conv_fields = ["day_count", "frequency", "business_convention", "parsing_method", "conventions_source"]
            
            for field in conv_fields:
                isin_val = isin_conv.get(field)
                desc_val = desc_conv.get(field)
                
                if isin_val != desc_val:
                    comparison["convention_differences"].append({
                        "field": field,
                        "isin_value": isin_val,
                        "desc_value": desc_val
                    })
                    print(f"   ❌ {field}:")
                    print(f"      ISIN Route:        {isin_val}")
                    print(f"      Description Route: {desc_val}")
                else:
                    print(f"   ✅ {field}: {isin_val}")
        
        else:
            print(f"❌ Cannot compare - one or both routes failed")
            if isin_result.get("status") != "success":
                print(f"   ISIN Route Error: {isin_result.get('error')}")
            if desc_result.get("status") != "success":
                print(f"   Description Route Error: {desc_result.get('error')}")
        
        return comparison
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Save detailed results to JSON file"""
        if filename is None:
            filename = f"route_comparison_{results['bond_info']['isin']}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")

def main():
    """Main function with command line interface"""
    debugger = RouteComparisonDebugger()
    
    if len(sys.argv) >= 4:
        # Command line arguments provided
        isin = sys.argv[1]
        description = sys.argv[2]
        price = float(sys.argv[3])
    else:
        # Interactive mode
        print("🔬 Bond Route Comparison Debugger")
        print("=" * 40)
        
        # Test cases - you can modify these
        test_cases = [
            {
                "isin": "XS2249741674",
                "description": "GALAXY PIPELINE, 3.25%, 30-Sep-2040",
                "price": 77.88
            },
            {
                "isin": "XS1709535097", 
                "description": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047",
                "price": 89.4
            },
            {
                "isin": "US912810TJ79",
                "description": "T 3 15/08/52",
                "price": 71.66
            }
        ]
        
        print("\nAvailable test cases:")
        for i, case in enumerate(test_cases):
            print(f"{i+1}. {case['isin']} - {case['description']}")
        
        choice = input(f"\nEnter test case number (1-{len(test_cases)}) or 'c' for custom: ")
        
        if choice.lower() == 'c':
            isin = input("Enter ISIN: ")
            description = input("Enter Description: ")
            price = float(input("Enter Price: "))
        else:
            try:
                case_idx = int(choice) - 1
                case = test_cases[case_idx]
                isin = case["isin"]
                description = case["description"]
                price = case["price"]
            except:
                print("Invalid choice, using first test case")
                case = test_cases[0]
                isin = case["isin"]
                description = case["description"] 
                price = case["price"]
    
    # Run the comparison
    results = debugger.test_bond_routes(isin, description, price)
    
    # Save results
    debugger.save_results(results)
    
    # Summary
    print(f"\n{'='*80}")
    print(f"🎯 SUMMARY")
    print(f"{'='*80}")
    
    comparison = results.get("comparison", {})
    
    if comparison.get("both_successful"):
        yield_diff = comparison.get("yield_difference", 0)
        conv_diffs = len(comparison.get("convention_differences", []))
        
        if comparison.get("identical_results"):
            print(f"✅ ROUTES ARE IDENTICAL - No convention issues detected")
        elif yield_diff < 0.01:
            print(f"⚠️  MINOR DIFFERENCES - Yield diff: {yield_diff*100:.4f} bp")
        else:
            print(f"❌ SIGNIFICANT DIFFERENCES - Yield diff: {yield_diff*100:.4f} bp")
        
        if conv_diffs > 0:
            print(f"⚠️  CONVENTION DIFFERENCES FOUND: {conv_diffs}")
            print("   This explains the yield differences!")
        else:
            print(f"✅ NO CONVENTION DIFFERENCES - Issue may be elsewhere")
    else:
        print(f"❌ ONE OR BOTH ROUTES FAILED - Cannot compare")

if __name__ == "__main__":
    main()
