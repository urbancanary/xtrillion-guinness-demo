#!/usr/bin/env python3
"""
FIXED COMPREHENSIVE 6-WAY BOND TESTING FRAMEWORK
=================================================

CRITICAL FIX: Direct Local method now uses the SAME calculation engine as APIs
- APIs use: SmartBondParser.calculate_accrued_interest()
- Direct Local was using: process_bonds_with_weightings() (WRONG!)

This ensures all methods use identical calculation logic.
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

# Add current directory to path for imports
sys.path.append('.')

# Import the SAME bond parser that APIs use
from bond_description_parser import SmartBondParser

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API URLs
LOCAL_API_URL = 'http://localhost:8080'
CLOUD_API_URL = 'https://future-footing-414610.uc.r.appspot.com'

# Database paths (same as APIs use)
DATABASE_PATH = './bonds_data.db'
VALIDATED_DB_PATH = './validated_quantlib_bonds.db'

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
    """Returns the REAL Bloomberg baseline results from user's actual data."""
    return {
        "US912810TJ79": {"yield": 4.90, "duration": 16.36, "spread": None},
        "XS2249741674": {"yield": 5.64, "duration": 10.10, "spread": 118},
        "XS1709535097": {"yield": 5.72, "duration": 9.82, "spread": 123},
        "XS1982113463": {"yield": 5.60, "duration": 9.93, "spread": 111},
        "USP37466AS18": {"yield": 6.27, "duration": 13.19, "spread": 144},
        "USP3143NAH72": {"yield": 5.95, "duration": 8.02, "spread": 160},
        "USP30179BR86": {"yield": 7.44, "duration": 11.58, "spread": 261},
        "US195325DX04": {"yield": 7.84, "duration": 12.98, "spread": 301},
        "US279158AJ82": {"yield": 9.28, "duration": 9.81, "spread": 445},
        "USP37110AM89": {"yield": 6.54, "duration": 12.39, "spread": 171},
        "XS2542166231": {"yield": 5.72, "duration": 7.21, "spread": 146},
        "XS2167193015": {"yield": 6.34, "duration": 15.27, "spread": 151},
        "XS1508675508": {"yield": 5.97, "duration": 12.60, "spread": 114},
        "XS1807299331": {"yield": 7.06, "duration": 11.45, "spread": 223},
        "US91086QAZ19": {"yield": 7.37, "duration": 13.37, "spread": 255},
        "USP6629MAD40": {"yield": 7.07, "duration": 11.38, "spread": 224},
        "US698299BL70": {"yield": 7.36, "duration": 13.49, "spread": 253},
        "US71654QDF63": {"yield": 9.88, "duration": 9.72, "spread": 505},
        "US71654QDE98": {"yield": 8.32, "duration": 4.47, "spread": 444},
        "XS2585988145": {"yield": 6.23, "duration": 13.33, "spread": 140},
        "XS1959337749": {"yield": 5.58, "duration": 13.26, "spread": 76},
        "XS2233188353": {"yield": 5.02, "duration": 0.23, "spread": 71},
        "XS2359548935": {"yield": 5.63, "duration": 11.51, "spread": 101},
        "XS0911024635": {"yield": 5.66, "duration": 11.24, "spread": 95},
        "USP0R80BAG79": {"yield": 5.87, "duration": 5.51, "spread": 187}
    }

def get_prior_month_end():
    """Get prior month end settlement date (same as APIs)"""
    from datetime import datetime, timedelta
    today = datetime.now()
    first_day_current_month = today.replace(day=1)
    last_day_previous_month = first_day_current_month - timedelta(days=1)
    return last_day_previous_month.strftime("%Y-%m-%d")

