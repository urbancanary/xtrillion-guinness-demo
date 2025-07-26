#!/usr/bin/env python3
"""
CONSOLIDATED COMPREHENSIVE 6-WAY BOND TESTING FRAMEWORK
======================================================

The ultimate 6-way testing system that consolidates all previous versions.
Tests yield, spread, and duration for 25 bonds across 6 methods with Bloomberg baseline.

Features:
- Tests ALL 3 variables: yield, spread, duration
- Complete 25-bond portfolio
- All 6 methods: Direct Local ±ISIN, API ±ISIN, Cloud ±ISIN
- Bloomberg baseline comparison
- Color-coded difference analysis
- HTML report generation
- Database archiving of results
- Archive management for old files

Methods Tested:
1. Direct Local + ISIN (Database lookup)
2. Direct Local - ISIN (Smart Parser)
3. Local API + ISIN 
4. Local API - ISIN 
5. Cloud API + ISIN
6. Cloud API - ISIN

Color Coding:
- Green: ≤5 bps difference (Excellent)
- Yellow: 5-20 bps difference (Good) 
- Orange: 20-50 bps difference (Acceptable)
- Red: >50 bps difference (Needs Investigation)
"""

import sys
import os
import sqlite3
import pandas as pd
import numpy as np
import requests
import json
import time
import logging
import traceback
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

# Add project paths
PROJECT_ROOT = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10"
sys.path.append(PROJECT_ROOT)

try:
    from google_analysis10 import process_bond_portfolio
    from bond_description_parser import SmartBondParser
    GA10_AVAILABLE = True
except ImportError as e:
    print(f"GA10 import failed: {e}")
    GA10_AVAILABLE = False

# Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API URLs
LOCAL_API_URL = 'http://localhost:8080'
CLOUD_API_URL = 'https://future-footing-414610.uc.r.appspot.com'

