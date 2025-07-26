#!/usr/bin/env python3
"""
REAL PORTFOLIO COMPARISON TEST
==============================

Test the actual portfolio data using both:
1. Portfolio Analysis system (database-driven)
2. Parser system (text input)

After settlement date fixes, results should be identical or very similar.
"""

import sqlite3
import requests
import json
from datetime import datetime

# Your actual test portfolio data
TEST_PORTFOLIO = [
    {"isin": "US912810TJ79", "price": 71.66, "description": "T 3.00 15/08/52", "weight": 1},
    {"isin": "XS2249741674", "price": 77.88, "description": "GALAXY PIPELINE, 3.25%, 30-Sep-2040", "weight": 20},
    {"isin": "XS1709535097", "price": 89.40, "description": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047", "weight": 20},
    {"isin": "XS1982113463", "price": 87.14, "description": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039", "weight": 70},
    {"isin": "USP37466AS18", "price": 80.39, "description": "EMPRESA METRO, 4.7%, 07-May-2050", "weight": 180},
    {"isin": "USP3143NAH72", "price": 101.63, "description": "CODELCO INC, 6.15%, 24-Oct-2036", "weight": 260},
    {"isin": "USP30179BR86", "price": 86.42, "description": "COMISION FEDERAL, 6.264%, 15-Feb-2052", "weight": 360},
    {"isin": "US195325DX04", "price": 52.71, "description": "COLOMBIA REP OF, 3.875%, 15-Feb-2061", "weight": 360},
    {"isin": "US279158AJ82", "price": 69.31, "description": "ECOPETROL SA, 5.875%, 28-May-2045", "weight": 940},
    {"isin": "USP37110AM89", "price": 76.24, "description": "EMPRESA NACIONAL, 4.5%, 14-Sep-2047", "weight": 180},
    {"isin": "XS2542166231", "price": 103.03, "description": "GREENSAIF PIPELI, 6.129%, 23-Feb-2038", "weight": 70},
    {"isin": "XS2167193015", "price": 64.50, "description": "STATE OF ISRAEL, 3.8%, 13-May-2060", "weight": 120},
    {"isin": "XS1508675508", "price": 82.42, "description": "SAUDI INT BOND, 4.5%, 26-Oct-2046", "weight": 70},
    {"isin": "XS1807299331", "price": 92.21, "description": "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048", "weight": 260},
    {"isin": "US91086QAZ19", "price": 78.00, "description": "UNITED MEXICAN, 5.75%, 12-Oct-2110", "weight": 360},
    {"isin": "USP6629MAD40", "price": 82.57, "description": "MEXICO CITY ARPT, 5.5%, 31-Jul-2047", "weight": 360},
    {"isin": "US698299BL70", "price": 56.60, "description": "PANAMA, 3.87%, 23-Jul-2060", "weight": 360},
    {"isin": "US71654QDF63", "price": 71.42, "description": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060", "weight": 360},
    {"isin": "US71654QDE98", "price": 89.55, "description": "PETROLEOS MEXICA, 5.95%, 28-Jan-2031", "weight": 360},
    {"isin": "XS2585988145", "price": 85.54, "description": "GACI FIRST INVST, 5.125%, 14-Feb-2053", "weight": 40},
    {"isin": "XS1959337749", "price": 89.97, "description": "QATAR STATE OF, 4.817%, 14-Mar-2049", "weight": 20},
    {"isin": "XS2233188353", "price": 99.23, "description": "QNB FINANCE LTD, 1.625%, 22-Sep-2025", "weight": 40},
    {"isin": "XS2359548935", "price": 73.79, "description": "QATAR ENERGY, 3.125%, 12-Jul-2041", "weight": 20},
    {"isin": "XS0911024635", "price": 93.29, "description": "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043", "weight": 70},
    {"isin": "USP0R80BAG79", "price": 97.26, "description": "SITIOS, 5.375%, 04-Apr-2032", "weight": 610}
]

def test_portfolio_system():
    """Test the portfolio analysis system (database-driven)"""
    print("📊 TESTING PORTFOLIO ANALYSIS SYSTEM")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('bloomberg_index.db')
        cursor = conn.cursor()
        
        results = []
        found_bonds = 0
        total_bonds = len(TEST_PORTFOLIO)
        
        for bond in TEST_PORTFOLIO:
            isin = bond["isin"]
            expected_price = bond["price"]
            
            # Get current portfolio system data
            cursor.execute("""
                SELECT isin, settlement_date, quantlib_accrued, price, 
                       coupon, maturity, days_accrued
                FROM all_bonds_calculations 
                WHERE isin = ?
            """, (isin,))
            
            result = cursor.fetchone()
            if result:
                found_bonds += 1
                portfolio_result = {
                    'isin': result[0],
                    'settlement_date': result[1],
                    'accrued_per_million': result[2],
                    'price': result[3],
                    'coupon': result[4],
                    'maturity': result[5],
                    'days_accrued': result[6],
                    'system': 'portfolio'
                }
                results.append(portfolio_result)
                
                print(f"✅ {isin}: Settlement={result[1]}, Accrued={result[2]:,.2f}")
            else:
                print(f"❌ {isin}: Not found in database")
        
        conn.close()
        
        print(f"\n📈 PORTFOLIO SYSTEM SUMMARY:")
        print(f"   Found: {found_bonds}/{total_bonds} bonds")
        print(f"   Settlement dates: {set(r['settlement_date'] for r in results)}")
        
        return results
        
    except Exception as e:
        print(f"❌ Portfolio system test failed: {e}")
        return []

def test_parser_system(test_bonds_sample=5):
    """Test the parser system (text input via API)"""
    print(f"\n🔍 TESTING PARSER SYSTEM (API)")
    print("=" * 50)
    
    # Test subset for speed
    sample_bonds = TEST_PORTFOLIO[:test_bonds_sample]
    results = []
    
    for bond in sample_bonds:
        try:
            # Use the API endpoint for bond parsing
            payload = {
                "description": bond["description"],
                "price": bond["price"],
                "settlement_date": "2025-06-30"  # Same as portfolio system
            }
            
            print(f"🧪 Testing: {bond['isin']} - {bond['description']}")
            
            response = requests.post(
                "http://localhost:8090/api/v1/bond/parse-and-calculate",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    calc_results = data.get('calculation_results', {})
                    calc_inputs = data.get('calculation_inputs', {})
                    
                    parser_result = {
                        'isin': bond['isin'],  # We know this from input
                        'settlement_date': calc_inputs.get('settlement_date'),
                        'accrued_per_million': calc_results.get('accrued_interest_per_million'),
                        'accrued_per_100': calc_results.get('accrued_interest_per_100'),
                        'yield_percent': calc_results.get('yield_to_maturity_percent'),
                        'duration_years': calc_results.get('modified_duration_years'),
                        'system': 'parser'
                    }
                    results.append(parser_result)
                    
                    print(f"   ✅ Settlement={parser_result['settlement_date']}, "
                          f"Accrued={parser_result['accrued_per_million']:,.2f}")
                else:
                    print(f"   ❌ API error: {data.get('error', 'Unknown')}")
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ⚠️ API not running (localhost:8090)")
            break
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📈 PARSER SYSTEM SUMMARY:")
    print(f"   Tested: {len(results)}/{len(sample_bonds)} bonds")
    if results:
        print(f"   Settlement dates: {set(r['settlement_date'] for r in results)}")
    
    return results

def compare_systems(portfolio_results, parser_results):
    """Compare results from both systems"""
    print(f"\n⚖️ COMPARING BOTH SYSTEMS")
    print("=" * 50)
    
    if not portfolio_results or not parser_results:
        print("❌ Cannot compare - insufficient data from one or both systems")
        return
    
    # Find matching bonds
    portfolio_dict = {r['isin']: r for r in portfolio_results}
    parser_dict = {r['isin']: r for r in parser_results}
    
    common_isins = set(portfolio_dict.keys()) & set(parser_dict.keys())
    
    if not common_isins:
        print("❌ No common bonds found between systems")
        return
    
    print(f"📊 COMPARING {len(common_isins)} COMMON BONDS:")
    print()
    
    settlement_match = 0
    accrued_comparisons = []
    
    for isin in sorted(common_isins):
        p_result = portfolio_dict[isin]
        r_result = parser_dict[isin]
        
        # Settlement date comparison
        settlement_match_status = "✅" if p_result['settlement_date'] == r_result['settlement_date'] else "❌"
        if p_result['settlement_date'] == r_result['settlement_date']:
            settlement_match += 1
        
        # Accrued interest comparison
        p_accrued = p_result.get('accrued_per_million', 0)
        r_accrued = r_result.get('accrued_per_million', 0)
        
        if p_accrued and r_accrued:
            difference = abs(p_accrued - r_accrued)
            percentage_diff = (difference / max(p_accrued, r_accrued)) * 100 if max(p_accrued, r_accrued) > 0 else 0
            
            accrued_comparisons.append({
                'isin': isin,
                'portfolio_accrued': p_accrued,
                'parser_accrued': r_accrued,
                'difference': difference,
                'percentage_diff': percentage_diff
            })
            
            status = "✅" if percentage_diff < 5 else "⚠️" if percentage_diff < 20 else "❌"
            
            print(f"{status} {isin}:")
            print(f"    Settlement: Portfolio={p_result['settlement_date']}, "
                  f"Parser={r_result['settlement_date']} {settlement_match_status}")
            print(f"    Accrued: Portfolio={p_accrued:,.0f}, "
                  f"Parser={r_accrued:,.0f}, Diff={percentage_diff:.1f}%")
            print()
    
    # Summary
    print("📈 OVERALL COMPARISON SUMMARY:")
    print(f"   Settlement Date Alignment: {settlement_match}/{len(common_isins)} bonds match")
    
    if accrued_comparisons:
        avg_percentage_diff = sum(c['percentage_diff'] for c in accrued_comparisons) / len(accrued_comparisons)
        excellent_matches = sum(1 for c in accrued_comparisons if c['percentage_diff'] < 5)
        
        print(f"   Accrued Interest Alignment:")
        print(f"     Average difference: {avg_percentage_diff:.1f}%")
        print(f"     Excellent matches (<5% diff): {excellent_matches}/{len(accrued_comparisons)}")
        
        if avg_percentage_diff < 5:
            print(f"   🎉 RESULT: EXCELLENT ALIGNMENT")
        elif avg_percentage_diff < 20:
            print(f"   ✅ RESULT: GOOD ALIGNMENT")
        else:
            print(f"   ⚠️ RESULT: NEEDS INVESTIGATION")

def main():
    """Run the comprehensive comparison test"""
    print("🚀 REAL PORTFOLIO COMPARISON TEST")
    print("=" * 60)
    print(f"Testing {len(TEST_PORTFOLIO)} bonds from your actual portfolio")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test both systems
    portfolio_results = test_portfolio_system()
    parser_results = test_parser_system(test_bonds_sample=5)  # Test subset for speed
    
    # Compare results
    compare_systems(portfolio_results, parser_results)

if __name__ == "__main__":
    main()
