#!/bin/bash
#
# Verify Treasury Deployment
# Checks if the production API is using updated Treasury data
#

echo "🔍 Verifying Treasury Data in Production"
echo "======================================"
echo ""

# Check local database
echo "📁 Local Database:"
LOCAL_DATE=$(sqlite3 bonds_data.db "SELECT MAX(Date) FROM tsys_enhanced;" 2>/dev/null || echo "Error")
echo "   Latest Treasury date: $LOCAL_DATE"
echo ""

# Check API response
echo "🌐 Production API Test:"
echo "   URL: https://future-footing-414610.uc.r.appspot.com"
echo "   Testing 10Y Treasury at par..."
echo ""

# API call for a 10Y Treasury at par
RESPONSE=$(curl -s -X POST https://future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_test_9r4t7w2k5m8p1z6x3v" \
  -d '{
    "description": "T 4.25 05/15/35",
    "price": 100.0,
    "settlement_date": "2025-07-31"
  }')

# Parse response
if echo "$RESPONSE" | grep -q "analytics"; then
    YTM=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('analytics', {}).get('ytm', 'N/A'))")
    echo "✅ API Response:"
    echo "   YTM: ${YTM}%"
    echo "   Expected: ~4.25% (bond coupon rate)"
    echo ""
    
    # Analysis
    echo "📊 Analysis:"
    if [[ "$YTM" == "4.249"* ]]; then
        echo "   ✅ YTM matches expected value!"
        echo "   ✅ API is likely using July 31 Treasury data"
    else
        echo "   ⚠️  YTM doesn't match expected value"
        echo "   ⚠️  API might be using older Treasury data"
    fi
else
    echo "❌ API Error:"
    echo "$RESPONSE" | head -n 5
fi

echo ""
echo "Note: Full verification requires checking the actual yield curve data"
echo "      used in spread calculations, which requires Z-spread implementation."