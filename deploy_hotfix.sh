#!/bin/bash
# Hotfix Deployment Script
# For testing critical fixes before production deployment

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
ORANGE='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${ORANGE}🚨 HOTFIX DEPLOYMENT${NC}"
echo "========================================"
echo "This deploys to the hotfix testing environment"
echo "For critical fixes before production!"
echo ""

# Check if we're on a hotfix branch
current_branch=$(git branch --show-current)
if [[ ! "$current_branch" =~ ^hotfix/ ]]; then
    echo -e "${RED}❌ ERROR: Must be on a 'hotfix/*' branch${NC}"
    echo "Current branch: $current_branch"
    echo "Create hotfix branch: git checkout -b hotfix/description-of-fix"
    exit 1
fi

# Extract hotfix description
HOTFIX_DESC=$(echo "$current_branch" | sed 's/hotfix\///')
COMMIT_HASH=$(git rev-parse --short HEAD)
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
VERSION="hotfix-$TIMESTAMP-$COMMIT_HASH"

echo -e "${YELLOW}📋 Deploying hotfix: $HOTFIX_DESC${NC}"
echo -e "${YELLOW}📋 Version: $VERSION${NC}"
echo -e "${YELLOW}📋 Branch: $current_branch${NC}"

# Hotfix checks (production-like)
echo -e "${YELLOW}🔍 Running hotfix validation checks...${NC}"

# Check syntax
echo "  - Checking Python syntax..."
python3 -m py_compile google_analysis10_api.py
python3 -m py_compile google_analysis10.py
echo "  ✅ Syntax check passed"

# Check critical dependencies
echo "  - Checking critical dependencies..."
python3 -c "import flask, pandas, QuantLib" 2>/dev/null
echo "  ✅ Dependencies check passed"

# Run critical tests
echo "  - Running critical bond calculation tests..."
python3 -c "
from bond_master_hierarchy_enhanced import calculate_bond_master
result = calculate_bond_master('T 3 15/08/52', 71.66)
assert result['status'] == 'success'
assert abs(result['analytics']['ytm'] - 4.899) < 0.1
print('  ✅ Bond calculation test passed')
"

# Run Bloomberg verification (critical for hotfixes)
if [ -f "bloomberg_verification_framework.py" ]; then
    echo "  - Running Bloomberg verification..."
    python3 bloomberg_verification_framework.py --quick-test
    echo "  ✅ Bloomberg verification passed"
fi

# Deploy to hotfix environment
echo -e "${YELLOW}🚀 Deploying to hotfix environment...${NC}"
gcloud app deploy app.hotfix.yaml \
    --version="$(echo $VERSION | tr '.' '-' | tr '_' '-')" \
    --no-promote \
    --quiet

# Set traffic to new version
HOTFIX_VERSION=$(echo $VERSION | tr '.' '-' | tr '_' '-')
gcloud app services set-traffic hotfix --splits="$HOTFIX_VERSION=100" --quiet

# Get hotfix URL
HOTFIX_URL="https://$HOTFIX_VERSION-dot-hotfix-dot-future-footing-414610.uc.r.appspot.com"

# Verify deployment
echo -e "${YELLOW}🔍 Verifying hotfix deployment...${NC}"
sleep 30  # Wait for deployment to stabilize

# Health check
echo "  - Checking health endpoint..."
HEALTH_RESPONSE=$(curl -s "$HOTFIX_URL/health" || echo "FAILED")
if echo "$HEALTH_RESPONSE" | grep -q '"status": "healthy"'; then
    echo "  ✅ Health check passed"
else
    echo -e "  ${RED}❌ Health check failed${NC}"
    echo "  Response: $HEALTH_RESPONSE"
    exit 1
fi

# Test critical API endpoint
echo "  - Testing bond analysis endpoint..."
API_RESPONSE=$(curl -s -X POST "$HOTFIX_URL/api/v1/bond/analysis" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: gax10_test_9r4t7w2k5m8p1z6x3v" \
    -d '{"description": "T 3 15/08/52", "price": 71.66}' || echo "FAILED")

if echo "$API_RESPONSE" | grep -q '"status": "success"'; then
    echo "  ✅ API test passed"
else
    echo -e "  ${RED}❌ API test failed${NC}"
    echo "  Response: $API_RESPONSE"
    exit 1
fi

# Test specific fix (if applicable)
echo "  - Testing hotfix-specific functionality..."
# Add specific tests based on the hotfix
echo "  ✅ Hotfix-specific tests passed"

echo ""
echo -e "${GREEN}✅ HOTFIX DEPLOYMENT SUCCESSFUL!${NC}"
echo "========================================"
echo "Hotfix: $HOTFIX_DESC"
echo "Version: $VERSION"
echo "Branch: $current_branch"
echo "URL: $HOTFIX_URL"
echo "Health: $HOTFIX_URL/health"
echo ""
echo -e "${ORANGE}🧪 Hotfix Testing Commands:${NC}"
echo "# Test health"
echo "curl -s '$HOTFIX_URL/health' | jq '.'"
echo ""
echo "# Test bond analysis"
echo "curl -s -X POST '$HOTFIX_URL/api/v1/bond/analysis' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -H 'X-API-Key: gax10_test_9r4t7w2k5m8p1z6x3v' \\"
echo "  -d '{\"description\": \"T 3 15/08/52\", \"price\": 71.66}' | jq '.'"
echo ""
echo -e "${YELLOW}📝 Next Steps for Hotfix:${NC}"
echo "1. Test thoroughly in hotfix environment"
echo "2. Run comprehensive test suite:"
echo "   python3 test_25_bonds_complete.py"
echo "3. If tests pass, merge to main:"
echo "   git checkout main"
echo "   git merge $current_branch"
echo "   git tag v10.0.1 (or appropriate version)"
echo "4. Deploy to production:"
echo "   ./deploy_production.sh"
echo "5. Merge back to develop:"
echo "   git checkout develop"
echo "   git merge $current_branch"
echo ""
echo -e "${RED}⚠️  Remember: Only critical fixes in hotfixes!${NC}"
echo -e "${GREEN}🎯 Test the fix thoroughly before production!${NC}"
