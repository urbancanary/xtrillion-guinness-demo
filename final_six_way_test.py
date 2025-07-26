#!/usr/bin/env python3
"""
🎯 FINAL WORKING 6-Way Comprehensive Bond Testing with Database Storage
Fixed record_number issue - should get successful results!
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

# Set up logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise

def main():
    print('🎯 FINAL WORKING 6-WAY BOND TEST')
    print('=' * 50)
    
    # Connect to our analysis database
    db_name = 'six_way_bond_analysis_20250722_090157.db'
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Generate unique test run ID
    test_run_id = f'run_{datetime.now().strftime("%Y%m%d_%H%M%S")}_final'
    print(f'🆔 Test Run ID: {test_run_id}')
    
    # Find main database
    main_db_path = 'bonds_data.db'
    if not os.path.exists(main_db_path):
        print('❌ bonds_data.db not found')
        return
    print(f'📂 Using database: {main_db_path}')
    
    # Test configuration
    LOCAL_API_URL = 'http://localhost:8080'
    CLOUD_API_URL = 'https://future-footing-414610.uc.r.appspot.com'
    
    # Get baseline bonds
    cursor.execute('SELECT isin, description, price, trade_date, weighting FROM baseline_bonds')
    baseline_bonds = cursor.fetchall()
    print(f'📊 Testing {len(baseline_bonds)} bonds across 6 methods')
    
    # Insert test metadata
    cursor.execute('''
    INSERT INTO test_metadata (test_run_id, start_time, total_bonds_tested, notes)
    VALUES (?, ?, ?, ?)
    ''', (test_run_id, datetime.now().isoformat(), len(baseline_bonds), 'FINAL working version with record_number fix'))
    
    def store_result(bond_id, method_name, method_num, input_type, success, result_data, error_msg=None, proc_time=None):
        """Store test result in database"""
        yield_val = result_data.get('yield') if result_data and success else None
        duration_val = result_data.get('duration') if result_data and success else None
        spread_val = result_data.get('spread') if result_data and success else None
        accrued_val = result_data.get('accrued_interest') if result_data and success else None
        bond_name = result_data.get('name') if result_data and success else None
        
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
            # FIXED: Add required db_path AND record_number parameters
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
        """Test API endpoint"""
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
    
    # Test all bonds across all methods
    total_tests = 0
    successful_tests = 0
    
    for i, bond in enumerate(baseline_bonds):
        isin, description, price, trade_date, weighting = bond
        print(f'\n🧪 Bond {i+1}/{len(baseline_bonds)}: {isin}')
        print(f'📋 {description[:50]}...')
        
        # Method 1: Direct Local + ISIN
        print('  M1: Local+ISIN...', end=' ')
        success, result, error, proc_time = test_direct_local(bond, use_isin=True)
        store_result(isin, 'Direct Local + ISIN', 1, 'ISIN', success, result, error, proc_time)
        total_tests += 1
        if success:
            successful_tests += 1
            print(f'✅ Y:{result.get("yield", 0):.2f}% D:{result.get("duration", 0):.1f}y S:{result.get("spread", 0):.0f}bp')
        else:
            print(f'❌ {error[:30]}...')
        
        # Method 2: Direct Local + DESC
        print('  M2: Local+DESC...', end=' ')
        success, result, error, proc_time = test_direct_local(bond, use_isin=False)
        store_result(isin, 'Direct Local + DESC', 2, 'DESCRIPTION', success, result, error, proc_time)
        total_tests += 1
        if success:
            successful_tests += 1
            print(f'✅ Y:{result.get("yield", 0):.2f}% D:{result.get("duration", 0):.1f}y S:{result.get("spread", 0):.0f}bp')
        else:
            print(f'❌ {error[:30]}...')
        
        # Method 3: Local API + ISIN
        print('  M3: API+ISIN...', end=' ')
        success, result, error, proc_time = test_api(LOCAL_API_URL, bond, use_isin=True)
        store_result(isin, 'Local API + ISIN', 3, 'ISIN', success, result, error, proc_time)
        total_tests += 1
        if success:
            successful_tests += 1
            print(f'✅ Y:{result.get("yield", 0):.2f}% D:{result.get("duration", 0):.1f}y S:{result.get("spread", 0):.0f}bp')
        else:
            print(f'❌ {error[:30]}...')
        
        # Method 4: Local API + DESC
        print('  M4: API+DESC...', end=' ')
        success, result, error, proc_time = test_api(LOCAL_API_URL, bond, use_isin=False)
        store_result(isin, 'Local API + DESC', 4, 'DESCRIPTION', success, result, error, proc_time)
        total_tests += 1
        if success:
            successful_tests += 1
            print(f'✅ Y:{result.get("yield", 0):.2f}% D:{result.get("duration", 0):.1f}y S:{result.get("spread", 0):.0f}bp')
        else:
            print(f'❌ {error[:30]}...')
        
        # Method 5: Cloud API + ISIN
        print('  M5: Cloud+ISIN...', end=' ')
        success, result, error, proc_time = test_api(CLOUD_API_URL, bond, use_isin=True)
        store_result(isin, 'Cloud API + ISIN', 5, 'ISIN', success, result, error, proc_time)
        total_tests += 1
        if success:
            successful_tests += 1
            print(f'✅ Y:{result.get("yield", 0):.2f}% D:{result.get("duration", 0):.1f}y S:{result.get("spread", 0):.0f}bp')
        else:
            print(f'❌ {error[:30]}...')
        
        # Method 6: Cloud API + DESC
        print('  M6: Cloud+DESC...', end=' ')
        success, result, error, proc_time = test_api(CLOUD_API_URL, bond, use_isin=False)
        store_result(isin, 'Cloud API + DESC', 6, 'DESCRIPTION', success, result, error, proc_time)
        total_tests += 1
        if success:
            successful_tests += 1
            print(f'✅ Y:{result.get("yield", 0):.2f}% D:{result.get("duration", 0):.1f}y S:{result.get("spread", 0):.0f}bp')
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
    
    print(f'\n📊 FINAL TEST SUMMARY')
    print(f'✅ Total Tests: {total_tests}')
    print(f'✅ Successful: {successful_tests} ({successful_tests/total_tests*100:.1f}%)')
    print(f'❌ Failed: {total_tests - successful_tests}')
    
    # Show what we stored
    cursor.execute('SELECT COUNT(*) FROM six_way_results WHERE test_run_id = ?', (test_run_id,))
    stored_results = cursor.fetchone()[0]
    print(f'💾 Stored Results: {stored_results}')
    
    # Quick success by method summary
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
    
    conn.close()
    print(f'\n🎯 Results saved to: {db_name}')
    print('🚀 READY FOR COMPARISON ANALYSIS!')

if __name__ == "__main__":
    main()
