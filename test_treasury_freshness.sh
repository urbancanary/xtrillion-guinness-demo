#!/bin/bash
# Test treasury data freshness across environments

echo "🏦 Testing Treasury Yield Data Freshness"
echo "========================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test production
echo -e "\n${YELLOW}Production Environment:${NC}"
curl -s -X GET https://future-footing-414610.uc.r.appspot.com/api/v1/treasury/status \
  -H "X-API-Key: gax10_demo_3j5h8m9k2p6r4t7w1q" | python3 -m json.tool

# Test development
echo -e "\n${YELLOW}Development Environment:${NC}"
curl -s -X GET https://development-dot-future-footing-414610.uc.r.appspot.com/api/v1/treasury/status \
  -H "X-API-Key: gax10_demo_3j5h8m9k2p6r4t7w1q" | python3 -m json.tool

# Test local if running
echo -e "\n${YELLOW}Local Environment (if running):${NC}"
curl -s -X GET http://localhost:8080/api/v1/treasury/status \
  -H "X-API-Key: gax10_demo_3j5h8m9k2p6r4t7w1q" | python3 -m json.tool 2>/dev/null || echo "Local server not running"

echo -e "\n✅ Treasury data check complete"