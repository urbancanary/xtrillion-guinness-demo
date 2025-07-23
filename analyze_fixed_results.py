#!/usr/bin/env python3
"""
FIXED RESULTS ANALYSIS: Real Bloomberg vs Fixed Direct Local Method
==================================================================
Analyzes the FIXED database to validate that Direct Local now matches APIs
"""

import sqlite3
import pandas as pd
import numpy as np

# REAL Bloomberg baseline data provided by user on 2025-07-22
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

def analyze_fixed_results():
    """Compare FIXED results vs REAL Bloomberg and show if Direct Local matches APIs"""
    
    print('🔧 FIXED RESULTS ANALYSIS vs REAL BLOOMBERG')
    print('Testing if Direct Local now matches API performance')
    print('=' * 70)
    
    # Connect to the FIXED database
    conn = sqlite3.connect('six_way_analysis_FIXED_20250722_104353.db')
    
    # Get our results
    results_df = pd.read_sql_query('''
        SELECT bond_identifier as isin, method_name, yield_pct, duration_years, success
        FROM six_way_results 
        WHERE yield_pct IS NOT NULL
    ''', conn)
    
    # Pivot to get methods as columns
    yield_pivot = results_df.pivot(index='isin', columns='method_name', values='yield_pct')
    duration_pivot = results_df.pivot(index='isin', columns='method_name', values='duration_years')
    
    print('📊 ARCHITECTURE FIX VALIDATION:')
    print('=' * 40)
    
    # Check if local_isin now matches local_api_isin
    if 'local_isin' in yield_pivot.columns and 'local_api_isin' in yield_pivot.columns:
        yield_diffs = []
        duration_diffs = []
        
        for isin in yield_pivot.index:
            if not pd.isna(yield_pivot.loc[isin, 'local_isin']) and not pd.isna(yield_pivot.loc[isin, 'local_api_isin']):
                yield_diff = abs(yield_pivot.loc[isin, 'local_isin'] - yield_pivot.loc[isin, 'local_api_isin']) * 100
                yield_diffs.append(yield_diff)
                
            if not pd.isna(duration_pivot.loc[isin, 'local_isin']) and not pd.isna(duration_pivot.loc[isin, 'local_api_isin']):
                duration_diff = abs(duration_pivot.loc[isin, 'local_isin'] - duration_pivot.loc[isin, 'local_api_isin'])
                duration_diffs.append(duration_diff)
        
        if yield_diffs:
            yield_diffs = np.array(yield_diffs)
            duration_diffs = np.array(duration_diffs)
            
            print(f'🎯 DIRECT LOCAL vs LOCAL API COMPARISON:')
            print(f'   Yield Difference: Mean {yield_diffs.mean():.3f}bp, Max {yield_diffs.max():.3f}bp')
            print(f'   Duration Difference: Mean {duration_diffs.mean():.4f}yr, Max {duration_diffs.max():.4f}yr')
            
            if yield_diffs.max() < 0.1 and duration_diffs.max() < 0.001:
                print('   ✅ SUCCESS: Direct Local now matches APIs perfectly!')
            elif yield_diffs.max() < 1 and duration_diffs.max() < 0.01:
                print('   ✅ GOOD: Direct Local now very close to APIs')
            else:
                print('   ⚠️ PARTIAL: Some differences remain')
    
    print('\n📊 PERFORMANCE vs REAL BLOOMBERG:')
    print('=' * 40)
    
    methods = ['local_isin', 'local_desc', 'local_api_isin', 'local_api_desc', 'cloud_api_isin', 'cloud_api_desc']
    method_names = ['Fixed Direct+ISIN', 'Fixed Direct+Desc', 'Local API+ISIN', 'Local API+Desc', 'Cloud API+ISIN', 'Cloud API+Desc']
    
    for method, name in zip(methods, method_names):
        if method in yield_pivot.columns:
            # Calculate differences vs real Bloomberg
            yield_diffs = []
            duration_diffs = []
            
            for isin in yield_pivot.index:
                if isin in REAL_BLOOMBERG_DATA and not pd.isna(yield_pivot.loc[isin, method]):
                    our_yield = yield_pivot.loc[isin, method]
                    bbg_yield = REAL_BLOOMBERG_DATA[isin]['yield']
                    yield_diff_bp = (our_yield - bbg_yield) * 100
                    yield_diffs.append(yield_diff_bp)
                    
                if isin in REAL_BLOOMBERG_DATA and not pd.isna(duration_pivot.loc[isin, method]):
                    our_duration = duration_pivot.loc[isin, method]
                    bbg_duration = REAL_BLOOMBERG_DATA[isin]['duration']
                    duration_diff = our_duration - bbg_duration
                    duration_diffs.append(duration_diff)
            
            if yield_diffs:
                yield_diffs = np.array(yield_diffs)
                duration_diffs = np.array(duration_diffs)
                
                print(f'\n{name}:')
                print(f'  Yield: Mean {yield_diffs.mean():.1f}bp, Std {yield_diffs.std():.1f}bp, Max {np.abs(yield_diffs).max():.1f}bp')
                print(f'  Duration: Mean {duration_diffs.mean():.3f}yr, Std {duration_diffs.std():.3f}yr, Max {np.abs(duration_diffs).max():.3f}yr')
                
                # Accuracy metrics
                within_5bp = (np.abs(yield_diffs) <= 5).sum()
                within_10bp = (np.abs(yield_diffs) <= 10).sum()
                within_05yr = (np.abs(duration_diffs) <= 0.5).sum()
                total = len(yield_diffs)
                
                print(f'  Accuracy: {within_5bp}/{total} within 5bp ({within_5bp/total*100:.1f}%), {within_05yr}/{total} within 0.5yr ({within_05yr/total*100:.1f}%)')
    
    print('\n🎯 BOTTOM LINE ASSESSMENT:')
    print('=' * 30)
    
    # Check success rates
    success_summary = results_df.groupby('method_name')['success'].agg(['count', 'sum']).reset_index()
    success_summary['success_rate'] = success_summary['sum'] / success_summary['count'] * 100
    
    for _, row in success_summary.iterrows():
        print(f'{row["method_name"]}: {row["sum"]}/{row["count"]} ({row["success_rate"]:.1f}% success)')
    
    print('\n✅ ARCHITECTURE FIX STATUS:')
    if 'local_isin' in yield_pivot.columns and 'local_api_isin' in yield_pivot.columns:
        if yield_diffs.max() < 1:
            print('   🎉 SUCCESS: Direct Local method now uses same engine as APIs!')
            print('   🚀 Ready for cloud deployment - no version mismatch!')
        else:
            print('   ⚠️ PARTIAL: Some improvement but differences remain')
    
    conn.close()

if __name__ == "__main__":
    analyze_fixed_results()
