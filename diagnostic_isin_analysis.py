#!/usr/bin/env python3
"""
Diagnostic tool to investigate ISIN vs non-ISIN calculation differences.
This tool provides detailed analysis of evaluation dates, settlement dates, and conventions.
"""

import sqlite3
import pandas as pd
import json
from datetime import datetime

def analyze_calculation_differences():
    """Analyze the specific causes of ISIN vs non-ISIN differences."""
    
    # Connect to the latest results database
    import glob
    import os
    
    db_files = glob.glob('six_way_analysis_FIXED_*.db')
    if not db_files:
        print("❌ No results database found")
        return
    
    latest_db = max(db_files, key=os.path.getctime)
    print(f"📊 Analyzing database: {latest_db}")
    
    conn = sqlite3.connect(latest_db)
    
    # Get all results
    results_df = pd.read_sql_query("SELECT * FROM test_log", conn)
    conn.close()
    
    print("\n" + "="*100)
    print("🔬 DIAGNOSTIC: ISIN vs Non-ISIN Calculation Differences")
    print("="*100)
    
    # Find bonds with both Method 1 (ISIN) and Method 2 (non-ISIN) results
    all_bonds = results_df['Description'].unique()
    
    print(f"\n📊 Total bonds analyzed: {len(all_bonds)}")
    
    # Detailed analysis for each bond
    analysis_results = []
    
    for desc in all_bonds:
        # Method 1: Local+ISIN (with ISIN)
        method1_results = results_df[(results_df['Description'] == desc) & (results_df['Method'] == 'Method 1: Local+ISIN')]
        
        # Method 2: Local-ISIN (without ISIN)
        method2_results = results_df[(results_df['Description'] == desc) & (results_df['Method'] == 'Method 2: Local-ISIN')]
        
        if len(method1_results) > 0 and len(method2_results) > 0:
            # Get the primary results - Method 1 vs Method 2
            method1_result = method1_results.iloc[0]
            method2_result = method2_results.iloc[0]
            
            # Calculate differences
            yield_diff = None
            duration_diff = None
            
            if pd.notna(method1_result['Yield']) and pd.notna(method2_result['Yield']):
                yield_diff = abs(method1_result['Yield'] - method2_result['Yield'])
            
            if pd.notna(method1_result['Duration']) and pd.notna(method2_result['Duration']):
                duration_diff = abs(method1_result['Duration'] - method2_result['Duration'])
            
            # Parse conventions
            method1_conventions = {}
            method2_conventions = {}
            
            try:
                if pd.notna(method1_result['Conventions']):
                    method1_conventions = eval(method1_result['Conventions'])
            except:
                method1_conventions = {}
            
            try:
                if pd.notna(method2_result['Conventions']):
                    method2_conventions = eval(method2_result['Conventions'])
            except:
                method2_conventions = {}
            
            # Convention comparison
            convention_diff_keys = []
            for key in set(list(method1_conventions.keys()) + list(method2_conventions.keys())):
                m1_val = method1_conventions.get(key)
                m2_val = method2_conventions.get(key)
                if m1_val != m2_val:
                    convention_diff_keys.append(key)
            
            analysis_results.append({
                'description': desc,
                'isin': method1_result['ISIN'],
                'yield_diff': yield_diff,
                'duration_diff': duration_diff,
                'method1_yield': method1_result['Yield'],
                'method2_yield': method2_result['Yield'],
                'method1_duration': method1_result['Duration'],
                'method2_duration': method2_result['Duration'],
                'method1_conventions': method1_conventions,
                'method2_conventions': method2_conventions,
                'convention_diff_keys': convention_diff_keys,
                'convention_diff_count': len(convention_diff_keys)
            })
    
    # Print detailed analysis
    print(f"\n🔍 DETAILED ANALYSIS:")
    print("-" * 120)
    
    for result in analysis_results:
        print(f"\n📈 {result['description']}")
        print(f"   ISIN: {result['isin']}")
        
        if result['yield_diff'] is not None:
            print(f"   Yield Difference: {result['yield_diff']*100:.2f} bp (M1: {result['method1_yield']:.4f}, M2: {result['method2_yield']:.4f})")
        
        if result['duration_diff'] is not None:
            print(f"   Duration Difference: {result['duration_diff']:.4f} (M1: {result['method1_duration']:.4f}, M2: {result['method2_duration']:.4f})")
        
        if result['convention_diff_count'] > 0:
            print(f"   Convention Differences ({result['convention_diff_count']}):")
            for key in result['convention_diff_keys']:
                isin_val = result['method1_conventions'].get(key, 'N/A')
                non_isin_val = result['method2_conventions'].get(key, 'N/A')
                print(f"     {key}: Method 1={isin_val} vs Method 2={non_isin_val}")
        else:
            print("   ✅ Conventions match")
        
        print("-" * 80)
    
    # Summary statistics
    print(f"\n📊 SUMMARY STATISTICS:")
    print(f"Total bonds with both ISIN and non-ISIN results: {len(analysis_results)}")
    
    yield_diffs = [r['yield_diff'] for r in analysis_results if r['yield_diff'] is not None]
    if yield_diffs:
        print(f"Average yield difference: {sum(yield_diffs)/len(yield_diffs)*100:.2f} bp")
        print(f"Max yield difference: {max(yield_diffs)*100:.2f} bp")
    
    duration_diffs = [r['duration_diff'] for r in analysis_results if r['duration_diff'] is not None]
    if duration_diffs:
        print(f"Average duration difference: {sum(duration_diffs)/len(duration_diffs):.4f}")
        print(f"Max duration difference: {max(duration_diffs):.4f}")
    
    convention_diffs = [r['convention_diff_count'] for r in analysis_results]
    if convention_diffs:
        print(f"Average convention differences: {sum(convention_diffs)/len(convention_diffs):.1f}")
        bonds_with_convention_diffs = sum(1 for r in analysis_results if r['convention_diff_count'] > 0)
        print(f"Bonds with convention differences: {bonds_with_convention_diffs}/{len(analysis_results)}")

if __name__ == "__main__":
    analyze_calculation_differences()
