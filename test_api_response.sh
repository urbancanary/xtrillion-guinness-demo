#!/bin/bash
# Test API endpoints and show responses

echo "=================================================="
echo "🧪 XTrillion API Response Examples"
echo "=================================================="

# 1. Health Check
echo -e "\n1️⃣ HEALTH CHECK:"
echo "curl -X GET https://future-footing-414610.uc.r.appspot.com/health"
echo -e "\nResponse:"
curl -s -X GET https://future-footing-414610.uc.r.appspot.com/health | python3 -m json.tool

# 2. Bond Analysis
echo -e "\n\n2️⃣ BOND ANALYSIS (US Treasury 3% 2052):"
echo 'curl -X POST https://future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_demo_3j5h8m9k2p6r4t7w1q" \
  -d {"description": "T 3 15/08/52", "price": 71.66, "settlement_date": "2025-04-18"}'
echo -e "\nResponse:"
curl -s -X POST https://future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_demo_3j5h8m9k2p6r4t7w1q" \
  -d '{"description": "T 3 15/08/52", "price": 71.66, "settlement_date": "2025-04-18"}' | python3 -m json.tool

# 3. Portfolio Analysis
echo -e "\n\n3️⃣ PORTFOLIO ANALYSIS (2 Bonds):"
echo 'curl -X POST https://future-footing-414610.uc.r.appspot.com/api/v1/portfolio/analysis \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_demo_3j5h8m9k2p6r4t7w1q" \
  -d {"data": [...]}'
echo -e "\nResponse:"
curl -s -X POST https://future-footing-414610.uc.r.appspot.com/api/v1/portfolio/analysis \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_demo_3j5h8m9k2p6r4t7w1q" \
  -d '{
    "data": [
        {"description": "T 3 15/08/52", "CLOSING PRICE": 71.66, "WEIGHTING": 50.0},
        {"description": "T 4.125 15/11/32", "CLOSING PRICE": 99.5, "WEIGHTING": 50.0}
    ]
}' | python3 -m json.tool

echo -e "\n=================================================="