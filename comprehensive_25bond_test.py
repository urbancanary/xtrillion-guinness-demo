#!/usr/bin/env python3
"""
🎯 COMPREHENSIVE 25-BOND 6-WAY TESTING - EDGE CASE HUNTER
Tests all 25 bonds across 6 methods to identify calculation edge cases
"""

import sqlite3
import pandas as pd
import numpy as np
import requests
import json
import time
from datetime import datetime
import sys
import logging
import os

# Set up logging to capture edge case details
logging.basicConfig(level=logging.WARNING)

def main():
    print('🔍 COMPREHENSIVE 25-BOND EDGE CASE TESTING')
    print('=' * 60)
    
    # Connect to our analysis database
    db_name = 'six_way_bond_analysis_20250722_090157.db'
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Generate unique test run ID for 25-bond test
    test_run_id = f'run_25bonds_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    print(f'🆔 25-Bond Test Run ID: {test_run_id}')
    
    # Find main database
    main_db_path = 'bonds_data.db'
    if not os.path.exists(main_db_path):
        print('❌ bonds_data.db not found')
        return
    print(f'📂 Using database: {main_db_path}')
    
    # Test configuration
    LOCAL_API_URL = 'http://localhost:8080'
    CLOUD_API_URL = 'https://future-footing-414610.uc.r.appspot.com'
    
    # Get all 25 baseline bonds
    cursor.execute('SELECT isin, description, price, trade_date, weighting FROM baseline_bonds ORDER BY isin')
    baseline_bonds = cursor.fetchall()
    print(f'📊 Testing {len(baseline_bonds)} bonds across 6 methods = {len(baseline_bonds) * 6} total tests')
    
    # Insert test metadata
    cursor.execute('''
    INSERT INTO test_metadata (test_run_id, start_time, total_bonds_tested, notes)
    VALUES (?, ?, ?, ?)
    ''', (test_run_id, datetime.now().isoformat(), len(baseline_bonds), '25-bond comprehensive edge case testing'))
    
    # Edge case tracking
    edge_cases = {
        'ultra_short_duration': [],  # < 1 year
        'ultra_long_duration': [],   # > 20 years
        'negative_spreads': [],      # < 0 bps
        'extreme_spreads': [],       # > 500 bps
        'distressed_bonds': [],      # price < 60
        'premium_bonds': [],         # price > 100
        'calculation_errors': [],    # failed calculations
        'parsing_failures': [],      # name parsing issues
        'extreme_yields': []         # < 2% or > 10%
    }
    
    def store_result(bond_id, method_name, method_num, input_type, success, result_data, error_msg=None, proc_time=None):
        """Store test result and track edge cases"""
        yield_val = result_data.get('yield') if result_data and success else None
        duration_val = result_data.get('duration') if result_data and success else None
        spread_val = result_data.get('spread') if result_data and success else None
        accrued_val = result_data.get('accrued_interest') if result_data and success else None
        bond_name = result_data.get('name') if result_data and success else None
        
        # Track edge cases for successful calculations
        if success and result_data:
            bond_info = f"{bond_id} ({bond_name})"
            
            # Duration edge cases
            if duration_val and duration_val < 1.0:
                edge_cases['ultra_short_duration'].append((bond_info, duration_val))
            elif duration_val and duration_val > 20.0:
                edge_cases['ultra_long_duration'].append((bond_info, duration_val))
            
            # Spread edge cases  
            if spread_val and spread_val < 0:
                edge_cases['negative_spreads'].append((bond_info, spread_val))
            elif spread_val and spread_val > 500:
                edge_cases['extreme_spreads'].append((bond_info, spread_val))
            
            # Yield edge cases
            if yield_val and (yield_val < 2.0 or yield_val > 10.0):
                edge_cases['extreme_yields'].append((bond_info, yield_val))
        
        # Track failures
        if not success:
            if 'parsing' in error_msg.lower() or 'empty results' in error_msg.lower():
                edge_cases['parsing_failures'].append((bond_id, error_msg))
            else:
                edge_cases['calculation_errors'].append((bond_id, error_msg))
        
        cursor.execute('''
        INSERT INTO six_way_results 
        (test_run_id, bond_identifier, method_name, method_number, input_type, 
         success, yield_pct, duration_years, spread_bps, accrued_interest, 
         bond_name, error_message, processing_time_ms)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (test_run_id, bond_id, method_name, method_num, input_type, 
              success, yield_val, duration_val, spread_val, accrued_val,
              bond_name, error_msg, proc_time))
    
    def test_direct_local(bond_data, use_isin=True):
        """Test direct local calculation with proper parameters"""
        try:
            sys.path.append('.')
            from google_analysis10 import process_bonds_with_weightings
            
            if use_isin:
                test_data = pd.DataFrame([{
                    'BOND_CD': bond_data[0],  # ISIN
                    'CLOSING PRICE': bond_data[2],
                    'Inventory Date': bond_data[3],
                    'WEIGHTING': bond_data[4]
                }])
            else:
                test_data = pd.DataFrame([{
                    'BOND_ENAME': bond_data[1],  # Description
                    'CLOSING PRICE': bond_data[2],
                    'Inventory Date': bond_data[3], 
                    'WEIGHTING': bond_data[4]
                }])
            
            start_time = time.time()
            results = process_bonds_with_weightings(test_data, main_db_path, record_number=1)
            proc_time = (time.time() - start_time) * 1000
            
            if not results.empty and len(results) > 0:
                result = results.iloc[0].to_dict()
                return True, result, None, proc_time
            else:
                return False, None, 'Empty results returned', proc_time
                
        except Exception as e:
            return False, None, str(e), None
    
    def test_api(api_url, bond_data, use_isin=True):
        """Test API endpoint with timeout protection"""
        try:
            if use_isin:
                payload = {
                    'data': [{
                        'BOND_CD': bond_data[0],
                        'CLOSING PRICE': bond_data[2],
                        'Inventory Date': bond_data[3],
                        'WEIGHTING': bond_data[4]
                    }]
                }
            else:
                payload = {
                    'data': [{
                        'BOND_ENAME': bond_data[1],
                        'CLOSING PRICE': bond_data[2],
                        'Inventory Date': bond_data[3],
                        'WEIGHTING': bond_data[4]
                    }]
                }
            
            start_time = time.time()
            response = requests.post(f'{api_url}/api/v1/portfolio/analyze', 
                                   json=payload, timeout=30)
            proc_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and len(data['results']) > 0:
                    return True, data['results'][0], None, proc_time
                else:
                    return False, None, f'No results in API response', proc_time
            else:
                return False, None, f'API error {response.status_code}', proc_time
                
        except requests.exceptions.RequestException as e:
            return False, None, f'Network error: {str(e)[:100]}', None
        except Exception as e:
            return False, None, str(e)[:100], None
    
    # Test all 25 bonds across all 6 methods
    total_tests = 0
    successful_tests = 0
    bond_count = 0
    
    # Track progress and edge case bonds
    print('\n🧪 STARTING COMPREHENSIVE TESTING...')
    print('Legend: ✅=Success ❌=Fail ⚠️=Edge Case')
    
    for i, bond in enumerate(baseline_bonds):
        isin, description, price, trade_date, weighting = bond
        bond_count += 1
        
        # Identify potential edge cases upfront
        edge_markers = []
        if price < 60:
            edge_markers.append('DISTRESSED')
            edge_cases['distressed_bonds'].append((isin, price))
        if price > 100:
            edge_markers.append('PREMIUM')  
            edge_cases['premium_bonds'].append((isin, price))
        
        edge_suffix = f" [{'/'.join(edge_markers)}]" if edge_markers else ""
        
        print(f'\n🧪 Bond {bond_count}/{len(baseline_bonds)}: {isin}{edge_suffix}')
        print(f'📋 {description[:55]}... @ {price}')
        
        # Method 1: Direct Local + ISIN
        print('  M1: Local+ISIN...', end=' ')
        success, result, error, proc_time = test_direct_local(bond, use_isin=True)
        store_result(isin, 'Direct Local + ISIN', 1, 'ISIN', success, result, error, proc_time)
        total_tests += 1
        if success:
            successful_tests += 1
            y, d, s = result.get("yield", 0), result.get("duration", 0), result.get("spread", 0)
            edge_flag = ""
            if d and (d < 1 or d > 20): edge_flag += "⚠️D"
            if s and (s < 0 or s > 500): edge_flag += "⚠️S" 
            if y and (y < 2 or y > 10): edge_flag += "⚠️Y"
            print(f'✅ Y:{y:.2f}% D:{d:.1f}y S:{s:.0f}bp {edge_flag}')
        else:
            print(f'❌ {error[:30]}...')
        
        # Method 2: Direct Local + DESC  
        print('  M2: Local+DESC...', end=' ')
        success, result, error, proc_time = test_direct_local(bond, use_isin=False)
        store_result(isin, 'Direct Local + DESC', 2, 'DESCRIPTION', success, result, error, proc_time)
        total_tests += 1
        if success:
            successful_tests += 1
            y, d, s = result.get("yield", 0), result.get("duration", 0), result.get("spread", 0)
            print(f'✅ Y:{y:.2f}% D:{d:.1f}y S:{s:.0f}bp')
        else:
            print(f'❌ {error[:30]}...')
        
        # Method 3: Local API + ISIN
        print('  M3: API+ISIN...', end=' ')
        success, result, error, proc_time = test_api(LOCAL_API_URL, bond, use_isin=True)
        store_result(isin, 'Local API + ISIN', 3, 'ISIN', success, result, error, proc_time)
        total_tests += 1
        if success:
            successful_tests += 1
            y, d, s = result.get("yield", 0), result.get("duration", 0), result.get("spread", 0)
            print(f'✅ Y:{y:.2f}% D:{d:.1f}y S:{s:.0f}bp')
        else:
            print(f'❌ {error[:30]}...')
        
        # Method 4: Local API + DESC
        print('  M4: API+DESC...', end=' ')
        success, result, error, proc_time = test_api(LOCAL_API_URL, bond, use_isin=False)
        store_result(isin, 'Local API + DESC', 4, 'DESCRIPTION', success, result, error, proc_time)
        total_tests += 1
        if success:
            successful_tests += 1
            y, d, s = result.get("yield", 0), result.get("duration", 0), result.get("spread", 0)
            print(f'✅ Y:{y:.2f}% D:{d:.1f}y S:{s:.0f}bp')
        else:
            print(f'❌ {error[:30]}...')
        
        # Method 5: Cloud API + ISIN
        print('  M5: Cloud+ISIN...', end=' ')
        success, result, error, proc_time = test_api(CLOUD_API_URL, bond, use_isin=True)
        store_result(isin, 'Cloud API + ISIN', 5, 'ISIN', success, result, error, proc_time)
        total_tests += 1
        if success:
            successful_tests += 1
            y, d, s = result.get("yield", 0), result.get("duration", 0), result.get("spread", 0)
            print(f'✅ Y:{y:.2f}% D:{d:.1f}y S:{s:.0f}bp')
        else:
            print(f'❌ {error[:30]}...')
        
        # Method 6: Cloud API + DESC
        print('  M6: Cloud+DESC...', end=' ')
        success, result, error, proc_time = test_api(CLOUD_API_URL, bond, use_isin=False)
        store_result(isin, 'Cloud API + DESC', 6, 'DESCRIPTION', success, result, error, proc_time)
        total_tests += 1
        if success:
            successful_tests += 1
            y, d, s = result.get("yield", 0), result.get("duration", 0), result.get("spread", 0)
            print(f'✅ Y:{y:.2f}% D:{d:.1f}y S:{s:.0f}bp')
        else:
            print(f'❌ {error[:30]}...')
        
        # Commit after each bond
        conn.commit()
    
    # Update test metadata
    cursor.execute('''
    UPDATE test_metadata 
    SET end_time = ?, successful_methods = ?
    WHERE test_run_id = ?
    ''', (datetime.now().isoformat(), successful_tests, test_run_id))
    
    conn.commit()
    
    print(f'\n📊 25-BOND COMPREHENSIVE TEST SUMMARY')
    print('=' * 60)
    print(f'✅ Total Tests: {total_tests}')
    print(f'✅ Successful: {successful_tests} ({successful_tests/total_tests*100:.1f}%)')
    print(f'❌ Failed: {total_tests - successful_tests}')
    
    # Success by method summary
    cursor.execute('''
    SELECT method_name, COUNT(*) as total, SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful
    FROM six_way_results 
    WHERE test_run_id = ?
    GROUP BY method_name
    ORDER BY method_number
    ''', (test_run_id,))
    
    print(f'\n📈 SUCCESS BY METHOD:')
    for row in cursor.fetchall():
        method, total, successful = row
        success_rate = (successful/total*100) if total > 0 else 0
        print(f'  {method:<20}: {successful}/{total} ({success_rate:.0f}%)')
    
    # EDGE CASE ANALYSIS
    print(f'\n🔍 EDGE CASE ANALYSIS')
    print('=' * 60)
    
    # Report edge cases found
    if edge_cases['ultra_short_duration']:
        print(f'⚠️  ULTRA SHORT DURATION (< 1y): {len(edge_cases["ultra_short_duration"])} bonds')
        for bond, duration in edge_cases['ultra_short_duration']:
            print(f'    {bond}: {duration:.3f} years')
    
    if edge_cases['ultra_long_duration']:
        print(f'⚠️  ULTRA LONG DURATION (> 20y): {len(edge_cases["ultra_long_duration"])} bonds')
        for bond, duration in edge_cases['ultra_long_duration']:
            print(f'    {bond}: {duration:.1f} years')
    
    if edge_cases['negative_spreads']:
        print(f'⚠️  NEGATIVE SPREADS: {len(edge_cases["negative_spreads"])} bonds')
        for bond, spread in edge_cases['negative_spreads']:
            print(f'    {bond}: {spread:.0f} bps')
    
    if edge_cases['extreme_spreads']:
        print(f'⚠️  EXTREME SPREADS (> 500bp): {len(edge_cases["extreme_spreads"])} bonds')
        for bond, spread in edge_cases['extreme_spreads']:
            print(f'    {bond}: {spread:.0f} bps')
    
    if edge_cases['extreme_yields']:
        print(f'⚠️  EXTREME YIELDS (< 2% or > 10%): {len(edge_cases["extreme_yields"])} bonds')
        for bond, yield_val in edge_cases['extreme_yields']:
            print(f'    {bond}: {yield_val:.2f}%')
    
    if edge_cases['distressed_bonds']:
        print(f'⚠️  DISTRESSED BONDS (< 60 price): {len(edge_cases["distressed_bonds"])} bonds')
        for bond, price in edge_cases['distressed_bonds']:
            print(f'    {bond}: {price}')
    
    if edge_cases['premium_bonds']:
        print(f'⚠️  PREMIUM BONDS (> 100 price): {len(edge_cases["premium_bonds"])} bonds')
        for bond, price in edge_cases['premium_bonds']:
            print(f'    {bond}: {price}')
    
    conn.close()
    print(f'\n🎯 Results saved to: {db_name}')
    print(f'📊 Test Run ID: {test_run_id}')
    print('🚀 EDGE CASE HUNTING COMPLETE!')

if __name__ == "__main__":
    main()
