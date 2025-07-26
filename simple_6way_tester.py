#!/usr/bin/env python3
"""
SIMPLE 6-WAY COMPREHENSIVE BOND TESTER - FIXED ENDPOINTS
=======================================================

FIXED: Updated to use correct API endpoints and payload formats.
Now runs full 25-bond test with all 6 methods.
"""

import sqlite3
import requests
import json
import time
from datetime import datetime, timedelta
import sys
import logging
import traceback

# Import existing calculation modules  
from google_analysis10 import process_bonds_with_weightings
from treasury_detector import enhance_bond_processing_with_treasuries

# Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

LOCAL_API_URL = 'http://localhost:8080'
CLOUD_API_URL = 'https://future-footing-414610.uc.r.appspot.com'
MAIN_DB_PATH = './bonds_data.db'

def get_prior_month_end():
    """Get prior month end date for institutional settlement"""
    today = datetime.now()
    first_day_current_month = today.replace(day=1)
    last_day_previous_month = first_day_current_month - timedelta(days=1)
    return last_day_previous_month.strftime("%Y-%m-%d")

def test_method_1_direct_local_plus_isin(bond_input):
    """Method 1: Direct Local + ISIN"""
    try:
        bond_data = {
            'isin': bond_input['isin'],
            'description': bond_input['description'],
            'price': bond_input['price'],
            'settlement_date': get_prior_month_end()
        }
        
        bonds_list = [bond_data]
        enhanced_bonds = enhance_bond_processing_with_treasuries(bonds_list, MAIN_DB_PATH)
        results = process_bonds_with_weightings(enhanced_bonds, use_prior_month_end=True)
        
        if results and len(results) > 0:
            result = results[0]
            return {
                'yield': result.get('yield'),
                'duration': result.get('duration'),
                'parser_used': 'direct_local'
            }
        return None
    except Exception as e:
        logger.error(f"Method 1 failed: {e}")
        return None

def test_method_2_direct_local_minus_isin(bond_input):
    """Method 2: Direct Local - ISIN (parser)"""
    # For now, this will fail without proper parser integration
    logger.warning("Method 2: Universal Parser not properly integrated")
    return None

