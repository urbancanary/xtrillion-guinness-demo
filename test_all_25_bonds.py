#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE 25-BOND PORTFOLIO TEST
Tests ALL bonds from the portfolio to validate corrected compounding conventions
"""

import requests
import json
import time
import sys
from typing import Dict, List

# API Configuration
API_BASE = "http://localhost:8082"
SETTLEMENT_DATE = "2025-07-30"

# Complete 25-bond portfolio from the documents
PORTFOLIO_BONDS = [
    {"description": "T 3 15/08/52", "price": 71.66, "weight": 1.03, "expected_yield": 4.90},
    {"description": "GALAXY PIPELINE, 3.25%, 30-Sep-2040", "price": 77.88, "weight": 3.88, "expected_yield": 5.64},
    {"description": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047", "price": 89.40, "weight": 3.78, "expected_yield": 5.72},
    {"description": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039", "price": 87.14, "weight": 3.71, "expected_yield": 5.60},
    {"description": "EMPRESA METRO, 4.7%, 07-May-2050", "price": 80.39, "weight": 4.57, "expected_yield": 6.27},
    {"description": "CODELCO INC, 6.15%, 24-Oct-2036", "price": 101.63, "weight": 5.79, "expected_yield": 5.95},
    {"description": "COMISION FEDERAL, 6.264%, 15-Feb-2052", "price": 86.42, "weight": 6.27, "expected_yield": 7.44},
    {"description": "COLOMBIA REP OF, 3.875%, 15-Feb-2061", "price": 52.71, "weight": 3.82, "expected_yield": 7.84},
    {"description": "ECOPETROL SA, 5.875%, 28-May-2045", "price": 69.31, "weight": 2.93, "expected_yield": 9.28},
    {"description": "EMPRESA NACIONAL, 4.5%, 14-Sep-2047", "price": 76.24, "weight": 2.73, "expected_yield": 6.54},
    {"description": "GREENSAIF PIPELI, 6.129%, 23-Feb-2038", "price": 103.03, "weight": 2.96, "expected_yield": 5.72},
    {"description": "STATE OF ISRAEL, 3.8%, 13-May-2060", "price": 64.50, "weight": 4.14, "expected_yield": 6.34},
    {"description": "SAUDI INT BOND, 4.5%, 26-Oct-2046", "price": 82.42, "weight": 4.09, "expected_yield": 5.97},
    {"description": "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048", "price": 92.21, "weight": 6.58, "expected_yield": 7.06},
    {"description": "UNITED MEXICAN, 5.75%, 12-Oct-2110", "price": 78.00, "weight": 1.69, "expected_yield": 7.37},
    {"description": "MEXICO CITY ARPT, 5.5%, 31-Jul-2047", "price": 82.57, "weight": 3.89, "expected_yield": 7.07},
    {"description": "PANAMA, 3.87%, 23-Jul-2060", "price": 56.60, "weight": 4.12, "expected_yield": 7.36},
    {"description": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060", "price": 71.42, "weight": 3.95, "expected_yield": 9.88},
    {"description": "PETROLEOS MEXICA, 5.95%, 28-Jan-2031", "price": 89.55, "weight": 1.30, "expected_yield": 8.32},
    {"description": "GACI FIRST INVST, 5.125%, 14-Feb-2053", "price": 85.54, "weight": 2.78, "expected_yield": 6.23},
    {"description": "QATAR STATE OF, 4.817%, 14-Mar-2049", "price": 89.97, "weight": 4.50, "expected_yield": 5.58},
    {"description": "QNB FINANCE LTD, 1.625%, 22-Sep-2025", "price": 99.23, "weight": 4.90, "expected_yield": 5.02},
    {"description": "QATAR ENERGY, 3.125%, 12-Jul-2041", "price": 73.79, "weight": 3.70, "expected_yield": 5.63},
    {"description": "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043", "price": 93.29, "weight": 3.32, "expected_yield": 5.66},
    {"description": "SITIOS, 5.375%, 04-Apr-2032", "price": 97.26, "weight": 3.12, "expected_yield": 5.87}
]

def test_single_bond(bond_data: Dict, bond_number: int) -> Dict:
    """Test a single bond and return results"""
    print(f"\n🧪 Testing Bond {bond_number:2d}: {bond_data['description'][:50]}...")
    
    # Prepare API request
    payload = {
        "description": bond_data["description"],
        "price": bond_data["price"],
        "settlement_date": SETTLEMENT_DATE
    }
    
    try:
        # Make API call
        response = requests.post(
            f"{API_BASE}/api/v1/bond/parse-and-calculate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract key metrics
            yield_to_maturity = result.get("yield_to_maturity", 0)
            duration = result.get("duration", 0)
            
            # Calculate yield difference
            expected_yield = bond_data.get("expected_yield", 0)
            yield_diff_bp = round((yield_to_maturity - expected_yield) * 100, 1)
            
            # Determine status
            if abs(yield_diff_bp) <= 5:
                status = "✅ PERFECT"
                status_color = "\033[92m"  # Green
            elif abs(yield_diff_bp) <= 10:
                status = "⚠️ CLOSE"
                status_color = "\033[93m"  # Yellow
            else:
                status = "❌ ERROR"
                status_color = "\033[91m"  # Red
            
            print(f"   {status_color}{status}\033[0m | "
                  f"Expected: {expected_yield:5.2f}% | "
                  f"Got: {yield_to_maturity:5.2f}% | "
                  f"Diff: {yield_diff_bp:+6.1f}bp | "
                  f"Duration: {duration:5.2f}")
            
            return {
                "bond_number": bond_number,
                "description": bond_data["description"],
                "price": bond_data["price"],
                "weight": bond_data["weight"],
                "expected_yield": expected_yield,
                "actual_yield": yield_to_maturity,
                "yield_diff_bp": yield_diff_bp,
                "duration": duration,
                "status": status.split()[1],  # PERFECT, CLOSE, ERROR
                "success": True,
                "full_response": result
            }
            
        else:
            print(f"   ❌ API ERROR | Status: {response.status_code}")
            return {
                "bond_number": bond_number,
                "description": bond_data["description"],
                "success": False,
                "error": f"HTTP {response.status_code}",
                "status": "API_ERROR"
            }
            
    except Exception as e:
        print(f"   ❌ EXCEPTION | {str(e)}")
        return {
            "bond_number": bond_number,
            "description": bond_data["description"],
            "success": False,
            "error": str(e),
            "status": "EXCEPTION"
        }

def analyze_results(results: List[Dict]) -> None:
    """Analyze and summarize test results"""
    successful_bonds = [r for r in results if r.get("success", False)]
    failed_bonds = [r for r in results if not r.get("success", False)]
    
    if not successful_bonds:
        print("\n🚨 TOTAL FAILURE - No bonds processed successfully!")
        return
    
    # Categorize successful bonds
    perfect_bonds = [r for r in successful_bonds if r["status"] == "PERFECT"]
    close_bonds = [r for r in successful_bonds if r["status"] == "CLOSE"]
    error_bonds = [r for r in successful_bonds if r["status"] == "ERROR"]
    
    # Calculate statistics
    yield_diffs = [abs(r["yield_diff_bp"]) for r in successful_bonds]
    avg_error = sum(yield_diffs) / len(yield_diffs) if yield_diffs else 0
    max_error = max(yield_diffs) if yield_diffs else 0
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"🎯 COMPREHENSIVE 25-BOND TEST RESULTS")
    print(f"{'='*80}")
    
    print(f"\n📊 SUCCESS SUMMARY:")
    print(f"   ✅ Perfect Matches (≤5bp):  {len(perfect_bonds):2d} bonds")
    print(f"   ⚠️ Close Matches (6-10bp):   {len(close_bonds):2d} bonds")
    print(f"   ❌ Significant Errors (>10bp): {len(error_bonds):2d} bonds")
    print(f"   🚨 Failed API Calls:         {len(failed_bonds):2d} bonds")
    print(f"   📈 Total Processed:          {len(successful_bonds):2d}/{len(results)} bonds")
    
    print(f"\n📈 ACCURACY METRICS:")
    print(f"   🎯 Average Error:    {avg_error:5.1f} bp")
    print(f"   📊 Maximum Error:    {max_error:5.1f} bp")
    print(f"   ✅ Success Rate:     {len(successful_bonds)/len(results)*100:5.1f}%")
    print(f"   🏆 Accuracy Rate:    {(len(perfect_bonds)+len(close_bonds))/len(results)*100:5.1f}%")
    
    # Show worst performers
    if error_bonds:
        print(f"\n🚨 BONDS WITH SIGNIFICANT ERRORS (>10bp):")
        error_bonds_sorted = sorted(error_bonds, key=lambda x: abs(x["yield_diff_bp"]), reverse=True)
        for bond in error_bonds_sorted:
            print(f"   📛 {bond['description'][:40]:40s} | "
                  f"Error: {bond['yield_diff_bp']:+6.1f}bp | "
                  f"Expected: {bond['expected_yield']:5.2f}% | "
                  f"Got: {bond['actual_yield']:5.2f}%")
    
    # Show failures
    if failed_bonds:
        print(f"\n🚨 FAILED API CALLS:")
        for bond in failed_bonds:
            print(f"   💥 {bond['description'][:40]:40s} | Error: {bond['error']}")
    
    # Overall verdict
    accuracy_rate = (len(perfect_bonds) + len(close_bonds)) / len(results) * 100
    if accuracy_rate >= 95:
        verdict = "🏆 EXCELLENT"
        verdict_color = "\033[92m"
    elif accuracy_rate >= 85:
        verdict = "✅ GOOD"
        verdict_color = "\033[93m"
    elif accuracy_rate >= 70:
        verdict = "⚠️ NEEDS WORK"
        verdict_color = "\033[93m"
    else:
        verdict = "❌ POOR"
        verdict_color = "\033[91m"
    
    print(f"\n🎯 OVERALL VERDICT: {verdict_color}{verdict}\033[0m")
    print(f"   Accuracy Rate: {accuracy_rate:.1f}% (Perfect + Close matches)")
    
    # Export results
    timestamp = int(time.time())
    output_file = f"bond_test_results_{timestamp}.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": timestamp,
            "summary": {
                "total_bonds": len(results),
                "successful_bonds": len(successful_bonds),
                "perfect_matches": len(perfect_bonds),
                "close_matches": len(close_bonds),
                "significant_errors": len(error_bonds),
                "failed_calls": len(failed_bonds),
                "average_error_bp": avg_error,
                "maximum_error_bp": max_error,
                "accuracy_rate": accuracy_rate
            },
            "detailed_results": results
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {output_file}")

def main():
    """Main test execution"""
    print(f"🚀 STARTING COMPREHENSIVE 25-BOND PORTFOLIO TEST")
    print(f"API: {API_BASE}")
    print(f"Settlement Date: {SETTLEMENT_DATE}")
    print(f"Total Bonds: {len(PORTFOLIO_BONDS)}")
    print(f"{'='*80}")
    
    # Test all bonds
    results = []
    for i, bond in enumerate(PORTFOLIO_BONDS, 1):
        result = test_single_bond(bond, i)
        results.append(result)
        time.sleep(0.5)  # Small delay to avoid overwhelming API
    
    # Analyze results
    analyze_results(results)

if __name__ == "__main__":
    main()
