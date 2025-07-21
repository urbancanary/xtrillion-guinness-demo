#!/usr/bin/env python3
"""
🏛️ Complete 25-Bond Portfolio Analytics from Database
==================================================
Extract yield, duration, and spread data directly from bonds_data.db
Using most recent data points for each ISIN
"""

import sqlite3
import pandas as pd
from datetime import datetime

# Database path
DB_PATH = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/bonds_data.db"

# All 25 ISINs
BOND_ISINS = [
    "US912810TJ79", "XS2249741674", "XS1709535097", "XS1982113463", "USP37466AS18",
    "USP3143NAH72", "USP30179BR86", "US195325DX04", "US279158AJ82", "USP37110AM89",
    "XS2542166231", "XS2167193015", "XS1508675508", "XS1807299331", "US91086QAZ19",
    "USP6629MAD40", "US698299BL70", "US71654QDF63", "US71654QDE98", "XS2585988145",
    "XS1959337749", "XS2233188353", "XS2359548935", "XS0911024635", "USP0R80BAG79"
]

# Bond names from your input
BOND_NAMES = [
    "US TREASURY N/B, 3%, 15-Aug-2052",
    "GALAXY PIPELINE, 3.25%, 30-Sep-2040",
    "ABU DHABI CRUDE, 4.6%, 02-Nov-2047",
    "SAUDI ARAB OIL, 4.25%, 16-Apr-2039",
    "EMPRESA METRO, 4.7%, 07-May-2050",
    "CODELCO INC, 6.15%, 24-Oct-2036",
    "COMISION FEDERAL, 6.264%, 15-Feb-2052",
    "COLOMBIA REP OF, 3.875%, 15-Feb-2061",
    "ECOPETROL SA, 5.875%, 28-May-2045",
    "EMPRESA NACIONAL, 4.5%, 14-Sep-2047",
    "GREENSAIF PIPELI, 6.129%, 23-Feb-2038",
    "STATE OF ISRAEL, 3.8%, 13-May-2060",
    "SAUDI INT BOND, 4.5%, 26-Oct-2046",
    "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048",
    "UNITED MEXICAN, 5.75%, 12-Oct-2110",
    "MEXICO CITY ARPT, 5.5%, 31-Jul-2047",
    "PANAMA, 3.87%, 23-Jul-2060",
    "PETROLEOS MEXICA, 6.95%, 28-Jan-2060",
    "PETROLEOS MEXICA, 5.95%, 28-Jan-2031",
    "GACI FIRST INVST, 5.125%, 14-Feb-2053",
    "QATAR STATE OF, 4.817%, 14-Mar-2049",
    "QNB FINANCE LTD, 1.625%, 22-Sep-2025",
    "QATAR ENERGY, 3.125%, 12-Jul-2041",
    "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043",
    "SITIOS, 5.375%, 04-Apr-2032"
]

# User provided prices
BOND_PRICES = [
    71.66, 77.88, 89.40, 87.14, 80.39, 101.63, 86.42, 52.71, 69.31, 76.24,
    103.03, 64.50, 82.42, 92.21, 78.00, 82.57, 56.60, 71.42, 89.55, 85.54,
    89.97, 99.23, 73.79, 93.29, 97.26
]

def get_latest_bond_data():
    """Get most recent yield and duration data for all bonds from database"""
    
    conn = sqlite3.connect(DB_PATH)
    
    # Query to get most recent data for each ISIN
    query = """
    SELECT 
        p.isin,
        p.description,
        p.price as db_price,
        p.ytw as yield_pct,
        p.oad as duration_years,
        p.bpdate as date_str
    FROM pricetable p
    WHERE p.isin IN ({})
    ORDER BY p.bpdate DESC
    """.format(','.join(['?' for _ in BOND_ISINS]))
    
    df = pd.read_sql_query(query, conn, params=BOND_ISINS)
    conn.close()
    
    # Get most recent entry for each ISIN
    latest_df = df.groupby('isin').first().reset_index()
    
    return latest_df

def calculate_spreads(yields, treasury_yield):
    """Calculate spreads vs Treasury benchmark in basis points"""
    return [(y - treasury_yield) * 100 if y > 0 else 0 for y in yields]