class ConsolidatedSixWayTester:
    """
    Comprehensive 6-way testing system for bond calculations
    Tests yield, spread, and duration across all methods
    """
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.db_path = f"{self.project_root}/six_way_analysis_CONSOLIDATED_{self.timestamp}.db"
        self.settlement_date = '2025-06-30'
        
        # Database paths for GA10 integration
        self.main_db_path = f"{self.project_root}/bonds_data.db"
        self.validated_db_path = f"{self.project_root}/validated_quantlib_bonds.db"
        self.bloomberg_db_path = f"{self.project_root}/bloomberg_index.db"
        
        # Initialize database
        self.init_database()
        
        # 25-bond test portfolio with Bloomberg baselines
        self.test_portfolio = [
            {
                'isin': 'US912810TJ79', 'price': 71.66, 
                'name': 'US TREASURY N/B, 3%, 15-Aug-2052',
                'bloomberg': {'yield': 4.89916, 'duration': 16.35658, 'spread': 39.91632}
            },
            {
                'isin': 'XS2249741674', 'price': 77.88,
                'name': 'GALAXY PIPELINE, 3.25%, 30-Sep-2040', 
                'bloomberg': {'yield': 5.39556, 'duration': 11.22303, 'spread': 89.55584}
            },
            {
                'isin': 'XS1709535097', 'price': 89.40,
                'name': 'ABU DHABI CRUDE, 4.6%, 02-Nov-2047',
                'bloomberg': {'yield': 5.42359, 'duration': 13.21138, 'spread': 92.35907}
            },
            {
                'isin': 'XS1982113463', 'price': 87.14,
                'name': 'SAUDI ARAB OIL, 4.25%, 16-Apr-2039',
                'bloomberg': {'yield': 5.59944, 'duration': 9.93052, 'spread': 109.94388}
            },
            {
                'isin': 'USP37466AS18', 'price': 80.39,
                'name': 'EMPRESA METRO, 4.7%, 07-May-2050',
                'bloomberg': {'yield': 6.26618, 'duration': 13.18176, 'spread': 176.61783}
            },
            {
                'isin': 'USP3143NAH72', 'price': 101.63,
                'name': 'CODELCO INC, 6.15%, 24-Oct-2036',
                'bloomberg': {'yield': 5.94874, 'duration': 8.01689, 'spread': 144.87434}
            },
            {
                'isin': 'USP30179BR86', 'price': 86.42,
                'name': 'COMISION FEDERAL, 6.264%, 15-Feb-2052',
                'bloomberg': {'yield': 7.44217, 'duration': 11.58710, 'spread': 294.21683}
            },
            {
                'isin': 'US195325DX04', 'price': 52.71,
                'name': 'COLOMBIA REP OF, 3.875%, 15-Feb-2061',
                'bloomberg': {'yield': 7.83636, 'duration': 12.97993, 'spread': 333.63631}
            },
            {
                'isin': 'US279158AJ82', 'price': 69.31,
                'name': 'ECOPETROL SA, 5.875%, 28-May-2045',
                'bloomberg': {'yield': 9.28195, 'duration': 9.80447, 'spread': 478.19491}
            },
            {
                'isin': 'USP37110AM89', 'price': 76.24,
                'name': 'EMPRESA NACIONAL, 4.5%, 14-Sep-2047',
                'bloomberg': {'yield': 6.54274, 'duration': 12.38229, 'spread': 204.27423}
            },
            {
                'isin': 'XS2542166231', 'price': 103.03,
                'name': 'GREENSAIF PIPELI, 6.129%, 23-Feb-2038',
                'bloomberg': {'yield': 5.78691, 'duration': 8.61427, 'spread': 128.69067}
            },
            {
                'isin': 'XS2167193015', 'price': 64.50,
                'name': 'STATE OF ISRAEL, 3.8%, 13-May-2060',
                'bloomberg': {'yield': 6.33756, 'duration': 15.26825, 'spread': 183.75586}
            },
            {
                'isin': 'XS1508675508', 'price': 82.42,
                'name': 'SAUDI INT BOND, 4.5%, 26-Oct-2046',
                'bloomberg': {'yield': 5.96747, 'duration': 12.60204, 'spread': 146.74727}
            },
            {
                'isin': 'XS1807299331', 'price': 92.21,
                'name': 'KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048',
                'bloomberg': {'yield': 7.05978, 'duration': 11.44784, 'spread': 255.97846}
            },
            {
                'isin': 'US91086QAZ19', 'price': 78.00,
                'name': 'UNITED MEXICAN, 5.75%, 12-Oct-2110',
                'bloomberg': {'yield': 7.37494, 'duration': 13.36798, 'spread': 287.49419}
            },
            {
                'isin': 'USP6629MAD40', 'price': 82.57,
                'name': 'MEXICO CITY ARPT, 5.5%, 31-Jul-2047',
                'bloomberg': {'yield': 7.07038, 'duration': 11.37892, 'spread': 257.03820}
            },
            {
                'isin': 'US698299BL70', 'price': 56.60,
                'name': 'PANAMA, 3.87%, 23-Jul-2060',
                'bloomberg': {'yield': 7.32679, 'duration': 13.57604, 'spread': 282.67859}
            },
            {
                'isin': 'US71654QDF63', 'price': 71.42,
                'name': 'PETROLEOS MEXICA, 6.95%, 28-Jan-2060',
                'bloomberg': {'yield': 9.87572, 'duration': 9.71461, 'spread': 537.57173}
            },
            {
                'isin': 'US71654QDE98', 'price': 89.55,
                'name': 'PETROLEOS MEXICA, 5.95%, 28-Jan-2031',
                'bloomberg': {'yield': 8.32733, 'duration': 4.46458, 'spread': 382.73346}
            },
            {
                'isin': 'XS2585988145', 'price': 85.54,
                'name': 'GACI FIRST INVST, 5.125%, 14-Feb-2053',
                'bloomberg': {'yield': 6.22763, 'duration': 13.33263, 'spread': 172.76259}
            },
            {
                'isin': 'XS1959337749', 'price': 89.97,
                'name': 'QATAR STATE OF, 4.817%, 14-Mar-2049',
                'bloomberg': {'yield': 5.58469, 'duration': 13.26146, 'spread': 108.46879}
            },
            {
                'isin': 'XS2233188353', 'price': 99.23,
                'name': 'QNB FINANCE LTD, 1.625%, 22-Sep-2025',
                'bloomberg': {'yield': 5.02106, 'duration': 0.22450, 'spread': 52.10619}
            },
            {
                'isin': 'XS2359548935', 'price': 73.79,
                'name': 'QATAR ENERGY, 3.125%, 12-Jul-2041',
                'bloomberg': {'yield': 5.62805, 'duration': 11.51499, 'spread': 112.80529}
            },
            {
                'isin': 'XS0911024635', 'price': 93.29,
                'name': 'SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043',
                'bloomberg': {'yield': 5.66298, 'duration': 11.23839, 'spread': 116.29823}
            },
            {
                'isin': 'USP0R80BAG79', 'price': 97.26,
                'name': 'SITIOS, 5.375%, 04-Apr-2032',
                'bloomberg': {'yield': 5.86969, 'duration': 5.51011, 'spread': 136.96853}
            }
        ]
        
        # Initialize Smart Bond Parser
        try:
            self.parser = SmartBondParser()
            self.parser_available = True
        except Exception as e:
            logger.warning(f"Smart Bond Parser not available: {e}")
            self.parser_available = False
    
    def init_database(self):
        """Initialize SQLite database for storing results"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create comprehensive results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bond_test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_timestamp TEXT,
                    bond_isin TEXT,
                    bond_name TEXT,
                    bloomberg_baseline_yield REAL,
                    bloomberg_baseline_duration REAL,
                    bloomberg_baseline_spread REAL,
                    method_1_yield REAL,
                    method_1_duration REAL,
                    method_1_spread REAL,
                    method_1_status TEXT,
                    method_2_yield REAL,
                    method_2_duration REAL,
                    method_2_spread REAL,
                    method_2_status TEXT,
                    method_3_yield REAL,
                    method_3_duration REAL,
                    method_3_spread REAL,
                    method_3_status TEXT,
                    method_4_yield REAL,
                    method_4_duration REAL,
                    method_4_spread REAL,
                    method_4_status TEXT,
                    method_5_yield REAL,
                    method_5_duration REAL,
                    method_5_spread REAL,
                    method_5_status TEXT,
                    method_6_yield REAL,
                    method_6_duration REAL,
                    method_6_spread REAL,
                    method_6_status TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info(f"Database initialized: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def test_method_1_direct_local_with_isin(self, bond: Dict) -> Dict:
        """Method 1: Direct Local + ISIN (Database lookup)"""
        try:
            if not GA10_AVAILABLE:
                return {'status': 'error', 'error': 'GA10 not available'}
            
            portfolio_data = {
                'data': [{
                    'isin': bond['isin'],
                    'price': bond['price'],
                    'weighting': 1.0
                }]
            }
            
            # Use the correct GA10 function with proper database paths
            results = process_bond_portfolio(
                portfolio_data=portfolio_data,
                db_path=self.main_db_path,
                validated_db_path=self.validated_db_path,
                bloomberg_db_path=self.bloomberg_db_path,
                settlement_date=self.settlement_date
            )
            
            if results and len(results) > 0:
                result = results[0]
                if result.get('successful', False):
                    return {
                        'status': 'success',
                        'yield': result.get('yield', 0) * 100,  # Convert to percentage
                        'duration': result.get('duration', 0),
                        'spread': result.get('g_spread', 0)  # Use g_spread for treasury spread
                    }
                else:
                    return {'status': 'error', 'error': result.get('error', 'Calculation failed')}
            else:
                return {'status': 'error', 'error': 'No results returned'}
                
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def test_method_2_direct_local_without_isin(self, bond: Dict) -> Dict:
        """Method 2: Direct Local - ISIN (Smart Parser)"""
        try:
            if not GA10_AVAILABLE or not self.parser_available:
                return {'status': 'error', 'error': 'Parser not available'}
            
            portfolio_data = {
                'data': [{
                    'description': bond['name'],
                    'price': bond['price'],
                    'weighting': 1.0
                }]
            }
            
            # Use the correct GA10 function with description instead of ISIN
            results = process_bond_portfolio(
                portfolio_data=portfolio_data,
                db_path=self.main_db_path,
                validated_db_path=self.validated_db_path,
                bloomberg_db_path=self.bloomberg_db_path,
                settlement_date=self.settlement_date
            )
            
            if results and len(results) > 0:
                result = results[0]
                if result.get('successful', False):
                    return {
                        'status': 'success',
                        'yield': result.get('yield', 0) * 100,  # Convert to percentage
                        'duration': result.get('duration', 0),
                        'spread': result.get('g_spread', 0)  # Use g_spread for treasury spread
                    }
                else:
                    return {'status': 'error', 'error': result.get('error', 'Calculation failed')}
            else:
                return {'status': 'error', 'error': 'No results returned'}
                
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def test_api_method(self, bond: Dict, use_isin: bool, api_url: str) -> Dict:
        """Generic API testing method"""
        try:
            if use_isin:
                payload = {
                    'isin': bond['isin'],
                    'price': bond['price']
                }
            else:
                payload = {
                    'description': bond['name'],
                    'price': bond['price']
                }
            
            # Try multiple possible endpoints
            endpoints = [
                '/api/v1/bond/parse-and-calculate',
                '/api/bond/calculate',
                '/calculate',
                '/bond/calculate'
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.post(
                        f"{api_url}{endpoint}",
                        json=payload,
                        timeout=30,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Extract metrics from various possible response formats
                        yield_val = self._extract_metric(data, ['ytm_semi', 'ytm', 'yield_to_maturity', 'yield'])
                        duration_val = self._extract_metric(data, ['mod_dur_semi', 'modified_duration', 'duration'])
                        spread_val = self._extract_metric(data, ['tsy_spread_semi', 'spread', 'treasury_spread'])
                        
                        return {
                            'status': 'success',
                            'yield': yield_val,
                            'duration': duration_val,
                            'spread': spread_val,
                            'endpoint': endpoint
                        }
                    
                except requests.exceptions.RequestException:
                    continue
            
            return {'status': 'error', 'error': 'All endpoints failed'}
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _extract_metric(self, data: Dict, possible_keys: List[str]) -> float:
        """Extract metric from API response with multiple possible key names"""
        for key in possible_keys:
            if key in data:
                value = data[key]
                return float(value) if value is not None else 0.0
            
            # Check nested structures
            if 'result' in data and isinstance(data['result'], dict) and key in data['result']:
                value = data['result'][key]
                return float(value) if value is not None else 0.0
            
            if 'results' in data and isinstance(data['results'], list) and data['results']:
                if key in data['results'][0]:
                    value = data['results'][0][key]
                    return float(value) if value is not None else 0.0
        
        return 0.0
    
    def test_all_methods_for_bond(self, bond: Dict) -> Dict:
        """Test all 6 methods for a single bond"""
        logger.info(f"Testing bond: {bond['isin']} - {bond['name'][:50]}...")
        
        results = {
            'bond_isin': bond['isin'],
            'bond_name': bond['name'],
            'bloomberg_baseline': bond['bloomberg'],
            'method_results': {}
        }
        
        # Method 1: Direct Local + ISIN
        logger.info("  Testing Method 1: Direct Local + ISIN")
        results['method_results']['method_1'] = self.test_method_1_direct_local_with_isin(bond)
        time.sleep(0.5)  # Rate limiting
        
        # Method 2: Direct Local - ISIN  
        logger.info("  Testing Method 2: Direct Local - ISIN")
        results['method_results']['method_2'] = self.test_method_2_direct_local_without_isin(bond)
        time.sleep(0.5)
        
        # Method 3: Local API + ISIN
        logger.info("  Testing Method 3: Local API + ISIN")
        results['method_results']['method_3'] = self.test_api_method(bond, True, LOCAL_API_URL)
        time.sleep(0.5)
        
        # Method 4: Local API - ISIN
        logger.info("  Testing Method 4: Local API - ISIN") 
        results['method_results']['method_4'] = self.test_api_method(bond, False, LOCAL_API_URL)
        time.sleep(0.5)
        
        # Method 5: Cloud API + ISIN
        logger.info("  Testing Method 5: Cloud API + ISIN")
        results['method_results']['method_5'] = self.test_api_method(bond, True, CLOUD_API_URL)
        time.sleep(0.5)
        
        # Method 6: Cloud API - ISIN
        logger.info("  Testing Method 6: Cloud API - ISIN")
        results['method_results']['method_6'] = self.test_api_method(bond, False, CLOUD_API_URL)
        
        return results
    
    def save_results_to_database(self, bond_results: Dict):
        """Save individual bond results to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Extract data for database insertion
            test_timestamp = datetime.now().isoformat()
            bond_isin = bond_results['bond_isin']
            bond_name = bond_results['bond_name']
            
            bloomberg = bond_results['bloomberg_baseline']
            bbg_yield = bloomberg['yield']
            bbg_duration = bloomberg['duration'] 
            bbg_spread = bloomberg['spread']
            
            # Method results
            methods = bond_results['method_results']
            
            cursor.execute('''
                INSERT INTO bond_test_results (
                    test_timestamp, bond_isin, bond_name,
                    bloomberg_baseline_yield, bloomberg_baseline_duration, bloomberg_baseline_spread,
                    method_1_yield, method_1_duration, method_1_spread, method_1_status,
                    method_2_yield, method_2_duration, method_2_spread, method_2_status,
                    method_3_yield, method_3_duration, method_3_spread, method_3_status,
                    method_4_yield, method_4_duration, method_4_spread, method_4_status,
                    method_5_yield, method_5_duration, method_5_spread, method_5_status,
                    method_6_yield, method_6_duration, method_6_spread, method_6_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                test_timestamp, bond_isin, bond_name, bbg_yield, bbg_duration, bbg_spread,
                methods.get('method_1', {}).get('yield', 0), methods.get('method_1', {}).get('duration', 0), 
                methods.get('method_1', {}).get('spread', 0), methods.get('method_1', {}).get('status', 'unknown'),
                methods.get('method_2', {}).get('yield', 0), methods.get('method_2', {}).get('duration', 0),
                methods.get('method_2', {}).get('spread', 0), methods.get('method_2', {}).get('status', 'unknown'),
                methods.get('method_3', {}).get('yield', 0), methods.get('method_3', {}).get('duration', 0),
                methods.get('method_3', {}).get('spread', 0), methods.get('method_3', {}).get('status', 'unknown'),
                methods.get('method_4', {}).get('yield', 0), methods.get('method_4', {}).get('duration', 0),
                methods.get('method_4', {}).get('spread', 0), methods.get('method_4', {}).get('status', 'unknown'),
                methods.get('method_5', {}).get('yield', 0), methods.get('method_5', {}).get('duration', 0),
                methods.get('method_5', {}).get('spread', 0), methods.get('method_5', {}).get('status', 'unknown'),
                methods.get('method_6', {}).get('yield', 0), methods.get('method_6', {}).get('duration', 0),
                methods.get('method_6', {}).get('spread', 0), methods.get('method_6', {}).get('status', 'unknown')
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save results to database: {e}")
    
    def calculate_difference_color(self, calculated: float, bloomberg: float, metric_type: str = 'yield') -> str:
        """Calculate color coding based on difference from Bloomberg baseline"""
        if calculated == 0 or bloomberg == 0:
            return 'gray'
        
        if metric_type == 'yield' or metric_type == 'spread':
            # Convert to basis points
            diff_bps = abs((calculated - bloomberg) * 100)
        else:  # duration
            # Use absolute difference for duration
            diff_bps = abs(calculated - bloomberg) * 100  # Convert to comparable scale
        
        if diff_bps <= 5:
            return 'green'    # Excellent: ≤5 bps
        elif diff_bps <= 20:
            return 'yellow'   # Good: 5-20 bps
        elif diff_bps <= 50:
            return 'orange'   # Acceptable: 20-50 bps
        else:
            return 'red'      # Needs Investigation: >50 bps
    
    def generate_html_report(self, all_results: List[Dict]) -> str:
        """Generate comprehensive HTML report with color coding"""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Consolidated 6-Way Bond Testing Results</title>
    <style>
        body {{ font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif; margin: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; }}
        .summary {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 8px; text-align: center; border: 1px solid #ddd; font-size: 12px; }}
        th {{ background: #343a40; color: white; font-weight: 600; }}
        .bond-name {{ text-align: left; max-width: 200px; font-weight: 600; }}
        .metric-table {{ margin: 30px 0; }}
        .metric-title {{ font-size: 18px; font-weight: 700; margin: 20px 0 10px 0; color: #343a40; }}
        .green {{ background-color: #d4edda; color: #155724; }}
        .yellow {{ background-color: #fff3cd; color: #856404; }}
        .orange {{ background-color: #ffe6cc; color: #d63384; }}
        .red {{ background-color: #f8d7da; color: #721c24; }}
        .gray {{ background-color: #e9ecef; color: #6c757d; }}
        .legend {{ display: flex; gap: 20px; margin: 20px 0; }}
        .legend-item {{ padding: 5px 10px; border-radius: 4px; font-size: 12px; font-weight: 600; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Consolidated 6-Way Bond Testing Results</h1>
        <p>Complete Analysis: Yield, Spread & Duration vs Bloomberg Baseline</p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="legend">
        <div class="legend-item green">Excellent (≤5 bps)</div>
        <div class="legend-item yellow">Good (5-20 bps)</div>
        <div class="legend-item orange">Acceptable (20-50 bps)</div>
        <div class="legend-item red">Investigate (>50 bps)</div>
        <div class="legend-item gray">No Data</div>
    </div>
"""
        
        # Generate tables for each metric
        for metric, title in [('yield', 'Yield to Maturity (%)'), ('duration', 'Modified Duration (Years)'), ('spread', 'Treasury Spread (bps)')]:
            html += f"""
    <div class="metric-table">
        <div class="metric-title">📊 {title}</div>
        <table>
            <thead>
                <tr>
                    <th>ISIN</th>
                    <th>Bond Name</th>
                    <th>Bloomberg</th>
                    <th>Method 1<br>Direct+ISIN</th>
                    <th>Method 2<br>Direct-ISIN</th>
                    <th>Method 3<br>API+ISIN</th>
                    <th>Method 4<br>API-ISIN</th>
                    <th>Method 5<br>Cloud+ISIN</th>
                    <th>Method 6<br>Cloud-ISIN</th>
                </tr>
            </thead>
            <tbody>
"""
            
            for result in all_results:
                bond_isin = result['bond_isin']
                bond_name = result['bond_name'][:50] + "..." if len(result['bond_name']) > 50 else result['bond_name']
                bloomberg_val = result['bloomberg_baseline'][metric]
                
                html += f"""
                <tr>
                    <td><code>{bond_isin}</code></td>
                    <td class="bond-name">{bond_name}</td>
                    <td><strong>{bloomberg_val:.3f}</strong></td>
"""
                
                for method_num in range(1, 7):
                    method_key = f'method_{method_num}'
                    method_data = result['method_results'].get(method_key, {})
                    
                    if method_data.get('status') == 'success':
                        calculated_val = method_data.get(metric, 0)
                        color = self.calculate_difference_color(calculated_val, bloomberg_val, metric)
                        html += f'<td class="{color}">{calculated_val:.3f}</td>'
                    else:
                        html += f'<td class="gray">Error</td>'
                
                html += "</tr>"
            
            html += """
            </tbody>
        </table>
    </div>
"""
        
        html += """
</body>
</html>
"""
        
        # Save HTML report
        report_path = f"{self.project_root}/consolidated_6way_report_{self.timestamp}.html"
        with open(report_path, 'w') as f:
            f.write(html)
        
        logger.info(f"HTML report saved: {report_path}")
        return report_path
    
    def archive_old_files(self):
        """Archive old testing files to reduce clutter"""
        try:
            archive_dir = f"{self.project_root}/archive"
            os.makedirs(archive_dir, exist_ok=True)
            
            # Files to archive (not the new consolidated version)
            files_to_archive = [
                'comprehensive_6way_tester copy.py',
                'comprehensive_6way_tester.py',
                'comprehensive_6way_tester_FIXED.py',
                'comprehensive_6way_tester_FIXED_ENDPOINTS.py',
                'comprehensive_6way_tester_refactored.py'
            ]
            
            for filename in files_to_archive:
                source_path = f"{self.project_root}/{filename}"
                if os.path.exists(source_path):
                    archive_path = f"{archive_dir}/{filename}.archived_{self.timestamp}"
                    shutil.move(source_path, archive_path)
                    logger.info(f"Archived: {filename}")
            
            # Archive old database files (keep only most recent 5)
            db_files = list(Path(self.project_root).glob("six_way_analysis_*.db"))
            db_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            for old_db in db_files[5:]:  # Keep 5 most recent, archive rest
                archive_path = f"{archive_dir}/{old_db.name}.archived_{self.timestamp}"
                shutil.move(str(old_db), archive_path)
                logger.info(f"Archived old database: {old_db.name}")
            
        except Exception as e:
            logger.warning(f"Archive operation failed: {e}")
    
    def run_comprehensive_test(self) -> str:
        """Run the complete 6-way test on all 25 bonds"""
        logger.info("🚀 Starting Consolidated 6-Way Comprehensive Test")
        logger.info(f"Testing {len(self.test_portfolio)} bonds across 6 methods")
        logger.info(f"Database: {self.db_path}")
        
        start_time = time.time()
        all_results = []
        
        try:
            for i, bond in enumerate(self.test_portfolio, 1):
                logger.info(f"\n--- Bond {i}/{len(self.test_portfolio)} ---")
                
                # Test all methods for this bond
                bond_results = self.test_all_methods_for_bond(bond)
                all_results.append(bond_results)
                
                # Save to database
                self.save_results_to_database(bond_results)
                
                # Progress indicator
                if i % 5 == 0:
                    elapsed = time.time() - start_time
                    avg_time = elapsed / i
                    remaining = (len(self.test_portfolio) - i) * avg_time
                    logger.info(f"Progress: {i}/{len(self.test_portfolio)} ({i/len(self.test_portfolio)*100:.1f}%) - ETA: {remaining/60:.1f} minutes")
            
            # Generate HTML report
            report_path = self.generate_html_report(all_results)
            
            # Archive old files
            self.archive_old_files()
            
            # Summary statistics
            total_time = time.time() - start_time
            logger.info(f"\n🎉 Test Complete!")
            logger.info(f"Total time: {total_time/60:.1f} minutes")
            logger.info(f"Database: {self.db_path}")
            logger.info(f"HTML Report: {report_path}")
            
            return report_path
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            logger.error(traceback.format_exc())
            raise

def main():
    """Main execution function"""
    try:
        tester = ConsolidatedSixWayTester()
        report_path = tester.run_comprehensive_test()
        print(f"\n✅ SUCCESS: Comprehensive test complete!")
        print(f"📊 HTML Report: {report_path}")
        print(f"💾 Database: {tester.db_path}")
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        print(traceback.format_exc())
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
