#!/usr/bin/env python3
"""
REFACTORED COMPREHENSIVE 6-WAY BOND TESTING FRAMEWORK
====================================================

REFACTORED: Now uses Universal Bond Parser to eliminate parsing redundancy.
Should fix Methods 4 & 6 (API - ISIN) that were previously failing.

This script tests the new Universal Bond Parser integration across all 6 methods:
1. Direct Local + ISIN (database lookup)
2. Direct Local - ISIN (Universal Parser) ← ENHANCED
3. Local API + ISIN (API with database)
4. Local API - ISIN (Universal Parser) ← FIXED!
5. Cloud API + ISIN (when deployed)
6. Cloud API - ISIN (Universal Parser) ← FIXED!

KEY IMPROVEMENTS:
- Universal Bond Parser eliminates parsing redundancy
- Methods 4 & 6 should now work at 100% (previously 0%)
- PANAMA bond should show consistent ~7.46% across all methods
- Single parsing codebase for consistency
"""

import sqlite3
import pandas as pd
import requests
import json
import time
from datetime import datetime
import sys
import logging
import os
import traceback

# Add core module for Universal Parser
sys.path.append('./core')
from universal_bond_parser import UniversalBondParser, BondSpecification

# Import existing calculation modules
from google_analysis10 import process_bonds_with_weightings
from treasury_detector import enhance_bond_processing_with_treasuries

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API URLs
LOCAL_API_URL = 'http://localhost:8080'
CLOUD_API_URL = 'https://future-footing-414610.uc.r.appspot.com'

# Database paths
MAIN_DB_PATH = './bonds_data.db'

# Initialize Universal Parser (eliminates redundancy!)
universal_parser = UniversalBondParser('bonds_data.db', 'validated_quantlib_bonds.db')
logger.info("🚀 Universal Bond Parser initialized - should fix Methods 4 & 6!")

def get_prior_month_end():
    """Get prior month end date for institutional settlement"""
    today = datetime.now()
    first_day_current_month = today.replace(day=1)
    last_day_previous_month = first_day_current_month - timedelta(days=1)
    return last_day_previous_month.strftime("%Y-%m-%d")

def test_method_1_direct_local_plus_isin(bond_input):
    """Method 1: Direct Local + ISIN (database lookup)"""
    try:
        isin = bond_input['isin']
        price = bond_input['price']
        
        # Use Universal Parser for ISIN lookup (standardized approach)
        bond_spec = universal_parser.parse_bond(isin, clean_price=price)
        
        if not bond_spec.parsing_success:
            return None
            
        # Convert to format expected by existing calculation engine
        bond_data = {
            'isin': bond_spec.isin,
            'description': bond_spec.description or bond_spec.issuer,
            'price': bond_spec.clean_price,
            'settlement_date': get_prior_month_end()
        }
        
        bonds_list = [bond_data]
        enhanced_bonds = enhance_bond_processing_with_treasuries(bonds_list)
        results = process_bonds_with_weightings(enhanced_bonds, use_prior_month_end=True)
        
        return results[0] if results else None
        
    except Exception as e:
        logger.error(f"Method 1 failed for {bond_input.get('isin', 'unknown')}: {e}")
        return None

def test_method_2_direct_local_minus_isin(bond_input):
    """Method 2: Direct Local - ISIN (Universal Parser description parsing)"""
    try:
        description = bond_input['description']
        price = bond_input['price']
        
        # Use Universal Parser for description parsing (proven SmartBondParser integration)
        bond_spec = universal_parser.parse_bond(description, clean_price=price)
        
        if not bond_spec.parsing_success:
            logger.warning(f"Method 2: Universal Parser failed for '{description}': {bond_spec.error_message}")
            return None
            
        # Convert to format expected by existing calculation engine
        bond_data = {
            'isin': bond_spec.isin,
            'description': bond_spec.description or bond_spec.issuer,
            'price': bond_spec.clean_price,
            'settlement_date': get_prior_month_end()
        }
        
        bonds_list = [bond_data]
        enhanced_bonds = enhance_bond_processing_with_treasuries(bonds_list)
        results = process_bonds_with_weightings(enhanced_bonds, use_prior_month_end=True)
        
        result = results[0] if results else None
        if result:
            logger.info(f"Method 2 SUCCESS: {description[:50]}... -> Yield: {result.get('yield', 'N/A')}%, Parser: {bond_spec.parser_used}")
        
        return result
        
    except Exception as e:
        logger.error(f"Method 2 failed for {bond_input.get('description', 'unknown')}: {e}")
        return None

