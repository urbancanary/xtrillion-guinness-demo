#!/usr/bin/env python3
"""
🎯 Google Analysis 10 - Comprehensive Hierarchy Performance Test
Test all 25 Bloomberg baseline bonds through the optimized lookup hierarchy
"""

import time
from optimized_bond_lookup import OptimizedBondLookup
import pandas as pd
from datetime import datetime

def comprehensive_hierarchy_test():
    """Test all 25 Bloomberg baseline bonds through optimized hierarchy"""
    
    # Bloomberg baseline test bonds
    bloomberg_bonds = [
        {"ISIN": "US912810TJ79", "PX_MID": 71.66, "Name": "US TREASURY N/B, 3%, 15-Aug-2052"},
        {"ISIN": "XS2249741674", "PX_MID": 77.88, "Name": "GALAXY PIPELINE, 3.25%, 30-Sep-2040"},
        {"ISIN": "XS1709535097", "PX_MID": 89.40, "Name": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047"},
        {"ISIN": "XS1982113463", "PX_MID": 87.14, "Name": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039"},
        {"ISIN": "USP37466AS18", "PX_MID": 80.39, "Name": "EMPRESA METRO, 4.7%, 07-May-2050"},
        {"ISIN": "USP3143NAH72", "PX_MID": 101.63, "Name": "CODELCO INC, 6.15%, 24-Oct-2036"},
        {"ISIN": "USP30179BR86", "PX_MID": 86.42, "Name": "COMISION FEDERAL, 6.264%, 15-Feb-2052"},
        {"ISIN": "US195325DX04", "PX_MID": 52.71, "Name": "COLOMBIA REP OF, 3.875%, 15-Feb-2061"},
        {"ISIN": "US279158AJ82", "PX_MID": 69.31, "Name": "ECOPETROL SA, 5.875%, 28-May-2045"},
        {"ISIN": "USP37110AM89", "PX_MID": 76.24, "Name": "EMPRESA NACIONAL, 4.5%, 14-Sep-2047"},
        {"ISIN": "XS2542166231", "PX_MID": 103.03, "Name": "GREENSAIF PIPELI, 6.129%, 23-Feb-2038"},
        {"ISIN": "XS2167193015", "PX_MID": 64.50, "Name": "STATE OF ISRAEL, 3.8%, 13-May-2060"},
        {"ISIN": "XS1508675508", "PX_MID": 82.42, "Name": "SAUDI INT BOND, 4.5%, 26-Oct-2046"},
        {"ISIN": "XS1807299331", "PX_MID": 92.21, "Name": "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048"},
        {"ISIN": "US91086QAZ19", "PX_MID": 78.00, "Name": "UNITED MEXICAN, 5.75%, 12-Oct-2110"},
        {"ISIN": "USP6629MAD40", "PX_MID": 82.57, "Name": "MEXICO CITY ARPT, 5.5%, 31-Jul-2047"},
        {"ISIN": "US698299BL70", "PX_MID": 56.60, "Name": "PANAMA, 3.87%, 23-Jul-2060"},
        {"ISIN": "US71654QDF63", "PX_MID": 71.42, "Name": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060"},
        {"ISIN": "US71654QDE98", "PX_MID": 89.55, "Name": "PETROLEOS MEXICA, 5.95%, 28-Jan-2031"},
        {"ISIN": "XS2585988145", "PX_MID": 85.54, "Name": "GACI FIRST INVST, 5.125%, 14-Feb-2053"},
        {"ISIN": "XS1959337749", "PX_MID": 89.97, "Name": "QATAR STATE OF, 4.817%, 14-Mar-2049"},
        {"ISIN": "XS2233188353", "PX_MID": 99.23, "Name": "QNB FINANCE LTD, 1.625%, 22-Sep-2025"},
        {"ISIN": "XS2359548935", "PX_MID": 73.79, "Name": "QATAR ENERGY, 3.125%, 12-Jul-2041"},
        {"ISIN": "XS0911024635", "PX_MID": 93.29, "Name": "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043"},
        {"ISIN": "USP0R80BAG79", "PX_MID": 97.26, "Name": "SITIOS, 5.375%, 04-Apr-2032"}
    ]
    
    print("🎯 Google Analysis 10 - Comprehensive Hierarchy Performance Test")
    print(f"   Testing {len(bloomberg_bonds)} Bloomberg baseline bonds")
    print("=" * 80)
    
    lookup = OptimizedBondLookup()
    results = []
    
    # Test each bond through hierarchy
    for i, bond in enumerate(bloomberg_bonds):
        isin = bond['ISIN']
        name = bond['Name']
        
        print(f"\n📊 Bond {i+1}/25: {isin}")
        print(f"   {name[:60]}...")
        
        # Test ISIN-only lookup (this will follow the hierarchy)
        start_time = time.time()
        result = lookup.lookup_bond_hierarchy(isin=isin)
        end_time = time.time()
        
        # Extract key information
        result_summary = {
            'Bond_Number': i + 1,
            'ISIN': isin,
            'Name': name[:50] + "..." if len(name) > 50 else name,
            'Status': result['status'],
            'Route_Used': result.get('route_used', 'N/A'),
            'Hierarchy_Level': result.get('hierarchy_level', 'N/A'),
            'Lookup_Time_ms': result.get('lookup_time_ms', 0),
            'Has_Validated_Data': result.get('data_quality') == 'validated',
            'Has_Description': bool(result.get('description')),
            'Day_Count': result.get('conventions', {}).get('day_count', 'N/A'),
            'Frequency': result.get('conventions', {}).get('fixed_frequency', 'N/A')
        }
        
        results.append(result_summary)
        
        # Display immediate result
        if result['status'] == 'success':
            hierarchy_emoji = {1: "🏆", 2: "🥈", 3: "🥉", 4: "❌"}
            level_emoji = hierarchy_emoji.get(result.get('hierarchy_level', 4), "❓")
            
            print(f"   {level_emoji} SUCCESS (Level {result.get('hierarchy_level', 'N/A')}) - {result.get('lookup_time_ms', 0)}ms")
            print(f"      Route: {result.get('route_used', 'N/A')}")
            
            if result.get('data_quality') == 'validated':
                print(f"      ✅ VALIDATED CONVENTIONS: {result.get('conventions', {}).get('day_count', 'N/A')}")
            elif result.get('description'):
                print(f"      📝 DESCRIPTION: {result.get('description', 'N/A')[:50]}...")
            else:
                print(f"      📋 CONVENTIONS: {result.get('conventions', {}).get('day_count', 'N/A')}")
        else:
            print(f"   ❌ FAILED: {result.get('error', 'Unknown error')}")
    
    # Analyze results
    analyze_hierarchy_performance(results)
    
    # Save detailed results
    save_hierarchy_results(results)
    
    return results

def analyze_hierarchy_performance(results):
    """Analyze performance across hierarchy levels"""
    print("\n" + "=" * 80)
    print("📊 HIERARCHY PERFORMANCE ANALYSIS")
    print("=" * 80)
    
    total_bonds = len(results)
    successful_bonds = len([r for r in results if r['Status'] == 'success'])
    
    print(f"🎯 Overall Results:")
    print(f"   Total Bonds: {total_bonds}")
    print(f"   Successful: {successful_bonds}")
    print(f"   Success Rate: {successful_bonds/total_bonds*100:.1f}%")
    
    # Hierarchy level breakdown
    hierarchy_stats = {}
    for result in results:
        if result['Status'] == 'success':
            level = result['Hierarchy_Level']
            if level not in hierarchy_stats:
                hierarchy_stats[level] = []
            hierarchy_stats[level].append(result)
    
    print(f"\n🏆 Hierarchy Level Performance:")
    hierarchy_names = {
        1: "🏆 Level 1: Validated QuantLib Bonds (FASTEST + BEST QUALITY)",
        2: "🥈 Level 2: Description Parsing (EFFICIENT)",
        3: "🥉 Level 3: ISIN → Description Lookup (FALLBACK)",
        4: "❌ Level 4: Error/Insufficient Input"
    }
    
    for level in sorted(hierarchy_stats.keys()):
        level_results = hierarchy_stats[level]
        count = len(level_results)
        percentage = count / successful_bonds * 100
        avg_time = sum(r['Lookup_Time_ms'] for r in level_results) / count if count > 0 else 0
        
        print(f"   {hierarchy_names.get(level, f'Level {level}')}")
        print(f"      Bonds: {count}/{successful_bonds} ({percentage:.1f}%)")
        print(f"      Avg Time: {avg_time:.1f}ms")
        
        # Show which bonds used this level
        if count <= 8:  # Show individual bonds if not too many
            for r in level_results[:8]:
                print(f"        • {r['ISIN']}: {r['Lookup_Time_ms']}ms")
        print()
    
    # Performance stats
    successful_results = [r for r in results if r['Status'] == 'success']
    if successful_results:
        times = [r['Lookup_Time_ms'] for r in successful_results]
        print(f"⚡ Performance Statistics:")
        print(f"   Average Lookup Time: {sum(times)/len(times):.1f}ms")
        print(f"   Fastest Lookup: {min(times)}ms")
        print(f"   Slowest Lookup: {max(times)}ms")
        
        # Count validated bonds
        validated_count = len([r for r in successful_results if r['Has_Validated_Data']])
        print(f"   Validated Conventions: {validated_count}/{successful_bonds} ({validated_count/successful_bonds*100:.1f}%)")

def save_hierarchy_results(results):
    """Save detailed results to CSV"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"hierarchy_performance_test_{timestamp}.csv"
    filepath = f"/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/{filename}"
    
    df = pd.DataFrame(results)
    df.to_csv(filepath, index=False)
    
    print(f"\n💾 Detailed results saved to: {filepath}")
    print(f"   Ready for further analysis and review!")

if __name__ == "__main__":
    comprehensive_hierarchy_test()
