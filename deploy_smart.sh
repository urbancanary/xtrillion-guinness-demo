#!/bin/bash

# ============================================
# SMART DEPLOYMENT SYSTEM WITH SAFETY CHECKS
# ============================================
# Enforces: Development → Maia-Dev → Production
# Prevents accidental production deployments

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Deployment tracker file
TRACKER_FILE=".deployment_tracker.json"

# Get current git commit
COMMIT_HASH=$(git rev-parse --short HEAD)
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
CURRENT_BRANCH=$(git branch --show-current)

# Function to update deployment tracker
update_tracker() {
    local environment=$1
    local version=$2
    local status=$3
    
    # Update tracker using Python for JSON handling
    python3 << EOF
import json
import datetime

with open('$TRACKER_FILE', 'r') as f:
    tracker = json.load(f)

# Add to history
tracker['deployment_history'].append({
    'environment': '$environment',
    'version': '$version',
    'commit': '$COMMIT_HASH',
    'branch': '$CURRENT_BRANCH',
    'timestamp': datetime.datetime.now().isoformat(),
    'status': '$status'
})

# Update current stage
if '$status' == 'success':
    tracker['current_stage']['$environment'] = {
        'version': '$version',
        'commit': '$COMMIT_HASH',
        'timestamp': datetime.datetime.now().isoformat()
    }

# Keep only last 100 history entries
tracker['deployment_history'] = tracker['deployment_history'][-100:]

with open('$TRACKER_FILE', 'w') as f:
    json.dump(tracker, f, indent=2)
EOF
}

# Function to check if deployment is allowed
check_deployment_allowed() {
    local target_env=$1
    
    python3 << EOF
import json
import sys
from datetime import datetime, timedelta

with open('$TRACKER_FILE', 'r') as f:
    tracker = json.load(f)

target = '$target_env'
current = tracker['current_stage']

# Check deployment order
if target == 'maia-dev':
    # Must deploy to development first
    if not current['development']:
        print("ERROR: Must deploy to development first!")
        sys.exit(1)
    
    # Check if development version is newer than maia-dev
    dev_commit = current['development'].get('commit', '')
    if current['maia-dev'] and current['maia-dev'].get('commit', '') == dev_commit:
        print("WARNING: This version already deployed to maia-dev")

elif target == 'production':
    # Must deploy to maia-dev first
    if not current['maia-dev']:
        print("ERROR: Must deploy to maia-dev first!")
        sys.exit(1)
    
    # Check minimum testing time in maia-dev
    maia_time = datetime.fromisoformat(current['maia-dev']['timestamp'])
    hours_in_maia = (datetime.now() - maia_time).total_seconds() / 3600
    
    if hours_in_maia < tracker['rules']['minimum_maia_hours']:
        print(f"ERROR: Must test in maia-dev for at least {tracker['rules']['minimum_maia_hours']} hours!")
        print(f"Current time in maia-dev: {hours_in_maia:.1f} hours")
        sys.exit(1)
    
    # Check if maia-dev version matches what we're deploying
    maia_commit = current['maia-dev'].get('commit', '')
    if maia_commit != '$COMMIT_HASH':
        print(f"ERROR: Current commit ({COMMIT_HASH}) doesn't match maia-dev ({maia_commit})")
        print("Deploy to maia-dev first with current changes!")
        sys.exit(1)

print("ALLOWED")
EOF
}

# Function to show deployment status
show_status() {
    echo -e "${CYAN}📊 DEPLOYMENT STATUS${NC}"
    echo "================================"
    
    python3 << EOF
import json
from datetime import datetime

with open('$TRACKER_FILE', 'r') as f:
    tracker = json.load(f)

current = tracker['current_stage']

for env in ['development', 'maia-dev', 'production']:
    if current[env]:
        deployed_time = datetime.fromisoformat(current[env]['timestamp'])
        age = datetime.now() - deployed_time
        hours = age.total_seconds() / 3600
        
        print(f"{env:12} ✅ v{current[env]['version']} ({hours:.1f} hours old)")
        print(f"              Commit: {current[env]['commit']}")
    else:
        print(f"{env:12} ❌ Not deployed")
EOF
    
    echo "================================"
}