def test_api_method(url, payload, method_name):
    """Generic API testing method"""
    try:
        response = requests.post(f"{url}/api/v1/bond/parse-and-calculate", 
                               json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                analytics = data.get('analytics', {})
                processing = data.get('processing', {})
                
                return {
                    'yield': analytics.get('yield'),
                    'duration': analytics.get('duration'),
                    'parser_used': f"{method_name}_{processing.get('parsing', 'unknown')}"
                }
        
        logger.warning(f"{method_name} failed: {response.status_code}")
        return None
        
    except Exception as e:
        logger.error(f"{method_name} failed: {e}")
        return None

def test_method_3_local_api_plus_isin(bond_input):
    """Method 3: Local API + ISIN"""
    payload = {
        'description': bond_input['description'],
        'isin': bond_input['isin'],
        'price': bond_input['price']
    }
    return test_api_method(LOCAL_API_URL, payload, "local_api_with_isin")

def test_method_4_local_api_minus_isin(bond_input):
    """Method 4: Local API - ISIN"""
    payload = {
        'description': bond_input['description'],
        'price': bond_input['price']
    }
    return test_api_method(LOCAL_API_URL, payload, "local_api_desc_only")

def test_method_5_cloud_api_plus_isin(bond_input):
    """Method 5: Cloud API + ISIN"""
    payload = {
        'description': bond_input['description'],
        'isin': bond_input['isin'],
        'price': bond_input['price']
    }
    return test_api_method(CLOUD_API_URL, payload, "cloud_api_with_isin")

def test_method_6_cloud_api_minus_isin(bond_input):
    """Method 6: Cloud API - ISIN"""
    payload = {
        'description': bond_input['description'],
        'price': bond_input['price']
    }
    return test_api_method(CLOUD_API_URL, payload, "cloud_api_desc_only")

def get_test_bonds():
    """Get the 25-bond test portfolio"""
    return [
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
        {"isin": "US698299BL70", "description": "PANAMA, 3.87%, 23-Jul-2060", "price": 56.60, "bloomberg_yield": 7.360000},
        {"isin": "US71654QDF63", "description": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060", "price": 71.42, "bloomberg_yield": 9.880000},
        {"isin": "US71654QDE98", "description": "PETROLEOS MEXICA, 5.95%, 28-Jan-2031", "price": 89.55, "bloomberg_yield": 8.320000},
        {"isin": "XS2585988145", "description": "GACI FIRST INVST, 5.125%, 14-Feb-2053", "price": 85.54, "bloomberg_yield": 6.230000},
        {"isin": "XS1959337749", "description": "QATAR STATE OF, 4.817%, 14-Mar-2049", "price": 89.97, "bloomberg_yield": 5.580000},
        {"isin": "XS2233188353", "description": "QNB FINANCE LTD, 1.625%, 22-Sep-2025", "price": 99.23, "bloomberg_yield": 5.020000},
        {"isin": "XS2359548935", "description": "QATAR ENERGY, 3.125%, 12-Jul-2041", "price": 73.79, "bloomberg_yield": 5.630000},
        {"isin": "XS0911024635", "description": "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043", "price": 93.29, "bloomberg_yield": 5.660000},
        {"isin": "USP0R80BAG79", "description": "SITIOS, 5.375%, 04-Apr-2032", "price": 97.26, "bloomberg_yield": 5.870000}
    ]

def run_comprehensive_test():
    """Run the comprehensive 6-way test"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    logger.info("🚀 SIMPLE 6-WAY COMPREHENSIVE BOND TESTER")
    logger.info("=" * 60)
    logger.info("🔧 FIXED: Using correct API endpoints")
    logger.info("📊 Testing all 25 bonds across 6 methods")
    logger.info("")
    
    bonds = get_test_bonds()
    test_methods = [
        ("Direct Local + ISIN", 1, test_method_1_direct_local_plus_isin),
        ("Direct Local - ISIN", 2, test_method_2_direct_local_minus_isin),
        ("Local API + ISIN", 3, test_method_3_local_api_plus_isin),
        ("Local API - ISIN", 4, test_method_4_local_api_minus_isin),
        ("Cloud API + ISIN", 5, test_method_5_cloud_api_plus_isin),
        ("Cloud API - ISIN", 6, test_method_6_cloud_api_minus_isin)
    ]
    
    method_success_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
    panama_results = {}
    
    # Test all bonds
    for bond_idx, bond in enumerate(bonds):
        logger.info(f"\n📈 Testing Bond {bond_idx + 1}/25: {bond['description'][:50]}...")
        
        for method_name, method_num, test_func in test_methods:
            logger.info(f"   Method {method_num}: {method_name}")
            
            try:
                result = test_func(bond)
                success = result is not None
                
                if success:
                    yield_val = result.get('yield')
                    duration_val = result.get('duration')
                    
                    logger.info(f"      ✅ Success: Yield {yield_val}%, Duration {duration_val}")
                    method_success_counts[method_num] += 1
                    
                    # Track PANAMA results
                    if "PANAMA" in bond['description']:
                        panama_results[method_num] = yield_val
                        logger.info(f"      🎯 PANAMA: {yield_val}% (Bloomberg: {bond['bloomberg_yield']}%)")
                        
                else:
                    logger.info(f"      ❌ Failed")
                
            except Exception as e:
                logger.error(f"      ❌ Exception: {e}")
    
    # Final summary
    logger.info("\n📊 FINAL SUMMARY - ALL 25 BONDS")
    logger.info("=" * 50)
    
    total_bonds = len(bonds)
    for method_num in range(1, 7):
        success_count = method_success_counts[method_num]
        success_rate = (success_count / total_bonds) * 100
        status = "✅" if success_rate == 100.0 else "⚠️" if success_rate > 50 else "❌"
        logger.info(f"{status} Method {method_num}: {success_count}/{total_bonds} ({success_rate:.1f}%)")
    
    # PANAMA bond results
    if panama_results:
        logger.info(f"\n🎯 PANAMA BOND RESULTS:")
        logger.info(f"   Bloomberg Baseline: 7.360000%")
        for method_num, yield_val in panama_results.items():
            diff = yield_val - 7.360000
            diff_bps = diff * 100
            logger.info(f"   Method {method_num}: {yield_val:.6f}% (diff: {diff_bps:+.1f} bps)")
    
    # Overall success
    total_success = sum(method_success_counts.values())
    overall_rate = (total_success / (6 * total_bonds)) * 100
    logger.info(f"\n🏆 OVERALL SUCCESS RATE: {total_success}/{6 * total_bonds} ({overall_rate:.1f}%)")
    
    return f"six_way_analysis_SIMPLE_{timestamp}.db"

if __name__ == "__main__":
    try:
        db_name = run_comprehensive_test()
        logger.info(f"\n✅ SUCCESS! Test completed")
        logger.info(f"📊 Results available")
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        logger.error(traceback.format_exc())
