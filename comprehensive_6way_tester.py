#!/usr/bin/env python3
"""
CONSOLIDATED COMPREHENSIVE 6-WAY BOND TESTING FRAMEWORK
========================================================

This single, unified script performs a comprehensive 6-way analysis of a bond portfolio,
stores the results in a database, and generates final comparison tables.

EXECUTION:
1. Ensure the local API server (google_analysis10_api.py) is running.
2. Run this script from your terminal: python3 comprehensive_6way_tester.py

FUNCTIONALITY:
- Creates a new, timestamped SQLite database for each test run.
- Tests a 25-bond portfolio against 6 calculation methods:
    1. Direct Local + ISIN (database lookup)
    2. Direct Local - ISIN (parser fallback)
    3. Local API + ISIN (API with database)
    4. Local API - ISIN (API with parser fallback)
    5. Cloud API + ISIN (when deployed)
    6. Cloud API - ISIN (cloud fallback)
- Stores all 150 (25 bonds * 6 methods) results in a detailed log table.
- Populates three final tables (yield_comparison, duration_comparison, spread_comparison)
  that show the results from all methods side-by-side against the Bloomberg baseline.
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

# --- Configuration ---
# Set up logging to capture details
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API URLs
LOCAL_API_URL = 'http://localhost:8080'
# Replace with your actual deployed URL when ready
CLOUD_API_URL = 'https://future-footing-414610.uc.r.appspot.com'

# Database paths
# Assumes the main bond data DB is in the same directory or a 'data' subdirectory
MAIN_DB_PATH = './bonds_data.db'
if not os.path.exists(MAIN_DB_PATH):
    MAIN_DB_PATH = './data/bonds_data.db'

# --- Data Sources ---
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
    """Returns the HIGH PRECISION Bloomberg baseline results from user's actual Bloomberg Terminal data.
    
    Updated: 2025-07-22 with 6+ decimal place precision
    Source: Bloomberg Terminal export with actual market data
    """
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


def setup_database(db_name):
    """Creates a new SQLite database and all required tables."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Main results table to log every individual test
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS six_way_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_run_id TEXT,
        bond_identifier TEXT,
        method_name TEXT,
        success BOOLEAN,
        yield_pct REAL,
        duration_years REAL,
        spread_bps REAL,
        error_message TEXT
    )
    ''')

    # Final comparison tables
    comparison_columns = """
        isin TEXT PRIMARY KEY,
        description TEXT,
        bbg_baseline REAL,
        local_isin REAL,
        local_desc REAL,
        local_api_isin REAL,
        local_api_desc REAL,
        cloud_api_isin REAL,
        cloud_api_desc REAL
    """
    cursor.execute(f"CREATE TABLE IF NOT EXISTS yield_comparison ({comparison_columns})")
    cursor.execute(f"CREATE TABLE IF NOT EXISTS duration_comparison ({comparison_columns})")
    cursor.execute(f"CREATE TABLE IF NOT EXISTS spread_comparison ({comparison_columns})")

    conn.commit()
    return conn

# --- Testing Framework ---
class ComprehensiveBondTester:
    def __init__(self, conn, test_run_id):
        self.conn = conn
        self.cursor = conn.cursor()
        self.test_run_id = test_run_id

    def _test_direct_local(self, bond_data, use_isin=True):
        """Tests the calculation engine by calling it directly as a library."""
        try:
            # Dynamically import the local calculation engine
            sys.path.append('.')
            from bond_master_hierarchy import process_bonds_with_weightings

            df_data = {'price': bond_data['price']}
            if use_isin:
                df_data['isin'] = bond_data['isin']
                # CRITICAL FIX: Include description even when using ISIN!
                df_data['Name'] = bond_data['description']  # For enhanced fallback case-insensitive lookup
            else:
                df_data['BOND_ENAME'] = bond_data['description']
            
            test_df = pd.DataFrame([df_data])
            
            # The local function requires the main DB path and record_number
            results_df = process_bonds_with_weightings(test_df, MAIN_DB_PATH, record_number=1)
            
            if not results_df.empty and results_df.iloc[0].get('error') is None:
                return True, results_df.iloc[0].to_dict(), None
            else:
                error = results_df.iloc[0].get('error', 'Empty results from local calc')
                return False, None, error

        except Exception as e:
            return False, None, f"Local import/calc failed: {traceback.format_exc()}"

    def _test_api(self, api_url, bond_data, use_isin=True):
        """Tests the calculation engine by calling its API endpoint."""
        try:
            payload = {'description': bond_data['description'], 'price': bond_data['price']}
            if use_isin:
                payload['isin'] = bond_data['isin']
            
            response = requests.post(f'{api_url}/api/v1/bond/parse-and-calculate', json=payload, timeout=45)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    # Extract bond analytics from the API response format
                    analytics = data.get('analytics', {})
                    bond_data = {
                        'yield': analytics.get('yield'),
                        'duration': analytics.get('duration'),
                        'spread': None  # Spread would need to be calculated separately
                    }
                    return True, bond_data, None
                else:
                    return False, None, data.get('error_message', 'API returned error status')
            else:
                return False, None, f'API Error {response.status_code}: {response.text[:100]}'
        except requests.exceptions.RequestException as e:
            return False, None, f'Network error: {e}'

    def run_all_tests(self, portfolio):
        """Executes all 6 test methods for every bond in the portfolio."""
        methods = {
            "local_isin": lambda bond: self._test_direct_local(bond, use_isin=True),
            "local_desc": lambda bond: self._test_direct_local(bond, use_isin=False),
            "local_api_isin": lambda bond: self._test_api(LOCAL_API_URL, bond, use_isin=True),
            "local_api_desc": lambda bond: self._test_api(LOCAL_API_URL, bond, use_isin=False),
            "cloud_api_isin": lambda bond: self._test_api(CLOUD_API_URL, bond, use_isin=True),
            "cloud_api_desc": lambda bond: self._test_api(CLOUD_API_URL, bond, use_isin=False)
        }

        for i, bond in enumerate(portfolio, 1):
            logger.info(f"--- Testing Bond {i}/{len(portfolio)}: {bond['isin']} ---")
            for name, func in methods.items():
                success, result, error = func(bond)
                self.cursor.execute('''
                    INSERT INTO six_way_results (test_run_id, bond_identifier, method_name, success, yield_pct, duration_years, spread_bps, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (self.test_run_id, bond['isin'], name, success, 
                      result.get('yield') if success else None,
                      result.get('duration') if success else None,
                      result.get('spread') if success else None,
                      error))
            self.conn.commit()