# Main menu
echo -e "${BLUE}🚀 SMART DEPLOYMENT SYSTEM${NC}"
echo "================================"
show_status
echo ""
echo "Select deployment target:"
echo "1) Development (Your Testing)"
echo "2) Maia-Dev (Team Testing)"
echo "3) Production (Live)"
echo "4) Show Deployment History"
echo "5) Exit"
echo ""
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        # Deploy to Development
        echo -e "${YELLOW}🔧 DEPLOYING TO DEVELOPMENT${NC}"
        echo "This is YOUR personal testing environment"
        echo ""
        
        VERSION="dev-$TIMESTAMP-$COMMIT_HASH"
        update_tracker "development" "$VERSION" "started"
        
        # Run deployment
        echo -e "${YELLOW}📦 Building and deploying...${NC}"
        if ./deploy_development.sh; then
            update_tracker "development" "$VERSION" "success"
            echo -e "${GREEN}✅ Successfully deployed to development!${NC}"
            echo ""
            echo "Test with Google Sheets:"
            echo '  =XT_SMART(A2:A10, B2:B10, , , "testing")'
            echo ""
            echo -e "${CYAN}Next step: Test thoroughly, then deploy to maia-dev${NC}"
        else
            update_tracker "development" "$VERSION" "failed"
            echo -e "${RED}❌ Deployment failed!${NC}"
            exit 1
        fi
        ;;
        
    2)
        # Deploy to Maia-Dev
        echo -e "${YELLOW}🔧 DEPLOYING TO MAIA-DEV${NC}"
        echo "This is for MAIA TEAM testing"
        echo ""
        
        # Check if allowed
        check_result=$(check_deployment_allowed "maia-dev")
        if [[ $check_result == ERROR* ]]; then
            echo -e "${RED}$check_result${NC}"
            exit 1
        elif [[ $check_result == WARNING* ]]; then
            echo -e "${YELLOW}$check_result${NC}"
            read -p "Continue anyway? (y/N): " confirm
            if [[ ! $confirm =~ ^[Yy]$ ]]; then
                exit 0
            fi
        fi
        
        VERSION="maia-$TIMESTAMP-$COMMIT_HASH"
        update_tracker "maia-dev" "$VERSION" "started"
        
        # Run deployment
        echo -e "${YELLOW}📦 Building and deploying...${NC}"
        if ./deploy_maia_dev.sh; then
            update_tracker "maia-dev" "$VERSION" "success"
            echo -e "${GREEN}✅ Successfully deployed to maia-dev!${NC}"
            echo ""
            echo "Maia team can test with:"
            echo '  =XT_SMART(A2:A10, B2:B10, , , "maia_dev")'
            echo ""
            echo -e "${CYAN}Next step: After 24+ hours of testing, deploy to production${NC}"
        else
            update_tracker "maia-dev" "$VERSION" "failed"
            echo -e "${RED}❌ Deployment failed!${NC}"
            exit 1
        fi
        ;;
        
    3)
        # Deploy to Production
        echo -e "${RED}⚠️  PRODUCTION DEPLOYMENT${NC}"
        echo "This will affect ALL LIVE USERS!"
        echo ""
        
        # Check if allowed
        check_result=$(check_deployment_allowed "production")
        if [[ $check_result == ERROR* ]]; then
            echo -e "${RED}$check_result${NC}"
            exit 1
        fi
        
        echo -e "${YELLOW}⚠️  FINAL CONFIRMATION REQUIRED${NC}"
        echo "You are about to deploy to PRODUCTION"
        echo "Current commit: $COMMIT_HASH"
        echo ""
        read -p "Type 'DEPLOY TO PRODUCTION' to confirm: " confirm
        if [ "$confirm" != "DEPLOY TO PRODUCTION" ]; then
            echo "Production deployment cancelled."
            exit 0
        fi
        
        VERSION="prod-$TIMESTAMP-$COMMIT_HASH"
        update_tracker "production" "$VERSION" "started"
        
        # Run deployment
        echo -e "${YELLOW}📦 Building and deploying to PRODUCTION...${NC}"
        if ./deploy_production.sh; then
            update_tracker "production" "$VERSION" "success"
            echo -e "${GREEN}✅ Successfully deployed to PRODUCTION!${NC}"
            echo ""
            echo "Production is now live with version $VERSION"
        else
            update_tracker "production" "$VERSION" "failed"
            echo -e "${RED}❌ Production deployment failed!${NC}"
            exit 1
        fi
        ;;
        
    4)
        # Show deployment history
        echo -e "${CYAN}📜 DEPLOYMENT HISTORY (Last 10)${NC}"
        echo "================================"
        python3 << EOF
import json
from datetime import datetime

with open('$TRACKER_FILE', 'r') as f:
    tracker = json.load(f)

history = tracker['deployment_history'][-10:]
for entry in reversed(history):
    timestamp = datetime.fromisoformat(entry['timestamp'])
    status_emoji = "✅" if entry['status'] == "success" else "❌"
    print(f"{timestamp.strftime('%Y-%m-%d %H:%M')} {status_emoji} {entry['environment']:12} {entry['version']}")
EOF
        ;;
        
    5)
        echo "Deployment cancelled."
        exit 0
        ;;
        
    *)
        echo -e "${RED}Invalid choice!${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}📊 Updated Deployment Status:${NC}"
show_status