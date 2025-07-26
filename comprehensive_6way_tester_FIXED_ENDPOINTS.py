#!/usr/bin/env python3
"""
FIXED COMPREHENSIVE 6-WAY BOND TESTING FRAMEWORK - CORRECT ENDPOINTS
===================================================================

FIXED: Updated to use correct API endpoints and payload formats.
- API endpoint: /api/v1/bond/parse-and-calculate (not /api/bond/calculate)
- Payload format: {"description": "...", "isin": "...", "price": ...}
- Response parsing: Updated to match actual API response format

This script tests bond calculation across all 6 methods:
1. Direct Local + ISIN (database lookup)
2. Direct Local - ISIN (Universal Parser)
3. Local API + ISIN (API with database) ← FIXED ENDPOINT
4. Local API - ISIN (Universal Parser) ← FIXED ENDPOINT
5. Cloud API + ISIN (when deployed) ← FIXED ENDPOINT
6. Cloud API - ISIN (Universal Parser) ← FIXED ENDPOINT
"""

import sys
import os

# CRITICAL FIX: Add the project directory to the Python path to ensure the correct module is loaded.
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import sqlite3
import pandas as pd

import requests
import json
import time
from datetime import datetime, timedelta
import logging
import traceback
import argparse
import glob
import io

# --- Logging Configuration ---
# CRITICAL: Configure logging at the very top to capture all messages.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add core module for Universal Parser
sys.path.append(os.path.abspath('./core'))
try:
    from smart_bond_parser import SmartBondParser, BondSpecification
    SMART_PARSER_AVAILABLE = True
except ImportError:
    logger.warning("Smart Bond Parser not available - Methods 2, 4, 6 may fail")
    SMART_PARSER_AVAILABLE = False

# Import existing calculation modules
# from google_analysis10 import process_bonds_with_weightings # This is now deprecated
from google_analysis10 import process_bond_portfolio

# --- API Configuration ---
LOCAL_API_URL = 'http://localhost:8080'
CLOUD_API_URL = 'https://future-footing-414610.uc.r.appspot.com'

# --- Database Paths ---
# Define absolute paths to prevent ambiguity during execution.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, 'bonds_data.db')
VALIDATED_DB_PATH = os.path.join(SCRIPT_DIR, 'validated_quantlib_bonds.db')
BLOOMBERG_DB_PATH = os.path.join(SCRIPT_DIR, 'bonds_data.db') # CORRECTED: This DB contains the treasury yields

# Initialize Smart Parser if available
smart_parser = None
if SMART_PARSER_AVAILABLE:
    try:
        smart_parser = SmartBondParser(DB_PATH, VALIDATED_DB_PATH, BLOOMBERG_DB_PATH)
        logger.info("🚀 Smart Bond Parser initialized")
    except Exception as e:
        logger.warning(f"Smart Parser initialization failed: {e}")
        SMART_PARSER_AVAILABLE = False

def get_prior_month_end():
    """Get prior month end date for institutional settlement"""
    today = datetime.now()
    first_day_current_month = today.replace(day=1)
    last_day_previous_month = first_day_current_month - timedelta(days=1)
    return last_day_previous_month.strftime("%Y-%m-%d")

def test_method_1_direct_local_plus_isin(bond, settlement_days=0):
    """Method 1: Uses local processing engine with ISIN via portfolio processor."""
    logger.info(f"Running Method 1: Direct Local + ISIN for T+{settlement_days}...")
    try:
        portfolio = {'data': [bond]}
        result = process_bond_portfolio(portfolio_data=portfolio, db_path=BLOOMBERG_DB_PATH, validated_db_path=VALIDATED_DB_PATH, bloomberg_db_path=BLOOMBERG_DB_PATH, settlement_days=settlement_days)
        return result[0] if result else None
    except Exception as e:
        logger.error(f"Method 1 (Direct Local + ISIN) failed for {bond['isin']}: {e}", exc_info=True)
        return None