# --- Analysis and Reporting ---
def create_comparison_tables(conn, test_run_id, baseline_data):
    """Queries the results and populates the final comparison tables."""
    logger.info("Creating final comparison tables...")
    
    # Read the detailed results into a pandas DataFrame
    df = pd.read_sql_query(f"SELECT * FROM six_way_results WHERE test_run_id = '{test_run_id}'", conn)
    
    baseline_df = pd.DataFrame.from_dict(baseline_data, orient='index').reset_index().rename(columns={'index': 'isin'})

    for metric in ['yield', 'duration', 'spread']:
        table_name = f"{metric}_comparison"
        metric_col = f"{metric}_pct" if metric == 'yield' else f"{metric}_years" if metric == 'duration' else f"{metric}_bps"
        
        # Pivot the results to get methods as columns
        pivot_df = df.pivot(index='bond_identifier', columns='method_name', values=metric_col).reset_index()
        pivot_df = pivot_df.rename(columns={'bond_identifier': 'isin'})

        # Merge with baseline data
        merged_df = pd.merge(baseline_df[['isin', metric]], pivot_df, on='isin', how='left')
        
        # Add description
        desc_df = pd.DataFrame(get_25_bond_portfolio())[['isin', 'description']]
        final_df = pd.merge(desc_df, merged_df, on='isin', how='left')
        final_df = final_df.rename(columns={metric: 'bbg_baseline'})

        # Ensure all columns exist, even if a method failed for all bonds
        expected_cols = ['isin', 'description', 'bbg_baseline', 'local_isin', 'local_desc', 'local_api_isin', 'local_api_desc', 'cloud_api_isin', 'cloud_api_desc']
        for col in expected_cols:
            if col not in final_df.columns:
                final_df[col] = None
        
        final_df = final_df[expected_cols] # Order columns correctly
        
        # Write to the specific comparison table
        final_df.to_sql(table_name, conn, if_exists='replace', index=False)
        logger.info(f"Successfully created '{table_name}' table.")

# --- Main Execution Block ---
def main():
    """Main function to orchestrate the testing and analysis."""
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_name = f'six_way_analysis_{timestamp}.db'
    test_run_id = f'run_{timestamp}'

    logger.info(f"Starting 6-Way Comprehensive Test. Run ID: {test_run_id}")
    logger.info(f"Results will be stored in: {db_name}")

    if not os.path.exists(MAIN_DB_PATH):
        logger.error(f"CRITICAL: Main bond database not found at '{MAIN_DB_PATH}'. Aborting.")
        return

    conn = setup_database(db_name)
    portfolio = get_25_bond_portfolio()
    baseline_data = get_bloomberg_baseline()
    
    tester = ComprehensiveBondTester(conn, test_run_id)
    tester.run_all_tests(portfolio)
    
    create_comparison_tables(conn, test_run_id, baseline_data)
    
    conn.close()
    
    end_time = time.time()
    logger.info(f"--- Testing Complete in {end_time - start_time:.2f} seconds ---")
    logger.info("Analysis complete. You can now inspect the database:")
    logger.info(f"DB Name: {db_name}")
    logger.info("Tables: yield_comparison, duration_comparison, spread_comparison")

if __name__ == "__main__":
    main()