def main():
    print("🏛️ 25-Bond Portfolio Analytics from Database")
    print("=" * 80)
    
    # Get data from database
    df = get_latest_bond_data()
    
    # Create comprehensive results table
    results = []
    
    for i, isin in enumerate(BOND_ISINS):
        # Get database data if available
        db_row = df[df['isin'] == isin]
        
        if not db_row.empty:
            yield_val = db_row.iloc[0]['yield_pct']
            duration_val = db_row.iloc[0]['duration_years']
            db_price = db_row.iloc[0]['db_price']
            db_desc = db_row.iloc[0]['description']
        else:
            yield_val = 0.0
            duration_val = 0.0
            db_price = 0.0
            db_desc = "Not found"
        
        results.append({
            'num': i + 1,
            'isin': isin,
            'user_price': BOND_PRICES[i],
            'db_price': db_price,
            'name': BOND_NAMES[i],
            'db_description': db_desc,
            'yield': yield_val,
            'duration': duration_val
        })
    
    # Find Treasury benchmark (US Treasury bond)
    treasury_yield = 0.0
    for r in results:
        if "US TREASURY" in r['name'] and r['yield'] > 0:
            treasury_yield = r['yield']
            break
    
    print(f"📊 Treasury Benchmark Yield: {treasury_yield:.2f}%")
    print(f"📅 Data Source: Database historical pricing")
    print("-" * 120)
    
    # Calculate spreads
    yields = [r['yield'] for r in results]
    spreads = calculate_spreads(yields, treasury_yield)
    
    # Display results table
    print(f"{'#':<3} {'ISIN':<15} {'User Price':<10} {'DB Price':<9} {'Description':<35} {'Yield (%)':<9} {'Duration':<9} {'Spread (bps)':<12}")
    print("-" * 120)
    
    portfolio_yield = 0
    portfolio_duration = 0
    portfolio_spread = 0
    successful_bonds = 0
    
    for i, result in enumerate(results):
        spread_val = spreads[i]
        
        if result['yield'] > 0:  # Valid data
            portfolio_yield += result['yield']
            portfolio_duration += result['duration']
            portfolio_spread += spread_val
            successful_bonds += 1
        
        # Format description to fit
        desc_short = result['name'][:35]
        
        print(f"{result['num']:<3} {result['isin']:<15} {result['user_price']:<10.2f} "
              f"{result['db_price']:<9.2f} {desc_short:<35} {result['yield']:<9.2f} "
              f"{result['duration']:<9.2f} {spread_val:<12.0f}")
    
    print("-" * 120)
    
    # Portfolio summary
    if successful_bonds > 0:
        avg_yield = portfolio_yield / successful_bonds
        avg_duration = portfolio_duration / successful_bonds
        avg_spread = portfolio_spread / successful_bonds
        
        print(f"\n📊 PORTFOLIO SUMMARY:")
        print(f"   Total Bonds: {len(results)}")
        print(f"   Available in Database: {successful_bonds}")
        print(f"   Coverage: {successful_bonds/len(results)*100:.1f}%")
        print(f"   Average Yield: {avg_yield:.2f}%")
        print(f"   Average Duration: {avg_duration:.2f} years")
        print(f"   Average Spread: {avg_spread:.0f} bps")
        print(f"   Treasury Benchmark: {treasury_yield:.2f}%")
        
        # Key insights
        print(f"\n🎯 KEY INSIGHTS:")
        highest_yield = max([r for r in results if r['yield'] > 0], key=lambda x: x['yield'])
        longest_duration = max([r for r in results if r['duration'] > 0], key=lambda x: x['duration'])
        widest_spread = max(spreads)
        
        print(f"   Highest Yield: {highest_yield['name'][:40]} ({highest_yield['yield']:.2f}%)")
        print(f"   Longest Duration: {longest_duration['name'][:40]} ({longest_duration['duration']:.2f} years)")
        print(f"   Widest Spread: {widest_spread:.0f} bps")
        
    else:
        print("⚠️  No bond data found in database")

if __name__ == "__main__":
    main()
