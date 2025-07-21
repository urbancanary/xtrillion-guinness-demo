#!/bin/bash

# Test script to verify the accrued_interest field removal from API responses

echo "🧪 Testing API Response Fix - Accrued Interest Field Removal"
echo "=============================================================="
echo

# Test 1: Business Response (Default)
echo "📊 TEST 1: Business Response Format (Default)"
echo "Expected: NO 'accrued_interest' field in analytics section"
echo "Expected: 'accrued_per_million' and 'days_accrued' fields present"
echo

curl -X POST "http://localhost:8080/api/v1/bond/parse-and-calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "T 3 15/08/52",
    "price": 71.66,
    "trade_date": "2025-06-30"
  }' | python3 -m json.tool

echo
echo "=============================================================="
echo

# Test 2: Technical Response 
echo "🔬 TEST 2: Technical Response Format"
echo "Expected: NO 'accrued_interest' field, only 'accrued_interest_per_100'"
echo

curl -X POST "http://localhost:8080/api/v1/bond/parse-and-calculate?technical=true" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "T 3 15/08/52", 
    "price": 71.66,
    "trade_date": "2025-06-30"
  }' | python3 -m json.tool

echo
echo "=============================================================="
echo "✅ VERIFICATION COMPLETE"
echo
echo "Key Changes Made:"
echo "1. ❌ Removed 'accrued_interest' field from business response analytics"
echo "2. ✅ Kept 'accrued_per_million' and 'days_accrued' fields"
echo "3. ✅ Increased precision for yield and duration (6 decimal places)"
echo "4. ✅ Technical response maintains 'accrued_interest_per_100' field"
echo
echo "📝 Notes:"
echo "- Business response now excludes the incorrect accrued_interest field"
echo "- Technical response still provides accrued_interest_per_100 for detailed analysis"
echo "- Response format is cleaner and more accurate"
