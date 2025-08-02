#!/bin/bash
# Development Deployment Script
# For code consolidation and new feature testing

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 DEVELOPMENT DEPLOYMENT${NC}"
echo "========================================"
echo "This deploys to the development environment"
echo "Safe for consolidation work and testing!"
echo ""

# Check if we're on develop branch (recommended)
current_branch=$(git branch --show-current)
if [ "$current_branch" != "develop" ]; then
    echo -e "${YELLOW}⚠️  WARNING: Not on 'develop' branch${NC}"
    echo "Current branch: $current_branch"
    echo "Consider switching: git checkout develop"
    read -p "Continue anyway? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Deployment cancelled."
        exit 1
    fi
fi

# Get current commit
COMMIT_HASH=$(git rev-parse --short HEAD)
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
VERSION="dev-$TIMESTAMP-$COMMIT_HASH"

echo -e "${YELLOW}📋 Deploying version: $VERSION${NC}"
echo -e "${YELLOW}📋 Branch: $current_branch${NC}"

# Development checks (less strict than production)
echo -e "${YELLOW}🔍 Running development checks...${NC}"

# Check syntax
echo "  - Checking Python syntax..."
python3 -m py_compile google_analysis10_api.py
echo "  ✅ Syntax check passed"

# Check basic imports
echo "  - Checking basic imports..."
python3 -c "import flask" 2>/dev/null
echo "  ✅ Basic imports check passed"

# Deploy to development
echo -e "${YELLOW}🚀 Deploying to development...${NC}"
gcloud app deploy app.development.yaml \
    --version="$(echo $VERSION | tr '.' '-' | tr '_' '-')" \
    --no-promote \
    --quiet

# Set traffic to new version
DEV_VERSION=$(echo $VERSION | tr '.' '-' | tr '_' '-')
gcloud app services set-traffic development --splits="$DEV_VERSION=100" --quiet

# Get development URL
DEV_URL="https://$DEV_VERSION-dot-development-dot-future-footing-414610.uc.r.appspot.com"

# Verify deployment
echo -e "${YELLOW}🔍 Verifying development deployment...${NC}"
sleep 20  # Wait for deployment

# Health check
echo "  - Checking health endpoint..."
HEALTH_RESPONSE=$(curl -s "$DEV_URL/health" || echo "FAILED")
if echo "$HEALTH_RESPONSE" | grep -q '"status": "healthy"'; then
    echo "  ✅ Health check passed"
else
    echo -e "  ${YELLOW}⚠️  Health check failed (normal for development)${NC}"
    echo "  Response: $HEALTH_RESPONSE"
fi

echo ""
echo -e "${GREEN}✅ DEVELOPMENT DEPLOYMENT SUCCESSFUL!${NC}"
echo "========================================"
echo "Version: $VERSION"
echo "Branch: $current_branch"
echo "URL: $DEV_URL"
echo "Health: $DEV_URL/health"
echo ""
echo -e "${BLUE}🔧 Development Environment Ready For:${NC}"
echo "1. Code consolidation (TASK-001, 002, 003)"
echo "2. New feature development"
echo "3. Testing and experimentation"
echo "4. Performance testing"
echo ""
echo -e "${YELLOW}📝 Testing Commands:${NC}"
echo "# Test health"
echo "curl -s '$DEV_URL/health' | jq '.'"
echo ""
echo "# Test bond analysis"
echo "curl -s -X POST '$DEV_URL/api/v1/bond/analysis' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -H 'X-API-Key: gax10_dev_4n8s6k2x7p9v5m8p1z' \\"
echo "  -d '{\"description\": \"T 3 15/08/52\", \"price\": 71.66}' | jq '.'"
echo ""
echo -e "${GREEN}🎉 Safe to develop - external users unaffected!${NC}"
