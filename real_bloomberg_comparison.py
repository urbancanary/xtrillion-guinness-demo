#!/usr/bin/env python3
"""
REAL Bloomberg Baseline Comparison
Using ACTUAL Bloomberg data provided by user on 2025-07-22
"""

import sqlite3
import pandas as pd
import numpy as np

# ACTUAL Bloomberg baseline data provided by user
REAL_BLOOMBERG_DATA = {
    'US912810TJ79': {'yield': 4.90, 'duration': 16.36, 'spread': None},
    'XS2249741674': {'yield': 5.64, 'duration': 10.10, 'spread': 118},
    'XS1709535097': {'yield': 5.72, 'duration': 9.82, 'spread': 123},
    'XS1982113463': {'yield': 5.60, 'duration': 9.93, 'spread': 111},
    'USP37466AS18': {'yield': 6.27, 'duration': 13.19, 'spread': 144},
    'USP3143NAH72': {'yield': 5.95, 'duration': 8.02, 'spread': 160},
    'USP30179BR86': {'yield': 7.44, 'duration': 11.58, 'spread': 261},
    'US195325DX04': {'yield': 7.84, 'duration': 12.98, 'spread': 301},
    'US279158AJ82': {'yield': 9.28, 'duration': 9.81, 'spread': 445},
    'USP37110AM89': {'yield': 6.54, 'duration': 12.39, 'spread': 171},
    'XS2542166231': {'yield': 5.72, 'duration': 7.21, 'spread': 146},
    'XS2167193015': {'yield': 6.34, 'duration': 15.27, 'spread': 151},
    'XS1508675508': {'yield': 5.97, 'duration': 12.60, 'spread': 114},
    'XS1807299331': {'yield': 7.06, 'duration': 11.45, 'spread': 223},
    'US91086QAZ19': {'yield': 7.37, 'duration': 13.37, 'spread': 255},
    'USP6629MAD40': {'yield': 7.07, 'duration': 11.38, 'spread': 224},
    'US698299BL70': {'yield': 7.36, 'duration': 13.49, 'spread': 253},
    'US71654QDF63': {'yield': 9.88, 'duration': 9.72, 'spread': 505},
    'US71654QDE98': {'yield': 8.32, 'duration': 4.47, 'spread': 444},
    'XS2585988145': {'yield': 6.23, 'duration': 13.33, 'spread': 140},
    'XS1959337749': {'yield': 5.58, 'duration': 13.26, 'spread': 76},
    'XS2233188353': {'yield': 5.02, 'duration': 0.23, 'spread': 71},
    'XS2359548935': {'yield': 5.63, 'duration': 11.51, 'spread': 101},
    'XS0911024635': {'yield': 5.66, 'duration': 11.24, 'spread': 95},
    'USP0R80BAG79': {'yield': 5.87, 'duration': 5.51, 'spread': 187}
}

