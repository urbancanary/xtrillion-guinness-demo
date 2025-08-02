#!/bin/bash
# Production Deployment Script - LOCKED VERSION
# Only for critical hotfixes after extensive testing

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${RED}🔒 PRODUCTION DEPLOYMENT - LOCKED VERSION${NC}"
echo "========================================================"
echo "This deploys to the LOCKED production environment"
echo "External users depend on this version being stable!"
echo ""

# Safety check
read -p "Are you sure you want to deploy to PRODUCTION? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Deployment cancelled."
    exit 1
fi

# Check if we're on main branch (required for production)
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    echo -e "${RED}❌ ERROR: Must be on 'main' branch for production deployment${NC}"
    echo "Current branch: $current_branch"
    echo "Switch to main branch: git checkout main"
    exit 1
fi

# Check for uncommitted changes
if [[ -n $(git status --porcelain) ]]; then
    echo -e "${RED}❌ ERROR: Uncommitted changes detected${NC}"
    echo "Commit or stash changes before deploying to production"
    git status
    exit 1
fi

# Get current version
VERSION=$(git describe --tags --exact-match 2>/dev/null || echo "v10.0.0")
echo -e "${YELLOW}📋 Deploying version: $VERSION${NC}"

# Pre-deployment checks
echo -e "${YELLOW}🔍 Running pre-deployment checks...${NC}"

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

# Backup current production version
echo -e "${YELLOW}💾 Creating production backup...${NC}"
BACKUP_DIR="archive/production_backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
gcloud app versions list --service=default --format="value(id)" | head -1 > "$BACKUP_DIR/previous_version.txt"
echo "  ✅ Backup created in $BACKUP_DIR"

# Deploy to production
echo -e "${YELLOW}🚀 Deploying to production...${NC}"
gcloud app deploy app.production.yaml \
    --version="$(echo $VERSION | tr '.' '-')" \
    --promote \
    --stop-previous-version \
    --quiet

# Verify deployment
echo -e "${YELLOW}🔍 Verifying deployment...${NC}"
sleep 30  # Wait for deployment to stabilize

# Health check
HEALTH_URL="https://future-footing-414610.uc.r.appspot.com/health"
echo "  - Checking health endpoint..."
HEALTH_RESPONSE=$(curl -s "$HEALTH_URL" || echo "FAILED")
if echo "$HEALTH_RESPONSE" | grep -q '"status": "healthy"'; then
    echo "  ✅ Health check passed"
else
    echo -e "  ${RED}❌ Health check failed${NC}"
    echo "  Response: $HEALTH_RESPONSE"
    exit 1
fi

# Test critical API endpoint
echo "  - Testing bond analysis endpoint..."
API_RESPONSE=$(curl -s -X POST "$HEALTH_URL/../api/v1/bond/analysis" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: gax10_demo_3j5h8m9k2p6r4t7w1q" \
    -d '{"description": "T 3 15/08/52", "price": 71.66}' || echo "FAILED")

if echo "$API_RESPONSE" | grep -q '"status": "success"'; then
    echo "  ✅ API test passed"
else
    echo -e "  ${RED}❌ API test failed${NC}"
    echo "  Response: $API_RESPONSE"
    
    # Auto-rollback on failure
    echo -e "${YELLOW}🔄 Auto-rolling back...${NC}"
    PREVIOUS_VERSION=$(cat "$BACKUP_DIR/previous_version.txt")
    gcloud app services set-traffic default --splits="$PREVIOUS_VERSION=100" --quiet
    exit 1
fi

echo ""
echo -e "${GREEN}✅ PRODUCTION DEPLOYMENT SUCCESSFUL!${NC}"
echo "========================================================"
echo "Version: $VERSION"
echo "URL: https://future-footing-414610.uc.r.appspot.com"
echo "Health: $HEALTH_URL"
echo "Backup: $BACKUP_DIR"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "1. Monitor production metrics for 30 minutes"
echo "2. Update external user documentation if needed"
echo "3. Notify external users of any changes (if applicable)"
echo ""
echo -e "${GREEN}🎉 External users can continue using the stable API!${NC}"