def test_method_3_local_api_plus_isin(bond_input):
    """Method 3: Local API + ISIN (should work - existing functionality)"""
    try:
        isin = bond_input['isin']
        price = bond_input['price']
        
        payload = {
            'bond_input': isin,
            'price': price,
            'settlement_date': get_prior_month_end()
        }
        
        response = requests.post(f"{LOCAL_API_URL}/api/bond/calculate", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                # Extract results from refactored API response
                results = data.get('results', {})
                return {
                    'yield': results.get('yield'),
                    'duration': results.get('duration'),
                    'spread': results.get('spread'),
                    'clean_price': results.get('clean_price', price),
                    'parser_used': data.get('bond_specification', {}).get('parser_used', 'api')
                }
        
        logger.warning(f"Method 3 API call failed for {isin}: {response.status_code}")
        return None
        
    except Exception as e:
        logger.error(f"Method 3 failed for {bond_input.get('isin', 'unknown')}: {e}")
        return None

def test_method_4_local_api_minus_isin(bond_input):
    """Method 4: Local API - ISIN (FIXED with Universal Parser!)"""
    try:
        description = bond_input['description']
        price = bond_input['price']
        
        # This should now work with the refactored API using Universal Parser
        payload = {
            'bond_input': description,  # Description instead of ISIN
            'price': price,
            'settlement_date': get_prior_month_end()
        }
        
        response = requests.post(f"{LOCAL_API_URL}/api/bond/calculate", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                # Extract results from refactored API response
                results = data.get('results', {})
                parser_used = data.get('bond_specification', {}).get('parser_used', 'api')
                
                result = {
                    'yield': results.get('yield'),
                    'duration': results.get('duration'),
                    'spread': results.get('spread'),
                    'clean_price': results.get('clean_price', price),
                    'parser_used': parser_used
                }
                
                logger.info(f"Method 4 SUCCESS: {description[:50]}... -> Yield: {result.get('yield', 'N/A')}%, Parser: {parser_used}")
                return result
            else:
                logger.warning(f"Method 4 API returned success=false for '{description}': {data.get('error', 'unknown error')}")
        else:
            logger.warning(f"Method 4 API call failed for '{description}': {response.status_code} - {response.text}")
        
        return None
        
    except Exception as e:
        logger.error(f"Method 4 failed for '{bond_input.get('description', 'unknown')}': {e}")
        return None

def test_method_5_cloud_api_plus_isin(bond_input):
    """Method 5: Cloud API + ISIN (if deployed)"""
    try:
        isin = bond_input['isin']
        price = bond_input['price']
        
        payload = {
            'bond_input': isin,
            'price': price,
            'settlement_date': get_prior_month_end()
        }
        
        response = requests.post(f"{CLOUD_API_URL}/api/bond/calculate", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                results = data.get('results', {})
                return {
                    'yield': results.get('yield'),
                    'duration': results.get('duration'),
                    'spread': results.get('spread'),
                    'clean_price': results.get('clean_price', price),
                    'parser_used': data.get('bond_specification', {}).get('parser_used', 'cloud_api')
                }
        
        return None
        
    except Exception as e:
        logger.error(f"Method 5 failed for {bond_input.get('isin', 'unknown')}: {e}")
        return None

def test_method_6_cloud_api_minus_isin(bond_input):
    """Method 6: Cloud API - ISIN (FIXED with Universal Parser on cloud!)"""
    try:
        description = bond_input['description']
        price = bond_input['price']
        
        # This should now work if cloud deployment includes Universal Parser
        payload = {
            'bond_input': description,
            'price': price,
            'settlement_date': get_prior_month_end()
        }
        
        response = requests.post(f"{CLOUD_API_URL}/api/bond/calculate", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                results = data.get('results', {})
                parser_used = data.get('bond_specification', {}).get('parser_used', 'cloud_api')
                
                result = {
                    'yield': results.get('yield'),
                    'duration': results.get('duration'),
                    'spread': results.get('spread'),
                    'clean_price': results.get('clean_price', price),
                    'parser_used': parser_used
                }
                
                logger.info(f"Method 6 SUCCESS: {description[:50]}... -> Yield: {result.get('yield', 'N/A')}%, Parser: {parser_used}")
                return result
        
        return None
        
    except Exception as e:
        logger.error(f"Method 6 failed for '{bond_input.get('description', 'unknown')}': {e}")
        return None

def create_comprehensive_database(timestamp):
    """Create database for storing all test results"""
    db_name = f'six_way_analysis_{timestamp}.db'
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Create detailed log table
    cursor.execute("""
        CREATE TABLE test_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bond_index INTEGER,
            isin TEXT,
            bond_name TEXT,
            bloomberg_baseline_yield REAL,
            method_name TEXT,
            method_number INTEGER,
            success BOOLEAN,
            yield_result REAL,
            duration_result REAL,
            spread_result REAL,
            parser_used TEXT,
            error_message TEXT,
            timestamp TEXT
        )
    """)
    
    # Create comparison tables
    cursor.execute("""
        CREATE TABLE yield_comparison (
            bond_index INTEGER PRIMARY KEY,
            isin TEXT,
            bond_name TEXT,
            bloomberg_baseline REAL,
            method_1_direct_isin REAL,
            method_2_direct_desc REAL,
            method_3_api_isin REAL,
            method_4_api_desc REAL,
            method_5_cloud_isin REAL,
            method_6_cloud_desc REAL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE duration_comparison (
            bond_index INTEGER PRIMARY KEY,
            isin TEXT,
            bond_name TEXT,
            method_1_direct_isin REAL,
            method_2_direct_desc REAL,
            method_3_api_isin REAL,
            method_4_api_desc REAL,
            method_5_cloud_isin REAL,
            method_6_cloud_desc REAL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE spread_comparison (
            bond_index INTEGER PRIMARY KEY,
            isin TEXT,
            bond_name TEXT,
            method_1_direct_isin REAL,
            method_2_direct_desc REAL,
            method_3_api_isin REAL,
            method_4_api_desc REAL,
            method_5_cloud_isin REAL,
            method_6_cloud_desc REAL
        )
    """)
    
    conn.commit()
    conn.close()
    return db_name

def get_test_bonds():
    """Get the 25-bond test portfolio"""
    bonds = [
        {"isin": "US912810TJ79", "description": "US TREASURY N/B, 3%, 15-Aug-2052", "price": 71.66, "bloomberg_yield": 4.900000},
        {"isin": "XS2249741674", "description": "GALAXY PIPELINE, 3.25%, 30-Sep-2040", "price": 77.88, "bloomberg_yield": 5.640000},
        {"isin": "XS1709535097", "description": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047", "price": 89.40, "bloomberg_yield": 5.720000},
        {"isin": "XS1982113463", "description": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039", "price": 87.14, "bloomberg_yield": 5.600000},
        {"isin": "USP37466AS18", "description": "EMPRESA METRO, 4.7%, 07-May-2050", "price": 80.39, "bloomberg_yield": 6.270000},
        {"isin": "USP3143NAH72", "description": "CODELCO INC, 6.15%, 24-Oct-2036", "price": 101.63, "bloomberg_yield": 5.950000},
        {"isin": "USP30179BR86", "description": "COMISION FEDERAL, 6.264%, 15-Feb-2052", "price": 86.42, "bloomberg_yield": 7.440000},
        {"isin": "US195325DX04", "description": "COLOMBIA REP OF, 3.875%, 15-Feb-2061", "price": 52.71, "bloomberg_yield": 7.840000},
        {"isin": "US279158AJ82", "description": "ECOPETROL SA, 5.875%, 28-May-2045", "price": 69.31, "bloomberg_yield": 9.280000},
        {"isin": "USP37110AM89", "description": "EMPRESA NACIONAL, 4.5%, 14-Sep-2047", "price": 76.24, "bloomberg_yield": 6.540000},
        {"isin": "XS2542166231", "description": "GREENSAIF PIPELI, 6.129%, 23-Feb-2038", "price": 103.03, "bloomberg_yield": 5.720000},
        {"isin": "XS2167193015", "description": "STATE OF ISRAEL, 3.8%, 13-May-2060", "price": 64.50, "bloomberg_yield": 6.340000},
        {"isin": "XS1508675508", "description": "SAUDI INT BOND, 4.5%, 26-Oct-2046", "price": 82.42, "bloomberg_yield": 5.970000},
        {"isin": "XS1807299331", "description": "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048", "price": 92.21, "bloomberg_yield": 7.060000},
        {"isin": "US91086QAZ19", "description": "UNITED MEXICAN, 5.75%, 12-Oct-2110", "price": 78.00, "bloomberg_yield": 7.370000},
        {"isin": "USP6629MAD40", "description": "MEXICO CITY ARPT, 5.5%, 31-Jul-2047", "price": 82.57, "bloomberg_yield": 7.070000},
        {"isin": "US698299BL70", "description": "PANAMA, 3.87%, 23-Jul-2060", "price": 56.60, "bloomberg_yield": 7.360000},  # The problematic one!
        {"isin": "US71654QDF63", "description": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060", "price": 71.42, "bloomberg_yield": 9.880000},
        {"isin": "US71654QDE98", "description": "PETROLEOS MEXICA, 5.95%, 28-Jan-2031", "price": 89.55, "bloomberg_yield": 8.320000},
        {"isin": "XS2585988145", "description": "GACI FIRST INVST, 5.125%, 14-Feb-2053", "price": 85.54, "bloomberg_yield": 6.230000},
        {"isin": "XS1959337749", "description": "QATAR STATE OF, 4.817%, 14-Mar-2049", "price": 89.97, "bloomberg_yield": 5.580000},
        {"isin": "XS2233188353", "description": "QNB FINANCE LTD, 1.625%, 22-Sep-2025", "price": 99.23, "bloomberg_yield": 5.020000},
        {"isin": "XS2359548935", "description": "QATAR ENERGY, 3.125%, 12-Jul-2041", "price": 73.79, "bloomberg_yield": 5.630000},
        {"isin": "XS0911024635", "description": "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043", "price": 93.29, "bloomberg_yield": 5.660000},
        {"isin": "USP0R80BAG79", "description": "SITIOS, 5.375%, 04-Apr-2032", "price": 97.26, "bloomberg_yield": 5.870000}
    ]
    return bonds

def run_comprehensive_test():
    """Run the comprehensive 6-way test with Universal Parser"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_name = create_comprehensive_database(timestamp)
    
    logger.info(f"🚀 Starting comprehensive 6-way test with Universal Parser")
    logger.info(f"📊 Database: {db_name}")
    logger.info(f"🎯 Expected: Methods 4 & 6 should now work (previously failed)")
    
    bonds = get_test_bonds()
    test_methods = [
        ("Direct Local + ISIN", 1, test_method_1_direct_local_plus_isin),
        ("Direct Local - ISIN", 2, test_method_2_direct_local_minus_isin),
        ("Local API + ISIN", 3, test_method_3_local_api_plus_isin),
        ("Local API - ISIN", 4, test_method_4_local_api_minus_isin),  # Should be FIXED!
        ("Cloud API + ISIN", 5, test_method_5_cloud_api_plus_isin),
        ("Cloud API - ISIN", 6, test_method_6_cloud_api_minus_isin)   # Should be FIXED!
    ]
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Store all results for comparison tables
    all_results = {}
    
    for bond_idx, bond in enumerate(bonds):
        logger.info(f"\n📈 Testing Bond {bond_idx + 1}/25: {bond['description'][:50]}...")
        
        bond_results = {}
        
        for method_name, method_num, test_func in test_methods:
            logger.info(f"   Method {method_num}: {method_name}")
            
            try:
                result = test_func(bond)
                success = result is not None
                
                if success:
                    yield_val = result.get('yield')
                    duration_val = result.get('duration')
                    spread_val = result.get('spread')
                    parser_used = result.get('parser_used', 'unknown')
                    
                    logger.info(f"      ✅ Success: Yield {yield_val}%, Duration {duration_val}, Parser: {parser_used}")
                    
                    # Special logging for PANAMA bond and Methods 4/6
                    if "PANAMA" in bond['description'] and method_num in [4, 6]:
                        logger.info(f"      🎯 PANAMA Method {method_num}: {yield_val}% (Should be ~7.46%, was 24.51%)")
                        
                else:
                    yield_val = duration_val = spread_val = None
                    parser_used = 'failed'
                    logger.info(f"      ❌ Failed")
                
                # Log to database
                cursor.execute("""
                    INSERT INTO test_log 
                    (bond_index, isin, bond_name, bloomberg_baseline_yield, method_name, method_number,
                     success, yield_result, duration_result, spread_result, parser_used, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    bond_idx, bond['isin'], bond['description'], bond['bloomberg_yield'],
                    method_name, method_num, success, yield_val, duration_val, spread_val,
                    parser_used, datetime.now().isoformat()
                ))
                
                bond_results[method_num] = {
                    'yield': yield_val,
                    'duration': duration_val,
                    'spread': spread_val
                }
                
            except Exception as e:
                logger.error(f"      ❌ Exception in {method_name}: {e}")
                cursor.execute("""
                    INSERT INTO test_log 
                    (bond_index, isin, bond_name, bloomberg_baseline_yield, method_name, method_number,
                     success, error_message, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    bond_idx, bond['isin'], bond['description'], bond['bloomberg_yield'],
                    method_name, method_num, False, str(e), datetime.now().isoformat()
                ))
                
                bond_results[method_num] = {
                    'yield': None,
                    'duration': None,
                    'spread': None
                }
        
        all_results[bond_idx] = bond_results
        
        # Populate comparison tables
        cursor.execute("""
            INSERT INTO yield_comparison 
            (bond_index, isin, bond_name, bloomberg_baseline, method_1_direct_isin, method_2_direct_desc,
             method_3_api_isin, method_4_api_desc, method_5_cloud_isin, method_6_cloud_desc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            bond_idx, bond['isin'], bond['description'], bond['bloomberg_yield'],
            bond_results[1]['yield'], bond_results[2]['yield'], bond_results[3]['yield'],
            bond_results[4]['yield'], bond_results[5]['yield'], bond_results[6]['yield']
        ))
        
        cursor.execute("""
            INSERT INTO duration_comparison 
            (bond_index, isin, bond_name, method_1_direct_isin, method_2_direct_desc,
             method_3_api_isin, method_4_api_desc, method_5_cloud_isin, method_6_cloud_desc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            bond_idx, bond['isin'], bond['description'],
            bond_results[1]['duration'], bond_results[2]['duration'], bond_results[3]['duration'],
            bond_results[4]['duration'], bond_results[5]['duration'], bond_results[6]['duration']
        ))
        
        cursor.execute("""
            INSERT INTO spread_comparison 
            (bond_index, isin, bond_name, method_1_direct_isin, method_2_direct_desc,
             method_3_api_isin, method_4_api_desc, method_5_cloud_isin, method_6_cloud_desc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            bond_idx, bond['isin'], bond['description'],
            bond_results[1]['spread'], bond_results[2]['spread'], bond_results[3]['spread'],
            bond_results[4]['spread'], bond_results[5]['spread'], bond_results[6]['spread']
        ))
        
        conn.commit()
    
    # Generate summary statistics
    logger.info("\n📊 GENERATING FINAL SUMMARY")
    logger.info("=" * 50)
    
    cursor.execute("""
        SELECT method_number, method_name, 
               COUNT(*) as total_tests,
               SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_tests,
               ROUND(100.0 * SUM(CASE WHEN success THEN 1 ELSE 0 END) / COUNT(*), 1) as success_rate
        FROM test_log 
        GROUP BY method_number, method_name 
        ORDER BY method_number
    """)
    
    method_stats = cursor.fetchall()
    
    for method_stat in method_stats:
        method_num, method_name, total, successful, success_rate = method_stat
        status = "✅" if success_rate == 100.0 else "⚠️" if success_rate > 0 else "❌"
        logger.info(f"{status} Method {method_num}: {method_name:<20} {successful}/{total} ({success_rate}%)")
    
    # Check for PANAMA bond results
    cursor.execute("""
        SELECT method_number, method_name, yield_result 
        FROM test_log 
        WHERE bond_name LIKE '%PANAMA%' AND success = 1
        ORDER BY method_number
    """)
    
    panama_results = cursor.fetchall()
    if panama_results:
        logger.info(f"\n🎯 PANAMA BOND RESULTS (Should be consistent ~7.46%):")
        for method_num, method_name, yield_val in panama_results:
            logger.info(f"   Method {method_num}: {yield_val:.6f}%")
    
    conn.close()
    
    logger.info(f"\n🎉 COMPREHENSIVE TEST COMPLETE!")
    logger.info(f"📊 Results saved to: {db_name}")
    logger.info(f"🚀 Universal Parser integration should have fixed Methods 4 & 6!")
    
    return db_name

if __name__ == "__main__":
    try:
        # Import necessary modules
        from datetime import timedelta
        
        logger.info("🚀 REFACTORED 6-WAY COMPREHENSIVE BOND TESTER")
        logger.info("=" * 60)
        logger.info("✅ Universal Bond Parser integrated")
        logger.info("🎯 Should fix Methods 4 & 6 (API - ISIN)")
        logger.info("📊 PANAMA bond should show consistent results")
        logger.info("")
        
        db_name = run_comprehensive_test()
        
        logger.info(f"\n✅ SUCCESS! Test completed successfully")
        logger.info(f"📊 Database: {db_name}")
        logger.info(f"🔍 Check the database for detailed results")
        logger.info(f"🎯 Expected: 6/6 methods at 100% success rate")
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        logger.error(traceback.format_exc())
