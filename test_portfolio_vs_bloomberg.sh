#!/bin/bash

# 🏦 Complete 25-Bond Portfolio Validation Test
# Tests API against Bloomberg Terminal Data

echo "🏦 Starting Complete Portfolio Validation Against Bloomberg Data"
echo "=================================================================="

# Bloomberg Reference Data (25 bonds)
BLOOMBERG_DATA='{
  "bonds": [
    {"isin": "US912810TJ79", "price": 71.66, "name": "US TREASURY N/B, 3%, 15-Aug-2052", "bbg_duration": 16.36, "bbg_yield": 4.90, "bbg_spread": null, "weight": 1.03},
    {"isin": "XS2249741674", "price": 77.88, "name": "GALAXY PIPELINE, 3.25%, 30-Sep-2040", "bbg_duration": 10.10, "bbg_yield": 5.64, "bbg_spread": 118, "weight": 3.88},
    {"isin": "XS1709535097", "price": 89.40, "name": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047", "bbg_duration": 9.82, "bbg_yield": 5.72, "bbg_spread": 123, "weight": 3.78},
    {"isin": "XS1982113463", "price": 87.14, "name": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039", "bbg_duration": 9.93, "bbg_yield": 5.60, "bbg_spread": 111, "weight": 3.71},
    {"isin": "USP37466AS18", "price": 80.39, "name": "EMPRESA METRO, 4.7%, 07-May-2050", "bbg_duration": 13.19, "bbg_yield": 6.27, "bbg_spread": 144, "weight": 4.57},
    {"isin": "USP3143NAH72", "price": 101.63, "name": "CODELCO INC, 6.15%, 24-Oct-2036", "bbg_duration": 8.02, "bbg_yield": 5.95, "bbg_spread": 160, "weight": 5.79},
    {"isin": "USP30179BR86", "price": 86.42, "name": "COMISION FEDERAL, 6.264%, 15-Feb-2052", "bbg_duration": 11.58, "bbg_yield": 7.44, "bbg_spread": 261, "weight": 6.27},
    {"isin": "US195325DX04", "price": 52.71, "name": "COLOMBIA REP OF, 3.875%, 15-Feb-2061", "bbg_duration": 12.98, "bbg_yield": 7.84, "bbg_spread": 301, "weight": 3.82},
    {"isin": "US279158AJ82", "price": 69.31, "name": "ECOPETROL SA, 5.875%, 28-May-2045", "bbg_duration": 9.81, "bbg_yield": 9.28, "bbg_spread": 445, "weight": 2.93},
    {"isin": "USP37110AM89", "price": 76.24, "name": "EMPRESA NACIONAL, 4.5%, 14-Sep-2047", "bbg_duration": 12.39, "bbg_yield": 6.54, "bbg_spread": 171, "weight": 2.73},
    {"isin": "XS2542166231", "price": 103.03, "name": "GREENSAIF PIPELI, 6.129%, 23-Feb-2038", "bbg_duration": 7.21, "bbg_yield": 5.72, "bbg_spread": 146, "weight": 2.96},
    {"isin": "XS2167193015", "price": 64.50, "name": "STATE OF ISRAEL, 3.8%, 13-May-2060", "bbg_duration": 15.27, "bbg_yield": 6.34, "bbg_spread": 151, "weight": 4.14},
    {"isin": "XS1508675508", "price": 82.42, "name": "SAUDI INT BOND, 4.5%, 26-Oct-2046", "bbg_duration": 12.60, "bbg_yield": 5.97, "bbg_spread": 114, "weight": 4.09},
    {"isin": "XS1807299331", "price": 92.21, "name": "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048", "bbg_duration": 11.45, "bbg_yield": 7.06, "bbg_spread": 223, "weight": 6.58},
    {"isin": "US91086QAZ19", "price": 78.00, "name": "UNITED MEXICAN, 5.75%, 12-Oct-2110", "bbg_duration": 13.37, "bbg_yield": 7.37, "bbg_spread": 255, "weight": 1.69},
    {"isin": "USP6629MAD40", "price": 82.57, "name": "MEXICO CITY ARPT, 5.5%, 31-Jul-2047", "bbg_duration": 11.38, "bbg_yield": 7.07, "bbg_spread": 224, "weight": 3.89},
    {"isin": "US698299BL70", "price": 56.60, "name": "PANAMA, 3.87%, 23-Jul-2060", "bbg_duration": 13.49, "bbg_yield": 7.36, "bbg_spread": 253, "weight": 4.12},
    {"isin": "US71654QDF63", "price": 71.42, "name": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060", "bbg_duration": 9.72, "bbg_yield": 9.88, "bbg_spread": 505, "weight": 3.95},
    {"isin": "US71654QDE98", "price": 89.55, "name": "PETROLEOS MEXICA, 5.95%, 28-Jan-2031", "bbg_duration": 4.47, "bbg_yield": 8.32, "bbg_spread": 444, "weight": 1.30},
    {"isin": "XS2585988145", "price": 85.54, "name": "GACI FIRST INVST, 5.125%, 14-Feb-2053", "bbg_duration": 13.33, "bbg_yield": 6.23, "bbg_spread": 140, "weight": 2.78},
    {"isin": "XS1959337749", "price": 89.97, "name": "QATAR STATE OF, 4.817%, 14-Mar-2049", "bbg_duration": 13.26, "bbg_yield": 5.58, "bbg_spread": 76, "weight": 4.50},
    {"isin": "XS2233188353", "price": 99.23, "name": "QNB FINANCE LTD, 1.625%, 22-Sep-2025", "bbg_duration": 0.23, "bbg_yield": 5.02, "bbg_spread": 71, "weight": 4.90},
    {"isin": "XS2359548935", "price": 73.79, "name": "QATAR ENERGY, 3.125%, 12-Jul-2041", "bbg_duration": 11.51, "bbg_yield": 5.63, "bbg_spread": 101, "weight": 3.70},
    {"isin": "XS0911024635", "price": 93.29, "name": "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043", "bbg_duration": 11.24, "bbg_yield": 5.66, "bbg_spread": 95, "weight": 3.32},
    {"isin": "USP0R80BAG79", "price": 97.26, "name": "SITIOS, 5.375%, 04-Apr-2032", "bbg_duration": 5.51, "bbg_yield": 5.87, "bbg_spread": 187, "weight": 3.12}
  ],
  "settlement_date": "2025-07-30"
}'

# API Endpoint
API_URL="http://localhost:8081"

echo "🔍 Testing API Health..."
curl -s "$API_URL/health" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f'✅ API Status: {data.get(\"status\", \"unknown\")}')
    print(f'✅ Service: {data.get(\"service\", \"unknown\")}')
    if 'dual_database_system' in data:
        print(f'✅ Primary DB: {data[\"dual_database_system\"][\"primary_database\"][\"status\"]}')
        print(f'✅ Secondary DB: {data[\"dual_database_system\"][\"secondary_database\"][\"status\"]}')
except:
    print('❌ API Health Check Failed')
    exit(1)
"

echo ""
echo "🏦 Testing Complete Portfolio (25 bonds)..."

# Create portfolio payload for API (using expected format)
PORTFOLIO_PAYLOAD=$(echo "$BLOOMBERG_DATA" | python3 -c "
import json, sys
data = json.load(sys.stdin)
portfolio = {
    'data': [
        {
            'BOND_CD': bond['isin'],
            'CLOSING PRICE': bond['price'], 
            'WEIGHTING': bond['weight'],
            'Inventory Date': '2025/07/30'
        } for bond in data['bonds']
    ]
}
print(json.dumps(portfolio, indent=2))
")

echo "$PORTFOLIO_PAYLOAD" > /tmp/portfolio_test.json

echo "📊 Sending portfolio to API..."
RESPONSE=$(curl -s -X POST "$API_URL/api/v1/portfolio/analyze" \
  -H "Content-Type: application/json" \
  -d "$PORTFOLIO_PAYLOAD")

echo "📈 API Response:"
echo "$RESPONSE" | python3 -m json.tool

echo ""
echo "🔬 Detailed Analysis vs Bloomberg..."

# Create comparison analysis
python3 -c "
import json
import sys

# Bloomberg data
bloomberg_str = '''$BLOOMBERG_DATA'''
bloomberg = json.loads(bloomberg_str)

# API response
try:
    api_response = json.loads('''$RESPONSE''')
    
    print('🏦 BLOOMBERG vs API COMPARISON')
    print('=' * 80)
    
    if 'portfolio_summary' in api_response:
        portfolio = api_response['portfolio_summary']
        print(f'📊 Portfolio Summary:')
        print(f'   Total Bonds: {portfolio.get(\"bond_count\", \"N/A\")}')
        print(f'   Successful: {portfolio.get(\"successful_calculations\", \"N/A\")}')
        print(f'   Failed: {portfolio.get(\"failed_calculations\", \"N/A\")}')
        
        if 'portfolio_yield' in portfolio:
            print(f'   Portfolio Yield: {portfolio[\"portfolio_yield\"]:.2f}%')
        if 'portfolio_duration' in portfolio:
            print(f'   Portfolio Duration: {portfolio[\"portfolio_duration\"]:.2f} years')
        if 'portfolio_spread' in portfolio:
            print(f'   Portfolio Spread: {portfolio[\"portfolio_spread\"]:.0f}bp')
    
    print()
    if 'bond_details' in api_response:
        print('🔍 Individual Bond Comparison:')
        print(f'{"ISIN":<15} {"BBG_YLD":<8} {"API_YLD":<8} {"DIFF":<8} {"BBG_DUR":<8} {"API_DUR":<8} {"STATUS":<10}')
        print('-' * 80)
        
        # Create lookup for Bloomberg data
        bbg_lookup = {bond['isin']: bond for bond in bloomberg['bonds']}
        
        for bond in api_response['bond_details']:
            isin = bond.get('isin', 'N/A')
            bbg_bond = bbg_lookup.get(isin, {})
            
            api_yield = bond.get('yield', 0.0)
            bbg_yield = bbg_bond.get('bbg_yield', 0.0)
            yield_diff = abs(api_yield - bbg_yield) if api_yield and bbg_yield else 999
            
            api_duration = bond.get('duration', 0.0) 
            bbg_duration = bbg_bond.get('bbg_duration', 0.0)
            
            status = '✅ GOOD' if yield_diff < 0.1 else '⚠️  CHECK' if yield_diff < 0.5 else '❌ FAIL'
            
            print(f'{isin:<15} {bbg_yield:<8.2f} {api_yield:<8.2f} {yield_diff:<8.2f} {bbg_duration:<8.2f} {api_duration:<8.2f} {status:<10}')
    
    else:
        print('❌ No bond_details in API response')
        print('Raw response keys:', list(api_response.keys()))
        
except json.JSONDecodeError as e:
    print(f'❌ Failed to parse API response: {e}')
    print('Raw response:', '''$RESPONSE'''[:500])
except Exception as e:
    print(f'❌ Analysis error: {e}')
"

echo ""
echo "🎯 Test Complete!"
echo "📊 Check the comparison above to validate portfolio accuracy against Bloomberg data"

# Cleanup
rm -f /tmp/portfolio_test.json