#!/usr/bin/env python3
"""
Test 25-Bond Portfolio with New /analysis Endpoint
=================================================

Test the new /api/v1/portfolio/analysis endpoint with:
1. ISIN-based lookup
2. Description-based lookup

Compare results and validate portfolio-level calculations.
"""

import requests
import json
from datetime import datetime

# API Configuration
BASE_URL = "https://future-footing-414610.uc.r.appspot.com"
API_KEY = "gax10_demo_3j5h8m9k2p6r4t7w1q"

headers = {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
}

# Test Portfolio Data - 25 Bonds with ISIN, Price, Name, Expected Metrics
portfolio_data = [
    {"isin": "US912810TJ79", "price": 71.66, "name": "T 3 15/08/52", "exp_duration": 16.357839, "exp_yield": 4.898453, "exp_spread": None},
    {"isin": "XS2249741674", "price": 77.88, "name": "GALAXY PIPELINE, 3.25%, 30-Sep-2040", "exp_duration": 10.097620, "exp_yield": 5.637570, "exp_spread": 118},
    {"isin": "XS1709535097", "price": 89.40, "name": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047", "exp_duration": 9.815219, "exp_yield": 5.717451, "exp_spread": 123},
    {"isin": "XS1982113463", "price": 87.14, "name": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039", "exp_duration": 9.927596, "exp_yield": 5.599746, "exp_spread": 111},
    {"isin": "USP37466AS18", "price": 80.39, "name": "EMPRESA METRO, 4.7%, 07-May-2050", "exp_duration": 13.189567, "exp_yield": 6.265800, "exp_spread": 144},
    {"isin": "USP3143NAH72", "price": 101.63, "name": "CODELCO INC, 6.15%, 24-Oct-2036", "exp_duration": 8.024166, "exp_yield": 5.949058, "exp_spread": 160},
    {"isin": "USP30179BR86", "price": 86.42, "name": "COMISION FEDERAL, 6.264%, 15-Feb-2052", "exp_duration": 11.583500, "exp_yield": 7.442306, "exp_spread": 261},
    {"isin": "US195325DX04", "price": 52.71, "name": "COLOMBIA REP OF, 3.875%, 15-Feb-2061", "exp_duration": 12.975798, "exp_