#!/usr/bin/env python3
"""
Validation script to compare our comprehensive test results against Bloomberg baseline.
"""

import sqlite3
import pandas as pd
import numpy as np

def get_25_bond_portfolio():
    """Returns the hardcoded 25-bond portfolio for testing."""
    return [
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

def get_bloomberg_baseline():
    """Returns the HIGH PRECISION Bloomberg baseline results from user's actual Bloomberg Terminal data."""
    return {
        "US912810TJ79": {"yield": 4.898453, "duration": 16.357839, "spread": None},
        "XS2249741674": {"yield": 5.637570, "duration": 10.097620, "spread": 118},
        "XS1709535097": {"yield": 5.717451, "duration": 9.815219, "spread": 123},
        "XS1982113463": {"yield": 5.599746, "duration": 9.927596, "spread": 111},
        "USP37466AS18": {"yield": 6.265800, "duration": 13.189567, "spread": 144},
        "USP3143NAH72": {"yield": 5.949058, "duration": 8.024166, "spread": 160},
        "USP30179BR86": {"yield": 7.442306, "duration": 11.583500, "spread": 261},
        "US195325DX04": {"yield": 7.836133, "duration": 12.975798, "spread": 301},
        "US279158AJ82": {"yield": 9.282266, "duration": 9.812703, "spread": 445},
        "USP37110AM89": {"yield": 6.542351, "duration": 12.389556, "spread": 171},
        "XS2542166231": {"yield": 5.720213, "duration": 7.207705, "spread": 146},
        "XS2167193015": {"yield": 6.337460, "duration": 15.269052, "spread": 151},
        "XS1508675508": {"yield": 5.967150, "duration": 12.598517, "spread": 114},
        "XS1807299331": {"yield": 7.059957, "duration": 11.446459, "spread": 223},
        "US91086QAZ19": {"yield": 7.374879, "duration": 13.370728, "spread": 255},
        "USP6629MAD40": {"yield": 7.070132, "duration": 11.382487, "spread": 224},
        "US698299BL70": {"yield": 7.362747, "duration": 13.488582, "spread": 253},
        "US71654QDF63": {"yield": 9.875691, "duration": 9.719713, "spread": 505},
        "US71654QDE98": {"yield": 8.324595, "duration": 4.469801, "spread": 444},
        "XS2585988145": {"yield": 6.228001, "duration": 13.327227, "spread": 140},
        "XS1959337749": {"yield": 5.584981, "duration": 13.261812, "spread": 76},
        "XS2233188353": {"yield": 5.015259, "duration": 0.225205, "spread": 71},
        "XS2359548935": {"yield": 5.628065, "duration": 11.512115, "spread": 101},
        "XS0911024635": {"yield": 5.663334, "duration": 11.237819, "spread": 95},
        "USP0R80BAG79": {"yield": 5.870215, "duration": 5.514383, "spread": 187}
    }

def validate_results():
    """Compare our results against Bloomberg baseline."""
    
    # Get the latest results database
    import glob
    import os
    
    # Find the latest results database
    db_files = glob.glob('six_way_analysis_FIXED_*.db')
    if not db_files:
        print("❌ No results database found")
        return
    
    latest_db = max(db_files, key=os.path.getctime)
    print(f"📊 Using database: {latest_db}")
    
    # Load results
    conn = sqlite3.connect(latest_db)
    results_df = pd.read_sql_query("SELECT * FROM test_log", conn)
    conn.close()
    
    # Get Bloomberg baseline
    bloomberg_baseline = get_bloomberg_baseline()
    
    # Get our 25 bond portfolio
    portfolio = get_25_bond_portfolio()
    
    print("\n" + "="*80)
    print("🎯 VALIDATION: Our Results vs Bloomberg Baseline")
    print("="*80)
    
    validation_results = []
    
    for bond in portfolio:
        isin = bond['isin']
        price = bond['price']
        description = bond['description']
        
        # Get Bloomberg baseline
        bbg = bloomberg_baseline.get(isin, {})
        bbg_yield = bbg.get('yield')
        bbg_duration = bbg.get('duration')
        bbg_spread = bbg.get('spread')
        
        # Get our best results (using Method 1: Direct Local + ISIN)
        our_results = results_df[
            (results_df['ISIN'] == isin) & 
            (results_df['Method'] == 'Method 1: Local+ISIN') &
            (results_df['Success'] == 1)
        ]
        
        if not our_results.empty and pd.notna(our_results.iloc[0]['Yield']):
            our_yield = our_results.iloc[0]['Yield']
            our_duration = our_results.iloc[0]['Duration']
            our_spread = our_results.iloc[0]['Spread']
            
            # Calculate differences
            yield_diff = abs(our_yield - bbg_yield) if bbg_yield else None
            duration_diff = abs(our_duration - bbg_duration) if bbg_duration else None
            
            validation_results.append({
                'ISIN': isin,
                'Description': description[:50] + '...' if len(description) > 50 else description,
                'Price': price,
                'Bloomberg_Yield': bbg_yield,
                'Our_Yield': our_yield,
                'Yield_Diff': yield_diff,
                'Bloomberg_Duration': bbg_duration,
                'Our_Duration': our_duration,
                'Duration_Diff': duration_diff,
                'Bloomberg_Spread': bbg_spread,
                'Our_Spread': our_spread
            })
    
    # Create validation dataframe
    validation_df = pd.DataFrame(validation_results)
    
    print(f"\n📈 SUMMARY STATISTICS:")
    print(f"Total bonds validated: {len(validation_df)}")
    
    # Yield accuracy
    yield_diffs = validation_df['Yield_Diff'].dropna()
    if not yield_diffs.empty:
        print(f"\n🎯 YIELD ACCURACY:")
        print(f"Average absolute difference: {yield_diffs.mean():.4f}%")
        print(f"Median absolute difference: {yield_diffs.median():.4f}%")
        print(f"Max difference: {yield_diffs.max():.4f}%")
        print(f"Min difference: {yield_diffs.min():.4f}%")
        
        within_1bp = (yield_diffs <= 0.01).sum()
        within_5bp = (yield_diffs <= 0.05).sum()
        within_10bp = (yield_diffs <= 0.10).sum()
        
        print(f"Within 1bp: {within_1bp}/{len(yield_diffs)} ({within_1bp/len(yield_diffs)*100:.1f}%)")
        print(f"Within 5bp: {within_5bp}/{len(yield_diffs)} ({within_5bp/len(yield_diffs)*100:.1f}%)")
        print(f"Within 10bp: {within_10bp}/{len(yield_diffs)} ({within_10bp/len(yield_diffs)*100:.1f}%)")
    
    # Duration accuracy
    duration_diffs = validation_df['Duration_Diff'].dropna()
    if not duration_diffs.empty:
        print(f"\n⏱️ DURATION ACCURACY:")
        print(f"Average absolute difference: {duration_diffs.mean():.4f} years")
        print(f"Median absolute difference: {duration_diffs.median():.4f} years")
        print(f"Max difference: {duration_diffs.max():.4f} years")
        print(f"Min difference: {duration_diffs.min():.4f} years")
        
        within_0_01 = (duration_diffs <= 0.01).sum()
        within_0_05 = (duration_diffs <= 0.05).sum()
        within_0_1 = (duration_diffs <= 0.1).sum()
        
        print(f"Within 0.01 years: {within_0_01}/{len(duration_diffs)} ({within_0_01/len(duration_diffs)*100:.1f}%)")
        print(f"Within 0.05 years: {within_0_05}/{len(duration_diffs)} ({within_0_05/len(duration_diffs)*100:.1f}%)")
        print(f"Within 0.1 years: {within_0_1}/{len(duration_diffs)} ({within_0_1/len(duration_diffs)*100:.1f}%)")
    
    # Detailed results
    print(f"\n📋 DETAILED RESULTS:")
    print("-" * 120)
    print(f"{'ISIN':<12} {'DESCRIPTION':<35} {'PRICE':<6} {'BBG_YLD':<8} {'OUR_YLD':<8} {'DIFF_bp':<8} {'BBG_DUR':<8} {'OUR_DUR':<8} {'DIFF':<6}")
    print("-" * 120)
    
    for _, row in validation_df.iterrows():
        yield_diff_bp = row['Yield_Diff'] * 100 if row['Yield_Diff'] else None
        duration_diff = row['Duration_Diff'] if row['Duration_Diff'] else None
        
        print(f"{row['ISIN']:<12} {row['Description']:<35} {row['Price']:<6.2f} "
              f"{row['Bloomberg_Yield']:<8.4f} {row['Our_Yield']:<8.4f} "
              f"{yield_diff_bp:<8.1f} {row['Bloomberg_Duration']:<8.4f} {row['Our_Duration']:<8.4f} "
              f"{duration_diff:<6.4f}")
    
    return validation_df

if __name__ == "__main__":
    validate_results()
