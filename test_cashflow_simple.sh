#!/bin/bash

# Simple curl commands to test cash flow endpoints

echo "=== Test 1: Get all cash flows for a Treasury bond ==="
curl -X POST "https://api.x-trillion.ai/api/v1/bond/cashflow" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" \
  -d '{
    "bonds": [
      {
        "description": "T 3 15/08/52",
        "nominal": 1000000
      }
    ]
  }'

echo -e "\n\n=== Test 2: Get next cash flow only ==="
curl -X POST "https://api.x-trillion.ai/api/v1/bond/cashflow/next" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" \
  -d '{
    "bonds": [
      {
        "description": "T 3 15/08/52",
        "nominal": 1000000
      }
    ]
  }'

echo -e "\n\n=== Test 3: Get cash flows for next 90 days ==="
curl -X POST "https://api.x-trillion.ai/api/v1/bond/cashflow/period/90" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" \
  -d '{
    "bonds": [
      {
        "description": "T 3 15/08/52",
        "nominal": 1000000
      }
    ]
  }'