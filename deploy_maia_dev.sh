#!/bin/bash

# ============================================
# MAIA DEVELOPMENT DEPLOYMENT SCRIPT
# ============================================
# Deploy to maia-dev environment for Maia team testing
# This is the intermediate step between your testing and production

echo -e "\033[0;34m🔧 MAIA DEVELOPMENT DEPLOYMENT\033[0m"
echo "========================================"
echo "This deploys to the maia-dev environment"
echo "For Maia team testing before production!"
echo ""

# Check if we're on the right branch (develop preferred for maia_dev)
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "develop" ]; then
    echo -e "\033[1;33m⚠️  WARNING: Not on 'develop' branch\033[0m"
    echo "Current branch: $CURRENT_BRANCH"
    echo "Consider switching: git checkout develop"
fi

# Generate version ID with branch info
TIMESTAMP=$(date +%Y%m%d%H%M%S)
COMMIT_HASH=$(git rev-parse --short HEAD)
VERSION_ID="maia-dev-${TIMESTAMP}-${COMMIT_HASH}"

echo -e "\033[1;33m📋 Deploying version: ${VERSION_ID}\033[0m"
echo -e "\033[1;33m📋 Branch: ${CURRENT_BRANCH}\033[0m"

# Validate that we have the maia-dev configuration
if [ ! -f "app.maia_dev.yaml" ]; then
    echo -e "\033[1;31m❌ Error: app.maia_dev.yaml not found!\033[0m"
    echo "Creating maia-dev configuration..."
    
    # Create maia-dev config based on development config
    cat > app.maia_dev.yaml << EOF
# Google Analysis 10 - Maia Development Environment
# For Maia team testing before production deployment

runtime: python311

# Maia development service name
service: maia-dev

# Maia dev entrypoint with moderate scaling
entrypoint: gunicorn --bind :\$PORT --workers 2 --threads 4 --timeout 120 google_analysis10_api:app

env_variables:
  PORT: 8080
  ENVIRONMENT: maia_development
  DATABASE_SOURCE: gcs
  PYTHONPATH: /srv
  VERSION: "maia-dev"
  API_VERSION: "v1-maia-dev"
  EXTERNAL_USERS: "true"
  DEBUG: "false"

# Maia dev scaling - balanced cost/performance
automatic_scaling:
  min_instances: 1  # Always have one instance ready
  max_instances: 5
  target_cpu_utilization: 0.7

# Standard resources for maia development
resources:
  cpu: 1
  memory_gb: 4

# Standard health checks for maia dev
readiness_check:
  path: "/health"
  check_interval_sec: 5
  timeout_sec: 4
  failure_threshold: 3
  success_threshold: 2

liveness_check:
  path: "/health"
  check_interval_sec: 30
  timeout_sec: 4
  failure_threshold: 3
  success_threshold: 2

# Use .gcloudignore for file exclusion
EOF
    
    echo -e "\033[1;32m✅ Created app.maia_dev.yaml configuration\033[0m"
fi

# Pre-deployment checks
echo -e "\033[1;33m🔍 Running maia-dev deployment checks...\033[0m"

# Check Python syntax
echo "  - Checking Python syntax..."
if python3 -m py_compile google_analysis10_api.py; then
    echo "  ✅ Syntax check passed"
else
    echo -e "\033[1;31m  ❌ Syntax check failed\033[0m"
    exit 1
fi

# Check basic imports
echo "  - Checking basic imports..."
if python3 -c "
import sys
sys.path.append('.')
try:
    import google_analysis10_api
    print('  ✅ Basic imports check passed')
except Exception as e:
    print(f'  ❌ Import error: {e}')
    sys.exit(1)
"; then
    :
else
    exit 1
fi

# Deploy to maia-dev
echo -e "\033[1;33m🚀 Deploying to maia-dev environment...\033[0m"

# Deploy with explicit version
gcloud app deploy app.maia_dev.yaml \
  --version="$VERSION_ID" \
  --no-promote \
  --quiet

if [ $? -eq 0 ]; then
    echo -e "\033[1;32m✅ Deployment successful!\033[0m"
    echo ""
    echo -e "\033[1;36m🌐 Maia-Dev Environment URLs:\033[0m"
    echo "📊 API Base: https://${VERSION_ID}-dot-maia-dev-dot-future-footing-414610.uc.r.appspot.com"
    echo "🩺 Health Check: https://${VERSION_ID}-dot-maia-dev-dot-future-footing-414610.uc.r.appspot.com/health"
    echo ""
    echo -e "\033[1;36m📋 Google Sheets Testing:\033[0m"
    echo "Use environment parameter: \"maia_dev\""
    echo "Example: =XT_ARRAY(A2:A10, B2:B10, , \"maia_dev\")"
    echo "Example: =xt_ytm(\"T 3 15/08/52\", 70, , \"maia_dev\")"
    echo ""
    echo -e "\033[1;33m🔄 Next Steps:\033[0m"
    echo "1. Test with Google Sheets using \"maia_dev\" environment"
    echo "2. Verify full precision is working (6+ decimal places)"
    echo "3. Once verified, deploy to production with ./deploy_production.sh"
    echo ""
    echo -e "\033[1;32m🎯 Ready for Maia team testing!\033[0m"
    
    # Promote to traffic if requested
    echo ""
    read -p "🚦 Promote this version to receive traffic? (y/N): " promote
    if [[ $promote =~ ^[Yy]$ ]]; then
        echo "📤 Promoting to receive traffic..."
        gcloud app services set-traffic maia-dev --splits="$VERSION_ID"=100
        echo -e "\033[1;32m✅ Version promoted! Now accessible at:\033[0m"
        echo "https://maia-dev-dot-future-footing-414610.uc.r.appspot.com"
    else
        echo "ℹ️  Version deployed but not promoted. Use --promote flag to send traffic."
    fi
    
else
    echo -e "\033[1;31m❌ Deployment failed!\033[0m"
    exit 1
fi

echo ""
echo -e "\033[1;36m📊 Deployment Summary:\033[0m"
echo "Environment: Maia Development"
echo "Version: $VERSION_ID"
echo "Branch: $CURRENT_BRANCH" 
echo "Status: Ready for testing"
echo "URL Pattern: maia-dev-dot-future-footing-414610.uc.r.appspot.com"