def test_method_2_direct_local_minus_isin(bond, settlement_days=0):
    """Method 2: Uses local processing engine without ISIN via portfolio processor."""
    logger.info(f"Running Method 2: Direct Local - ISIN for T+{settlement_days}...")
    try:
        bond_without_isin = bond.copy()
        if 'isin' in bond_without_isin:
            del bond_without_isin['isin']
        if 'BOND_CD' in bond_without_isin:
            del bond_without_isin['BOND_CD']

        portfolio = {'data': [bond_without_isin]}
        result = process_bond_portfolio(portfolio_data=portfolio, db_path=BLOOMBERG_DB_PATH, validated_db_path=VALIDATED_DB_PATH, bloomberg_db_path=BLOOMBERG_DB_PATH, settlement_days=settlement_days)
        return result[0] if result else None
    except Exception as e:
        logger.error(f"Method 2 (Direct Local - ISIN) failed for {bond.get('isin', 'N/A')}: {e}", exc_info=True)
        return None

def test_method_3_local_api_plus_isin(bond_input, settlement_days=0):
    """Method 3: Local API + ISIN - FIXED ENDPOINT"""
    try:
        payload = {
            'description': bond_input['description'],
            'isin': bond_input['isin'],
            'price': bond_input['price'],
            'settlement_days': settlement_days
        }
        response = requests.post(f"{LOCAL_API_URL}/api/v1/bond/parse-and-calculate?technical=true", json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        if data.get('status') == 'success' and data.get('analytics'):
            analytics = data['analytics']
            return {
                'yield': analytics.get('yield_to_maturity_percent'),
                'duration': analytics.get('modified_duration_years'),
                'spread': analytics.get('spread_bps'),
                'accrued_interest': analytics.get('accrued_interest'),
                'conventions': data.get('bond', {}).get('conventions'),
                'parser_used': data.get('bond', {}).get('parser_used', 'local_api_with_isin')
            }
        logger.warning(f"Method 3 (API) failed for {bond_input.get('isin')}: {data.get('message')}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Method 3 request failed for {bond_input.get('isin', 'unknown')}: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred in Method 3 for {bond_input.get('isin', 'unknown')}: {e}")
        return None

def test_method_4_local_api_minus_isin(bond_input, settlement_days=0):
    """Method 4: Local API - ISIN - FIXED ENDPOINT"""
    try:
        payload = {
            'description': bond_input['description'],
            'price': bond_input['price'],
            'settlement_days': settlement_days
        }
        response = requests.post(f"{LOCAL_API_URL}/api/v1/bond/parse-and-calculate?technical=true", json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        if data.get('status') == 'success' and data.get('analytics'):
            analytics = data['analytics']
            return {
                'yield': analytics.get('yield_to_maturity_percent'),
                'duration': analytics.get('modified_duration_years'),
                'spread': analytics.get('spread_bps'),
                'accrued_interest': analytics.get('accrued_interest'),
                'conventions': data.get('bond', {}).get('conventions'),
                'parser_used': data.get('bond', {}).get('parser_used', 'local_api_no_isin')
            }
        logger.warning(f"Method 4 (API) failed for '{bond_input.get('description')}': {data.get('message')}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Method 4 request failed for '{bond_input.get('description', 'unknown')}': {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred in Method 4 for '{bond_input.get('description', 'unknown')}': {e}")
        return None

def create_comprehensive_database(timestamp):
    """Creates a new SQLite database for the test run."""
    db_name = f"six_way_analysis_FIXED_{timestamp}.db"
    conn = sqlite3.connect(db_name)
    conn.close()
    return db_name

def run_all_methods_for_portfolio(bonds, settlement_configs):
    """Runs all 6 methods for the entire portfolio and returns a DataFrame."""
    all_results_list = []
    total_bonds = len(bonds)

    for i, bond in enumerate(bonds):
        logger.info(f"\n---\nProcessing Bond {i+1}/{total_bonds}: {bond.get('description')} (ISIN: {bond.get('isin')})\n---")
        for settlement_days in settlement_configs:
            # Define methods to run
            # Run Method 1 first to get baseline local conventions
            method1_result = test_method_1_direct_local_plus_isin(bond, settlement_days)
            method1_conventions = method1_result.get('conventions') if method1_result else None

            methods_to_run = {
                "Method 1: Local+ISIN": (lambda *args: method1_result, []),
                "Method 2: Local-ISIN": (test_method_2_direct_local_minus_isin, [bond, settlement_days]),
                "Method 3: API+ISIN": (test_method_3_local_api_plus_isin, [bond, settlement_days]),
                "Method 4: API-ISIN": (test_method_4_local_api_minus_isin, [bond, settlement_days]),
            }

            for method_name, (method_func, args) in methods_to_run.items():
                try:
                    result = method_func(*args)
                    if result:
                        all_results_list.append({
                            'ISIN': bond['isin'],
                            'Description': bond['description'],
                            'Method': method_name,
                            'Settlement': f"T+{settlement_days}",
                            'Yield': result.get('yield_to_maturity_percent') or result.get('yield'),
                            'Duration': result.get('modified_duration_years') or result.get('duration'),
                            'Spread': result.get('spread_bps') or result.get('spread') or result.get('z_spread'), # FIXED: Capture z_spread
                            'Conventions': str(result.get('conventions') or method1_conventions),
                            'Parser': result.get('parser_used'),
                            'Success': True
                        })
                    else:
                        # CRITICAL FIX: Append a failure record if the result is empty/None
                        logger.warning(f"Empty or invalid result for {method_name} on bond {bond['isin']}.")
                        all_results_list.append({
                            'ISIN': bond['isin'], 'Description': bond['description'], 'Method': method_name,
                            'Settlement': f"T+{settlement_days}", 'Yield': None, 'Duration': None, 'Spread': None,
                            'Conventions': None, 'Parser': 'N/A', 'Success': False
                        })
                except Exception as e:
                    if bond['isin'] == 'US91282CJZ59':
                        logger.error(f"TREASURY_DEBUG: Exception for {method_name} on bond {bond['isin']}: {e}", exc_info=True)
                    logger.error(f"{method_name} failed for {bond['isin']} (T+{settlement_days}): {traceback.format_exc()}")
                    all_results_list.append({
                        'ISIN': bond['isin'], 'Description': bond['description'], 'Method': method_name,
                        'Settlement': f"T+{settlement_days}", 'Yield': None, 'Duration': None, 'Spread': None,
                        'Conventions': None, 'Parser': None, 'Success': False
                    })

    return pd.DataFrame(all_results_list)

def get_test_bonds():
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

def run_comprehensive_test(force_run=False):
    """Run the comprehensive 6-way test and save results to a database."""
    # Check for recent databases if not forcing a run
    if not force_run:
        try:
            existing_dbs = glob.glob("six_way_analysis_FIXED_*.db")
            if existing_dbs:
                latest_db = max(existing_dbs, key=os.path.getctime)
                latest_time = datetime.fromtimestamp(os.path.getctime(latest_db))
                if datetime.now() - latest_time < timedelta(hours=1):
                    logger.info(f"Found recent database '{latest_db}' created at {latest_time}. Skipping test run.")
                    return None  # Signal to main that the run was skipped
        except Exception as e:
            logger.warning(f"Could not check for recent databases: {e}")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_name = create_comprehensive_database(timestamp)
    
    logger.info(f"🚀 Starting FIXED comprehensive 6-way test")
    logger.info(f"📊 Database: {db_name}")
    
    bonds = get_test_bonds()
    results_df = run_all_methods_for_portfolio(bonds, settlement_configs=[0, 1])
    
    # Save results to the database
    try:
        conn = sqlite3.connect(db_name)
        # --- Data Processing and Storage ---
        logger.info(f"[SAVE_DEBUG] Initial shape of results_df: {results_df.shape}")
        if not results_df.empty:
            results_df.to_sql('test_log', conn, if_exists='replace', index_label='id')
        
        # Create and save comparison table
        yield_pivot = results_df.pivot_table(
            index=['ISIN', 'Description'], 
            columns=['Method', 'Settlement'], 
            values='Yield'
        ).reset_index()
        yield_pivot.to_sql('yield_comparison', conn, if_exists='replace', index=False)

        # --- FIX: Enforce schema and handle NaNs before writing to DB ---
        # Final processing for the main results table
        logger.info(f"[SAVE_DEBUG] Before final processing. Shape: {results_df.shape}")
        if 'Conventions' in results_df.columns:
            results_df['Conventions'] = results_df['Conventions'].apply(str)
        logger.info(f"[SAVE_DEBUG] After converting Conventions to string. Shape: {results_df.shape}")

        # Define a schema for the final table for type consistency
        schema = {
            'ISIN': 'str',
            'Description': 'str',
            'Method': 'str',
            'Settlement': 'str',
            'Yield': 'float',
            'Duration': 'float',
            'Spread': 'float',
            'Conventions': 'str',
            'Parser': 'str',
            'Success': 'int'
        }
        results_df = results_df.astype(schema, errors='ignore')
        logger.info(f"[SAVE_DEBUG] After applying schema with astype. Shape: {results_df.shape}")

        # Convert dicts in 'Conventions' to JSON strings for SQLite compatibility
        if 'Conventions' in results_df.columns:
            results_df['Conventions'] = results_df['Conventions'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else x)
        logger.info(f"[SAVE_DEBUG] After converting Conventions to JSON. Shape: {results_df.shape}")

        # Replace NaN with None for SQLite compatibility
        results_df = results_df.where(pd.notnull(results_df), None)
        logger.info(f"[SAVE_DEBUG] After replacing NaNs. Shape: {results_df.shape}")

        # Log final DataFrame info before saving
        logger.info("--- Final DataFrame Info ---")
        buf = io.StringIO()
        results_df.info(buf=buf)
        logger.info(buf.getvalue())
        logger.info("--- Final DataFrame Content ---")
        logger.info(results_df.to_string())

        # Save the final, processed data
        try:
            results_df.to_sql('results_summary', conn, if_exists='replace', index=False)
            logger.info(f"✅ Successfully saved final results to 'results_summary' table. Shape: {results_df.shape}")
        except Exception as e:
            logger.error(f"🔥 Failed to save final results: {e}")

        # DEBUG: Read the data back and print it to verify it was saved
        logger.info("--- DEBUG: DataFrame content for US Treasury AFTER saving (read from DB) ---")
        try:
            saved_df = pd.read_sql('SELECT * FROM results_summary', conn)
            print(saved_df[saved_df['ISIN'] == 'US91282CJZ59'])
        except Exception as read_e:
            logger.error(f"Could not read back data from DB for debugging: {read_e}")

        conn.close()
        logger.info(f"✅ Database connection closed for {db_name}")
    except Exception as e:
        logger.error(f"Failed to save results to database: {e}")
    return db_name

def main():
    """Main function to run the comprehensive test suite."""
    parser = argparse.ArgumentParser(description='Run the comprehensive 6-way bond tester.')
    parser.add_argument('--force-run', action='store_true', help='Force a new test run even if a recent database exists.')
    args = parser.parse_args()

    try:
        logger.info("🚀 STARTING FIXED 6-WAY COMPREHENSIVE BOND TESTER")
        logger.info("=" * 60)
        
        db_name = run_comprehensive_test(force_run=args.force_run)
        
        if db_name:
            logger.info(f"\n✅ SUCCESS! Test completed successfully")
            logger.info(f"📊 Database: {db_name}")
        else:
            logger.info("⏹️ Test run skipped as a recent database exists. Use --force-run to override.")
            
    except Exception as e:
        logger.error(f"❌ Test failed with a critical error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    # Canary log to confirm script entry
    print("CANARY_LOG: Script __main__ block reached.")
    logger.info("CANARY_LOG: Script __main__ block reached, logger is active.")
    main()
