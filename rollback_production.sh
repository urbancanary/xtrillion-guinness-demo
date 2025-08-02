#!/bin/bash
# Production Rollback Script
# For emergency rollback to previous stable version

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${RED}🔄 EMERGENCY PRODUCTION ROLLBACK${NC}"
echo "========================================"
echo "This will rollback production to a previous version"
echo ""

# Check parameters
if [ $# -eq 0 ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 v10.0.0"
    echo ""
    echo "Available versions:"
    gcloud app versions list --service=default --format="table(id,traffic_split)" | head -10
    exit 1
fi

TARGET_VERSION=$1
TARGET_VERSION_FORMATTED=$(echo $TARGET_VERSION | tr '.' '-')

echo -e "${YELLOW}🎯 Target version: $TARGET_VERSION${NC}"
echo -e "${YELLOW}🎯 Formatted version: $TARGET_VERSION_FORMATTED${NC}"
echo ""

# Safety confirmation
echo -e "${RED}⚠️  WARNING: This will affect external users!${NC}"
echo "External users will be switched to version $TARGET_VERSION"
read -p "Are you absolutely sure? Type 'ROLLBACK' to confirm: " confirm

if [ "$confirm" != "ROLLBACK" ]; then
    echo "Rollback cancelled."
    exit 1
fi

# Check if target version exists
echo -e "${YELLOW}🔍 Checking if version exists...${NC}"
if ! gcloud app versions describe "$TARGET_VERSION_FORMATTED" --service=default >/dev/null 2>&1; then
    echo -e "${RED}❌ ERROR: Version $TARGET_VERSION_FORMATTED not found${NC}"
    echo ""
    echo "Available versions:"
    gcloud app versions list --service=default --format="table(id,traffic_split)"
    exit 1
fi

# Get current version for backup
CURRENT_VERSION=$(gcloud app versions list --service=default --filter="traffic_split>0" --format="value(id)")
echo -e "${YELLOW}📋 Current version: $CURRENT_VERSION${NC}"

# Perform rollback
echo -e "${YELLOW}🔄 Rolling back to $TARGET_VERSION...${NC}"
gcloud app services set-traffic default --splits="$TARGET_VERSION_FORMATTED=100" --quiet

# Verify rollback
echo -e "${YELLOW}🔍 Verifying rollback...${NC}"
sleep 20  # Wait for traffic switch

# Health check
HEALTH_URL="https://future-footing-414610.uc.r.appspot.com/health"
echo "  - Checking health endpoint..."
HEALTH_RESPONSE=$(curl -s "$HEALTH_URL" || echo "FAILED")
if echo "$HEALTH_RESPONSE" | grep -q '"status": "healthy"'; then
    echo "  ✅ Health check passed"
else
    echo -e "  ${RED}❌ Health check failed${NC}"
    echo "  Response: $HEALTH_RESPONSE"
    
    # Emergency re-rollback
    echo -e "${YELLOW}🚨 Emergency re-rollback to previous version...${NC}"
    gcloud app services set-traffic default --splits="$CURRENT_VERSION=100" --quiet
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
    
    # Emergency re-rollback
    echo -e "${YELLOW}🚨 Emergency re-rollback to previous version...${NC}"
    gcloud app services set-traffic default --splits="$CURRENT_VERSION=100" --quiet
    exit 1
fi

# Log rollback
ROLLBACK_LOG="archive/rollback_logs/rollback_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "$(dirname "$ROLLBACK_LOG")"
cat > "$ROLLBACK_LOG" << EOF
Rollback performed at: $(date)
From version: $CURRENT_VERSION
To version: $TARGET_VERSION_FORMATTED
Reason: Emergency rollback
Performed by: $(whoami)
Git commit: $(git rev-parse HEAD)
Health check: PASSED
API test: PASSED
EOF

echo ""
echo -e "${GREEN}✅ ROLLBACK SUCCESSFUL!${NC}"
echo "========================================"
echo "Rolled back from: $CURRENT_VERSION"
echo "Rolled back to: $TARGET_VERSION_FORMATTED"
echo "Current URL: https://future-footing-414610.uc.r.appspot.com"
echo "Log file: $ROLLBACK_LOG"
echo ""
echo -e "${YELLOW}📝 Post-Rollback Actions:${NC}"
echo "1. Monitor production metrics"
echo "2. Investigate root cause of issue"
echo "3. Prepare hotfix if needed"
echo "4. Notify external users if necessary"
echo "5. Update incident log"
echo ""
echo -e "${GREEN}🎯 External users now using stable version $TARGET_VERSION${NC}"