def setup_database(db_name):
    """Creates a new SQLite database and all required tables."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

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

class FixedBondTester:
    def __init__(self, conn, test_run_id):
        self.conn = conn
        self.cursor = conn.cursor()
        self.test_run_id = test_run_id
        # Initialize the SAME parser that APIs use
        self.parser = SmartBondParser(DATABASE_PATH, VALIDATED_DB_PATH)

    def _test_direct_local_FIXED(self, bond_data, use_isin=True):
        """
        FIXED: Now uses the SAME calculation engine as APIs!
        Previously: Called process_bonds_with_weightings() (WRONG!)
        Now: Uses SmartBondParser.calculate_accrued_interest() (SAME AS APIs!)
        """
        try:
            # Step 1: Parse bond description (same as API)
            if use_isin and 'isin' in bond_data:
                # Try ISIN lookup first
                parsed_bond = self.parser.parse_bond_description(bond_data['description'])
                if parsed_bond:
                    parsed_bond['isin'] = bond_data['isin']
            else:
                # Parse from description only
                parsed_bond = self.parser.parse_bond_description(bond_data['description'])
            
            if not parsed_bond:
                return False, None, f"Could not parse bond description: {bond_data['description']}"
            
            # Step 2: Predict conventions (same as API)
            predicted_conventions = self.parser.predict_most_likely_conventions(parsed_bond)
            
            # Step 3: Calculate using SAME method as API
            settlement_date = get_prior_month_end()
            price = bond_data['price']
            
            calculation_result = self.parser.calculate_accrued_interest(
                parsed_bond, predicted_conventions, settlement_date, price
            )
            
            if calculation_result['calculation_successful']:
                return True, {
                    'yield': calculation_result['yield_to_maturity'],
                    'duration': calculation_result['duration'],
                    'spread': None  # Spread calculation would be separate
                }, None
            else:
                return False, None, "Calculation failed"
            
        except Exception as e:
            return False, None, f"Fixed Local calc failed: {traceback.format_exc()}"

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
                    analytics = data.get('analytics', {})
                    bond_data = {
                        'yield': analytics.get('yield'),
                        'duration': analytics.get('duration'),
                        'spread': None
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
            "local_isin": lambda bond: self._test_direct_local_FIXED(bond, use_isin=True),
            "local_desc": lambda bond: self._test_direct_local_FIXED(bond, use_isin=False),
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

def create_comparison_tables(conn, test_run_id, baseline_data):
    """Queries the results and populates the final comparison tables."""
    logger.info("Creating final comparison tables...")
    
    df = pd.read_sql_query(f"SELECT * FROM six_way_results WHERE test_run_id = '{test_run_id}'", conn)
    baseline_df = pd.DataFrame.from_dict(baseline_data, orient='index').reset_index().rename(columns={'index': 'isin'})

    for metric in ['yield', 'duration', 'spread']:
        table_name = f"{metric}_comparison"
        metric_col = f"{metric}_pct" if metric == 'yield' else f"{metric}_years" if metric == 'duration' else f"{metric}_bps"
        
        pivot_df = df.pivot(index='bond_identifier', columns='method_name', values=metric_col).reset_index()
        pivot_df = pivot_df.rename(columns={'bond_identifier': 'isin'})

        merged_df = pd.merge(baseline_df[['isin', metric]], pivot_df, on='isin', how='left')
        
        desc_df = pd.DataFrame(get_25_bond_portfolio())[['isin', 'description']]
        final_df = pd.merge(desc_df, merged_df, on='isin', how='left')
        final_df = final_df.rename(columns={metric: 'bbg_baseline'})

        expected_cols = ['isin', 'description', 'bbg_baseline', 'local_isin', 'local_desc', 'local_api_isin', 'local_api_desc', 'cloud_api_isin', 'cloud_api_desc']
        for col in expected_cols:
            if col not in final_df.columns:
                final_df[col] = None
        
        final_df = final_df[expected_cols]
        final_df.to_sql(table_name, conn, if_exists='replace', index=False)
        logger.info(f"Successfully created '{table_name}' table.")

def main():
    """Main function to orchestrate the testing and analysis."""
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_name = f'six_way_analysis_FIXED_{timestamp}.db'
    test_run_id = f'run_FIXED_{timestamp}'

    logger.info(f"🔧 FIXED 6-Way Comprehensive Test. Run ID: {test_run_id}")
    logger.info(f"✅ Direct Local now uses SAME engine as APIs!")
    logger.info(f"✅ Bloomberg baseline updated to user's real data!")
    logger.info(f"Results will be stored in: {db_name}")

    if not os.path.exists(DATABASE_PATH):
        logger.error(f"CRITICAL: Main bond database not found at '{DATABASE_PATH}'. Aborting.")
        return

    conn = setup_database(db_name)
    portfolio = get_25_bond_portfolio()
    baseline_data = get_bloomberg_baseline()
    
    tester = FixedBondTester(conn, test_run_id)
    tester.run_all_tests(portfolio)
    
    create_comparison_tables(conn, test_run_id, baseline_data)
    
    conn.close()
    
    end_time = time.time()
    logger.info(f"--- FIXED Testing Complete in {end_time - start_time:.2f} seconds ---")
    logger.info("Analysis complete. You can now inspect the database:")
    logger.info(f"DB Name: {db_name}")
    logger.info("🎯 Direct Local should now match API results!")

if __name__ == "__main__":
    main()