def analyze_bloomberg_accuracy():
    """Compare our API results vs REAL Bloomberg data"""
    
    print('🎯 REAL BLOOMBERG ACCURACY ANALYSIS')
    print('Using ACTUAL Bloomberg baseline data from user')
    print('=' * 60)
    
    # Connect to latest database
    conn = sqlite3.connect('six_way_analysis_20250722_102715.db')
    
    # Get our results
    results_df = pd.read_sql_query('''
        SELECT bond_identifier as isin, method_name, yield_pct, duration_years 
        FROM six_way_results 
        WHERE success = 1 AND yield_pct IS NOT NULL
    ''', conn)
    
    # Pivot to get methods as columns
    yield_pivot = results_df.pivot(index='isin', columns='method_name', values='yield_pct')
    duration_pivot = results_df.pivot(index='isin', columns='method_name', values='duration_years')
    
    methods = ['local_api_isin', 'local_api_desc', 'cloud_api_isin', 'cloud_api_desc', 'local_isin']
    method_names = ['Local API+ISIN', 'Local API+Desc', 'Cloud API+ISIN', 'Cloud API+Desc', 'Direct Local']
    
    print('📊 YIELD ACCURACY vs REAL BLOOMBERG (basis points):')
    print('=' * 55)
    
    for method, name in zip(methods, method_names):
        if method in yield_pivot.columns:
            # Calculate differences vs real Bloomberg
            diffs = []
            valid_bonds = []
            
            for isin in yield_pivot.index:
                if isin in REAL_BLOOMBERG_DATA and not pd.isna(yield_pivot.loc[isin, method]):
                    our_yield = yield_pivot.loc[isin, method]
                    bbg_yield = REAL_BLOOMBERG_DATA[isin]['yield']
                    diff_bp = (our_yield - bbg_yield) * 100
                    diffs.append(diff_bp)
                    valid_bonds.append(isin)
            
            if diffs:
                diffs = np.array(diffs)
                print(f'\n{name}:')
                print(f'  Mean Error: {diffs.mean():.2f} bp')
                print(f'  Max Error: {np.abs(diffs).max():.2f} bp')
                print(f'  Std Dev: {diffs.std():.2f} bp')
                
                # Accuracy metrics
                within_1bp = (np.abs(diffs) <= 1).sum()
                within_5bp = (np.abs(diffs) <= 5).sum()
                within_10bp = (np.abs(diffs) <= 10).sum()
                total = len(diffs)
                
                print(f'  Within 1bp: {within_1bp}/{total} ({within_1bp/total*100:.1f}%)')
                print(f'  Within 5bp: {within_5bp}/{total} ({within_5bp/total*100:.1f}%)')
                print(f'  Within 10bp: {within_10bp}/{total} ({within_10bp/total*100:.1f}%)')
                
                # Show worst cases
                worst_idx = np.argmax(np.abs(diffs))
                worst_isin = valid_bonds[worst_idx]
                worst_diff = diffs[worst_idx]
                print(f'  Worst case: {worst_isin} ({worst_diff:.1f}bp)')
    
    print('\n📊 DURATION ACCURACY vs REAL BLOOMBERG (years):')
    print('=' * 50)
    
    for method, name in zip(methods, method_names):
        if method in duration_pivot.columns:
            # Calculate differences vs real Bloomberg
            diffs = []
            valid_bonds = []
            
            for isin in duration_pivot.index:
                if isin in REAL_BLOOMBERG_DATA and not pd.isna(duration_pivot.loc[isin, method]):
                    our_duration = duration_pivot.loc[isin, method]
                    bbg_duration = REAL_BLOOMBERG_DATA[isin]['duration']
                    diff_years = our_duration - bbg_duration
                    diffs.append(diff_years)
                    valid_bonds.append(isin)
            
            if diffs:
                diffs = np.array(diffs)
                print(f'\n{name}:')
                print(f'  Mean Error: {diffs.mean():.4f} years')
                print(f'  Max Error: {np.abs(diffs).max():.4f} years')
                print(f'  Std Dev: {diffs.std():.4f} years')
                
                # Accuracy metrics
                within_01 = (np.abs(diffs) <= 0.1).sum()
                within_05 = (np.abs(diffs) <= 0.5).sum()
                within_1 = (np.abs(diffs) <= 1.0).sum()
                total = len(diffs)
                
                print(f'  Within 0.1yr: {within_01}/{total} ({within_01/total*100:.1f}%)')
                print(f'  Within 0.5yr: {within_05}/{total} ({within_05/total*100:.1f}%)')
                print(f'  Within 1.0yr: {within_1}/{total} ({within_1/total*100:.1f}%)')
                
                # Show worst cases
                worst_idx = np.argmax(np.abs(diffs))
                worst_isin = valid_bonds[worst_idx]
                worst_diff = diffs[worst_idx]
                print(f'  Worst case: {worst_isin} ({worst_diff:.4f}yr)')
    
    conn.close()

if __name__ == "__main__":
    analyze_bloomberg_accuracy()
