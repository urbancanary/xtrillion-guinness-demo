#!/bin/bash
# Google Analysis 10 - Rollback Script
# Emergency rollback to previous version

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ -z "$1" ]; then
    echo -e "${RED}Error: Please specify service to rollback${NC}"
    echo "Usage: ./rollback.sh [rmb-dev|maia-dev|production]"
    exit 1
fi

SERVICE=$1

case $SERVICE in
    "rmb-dev")
        SERVICE_NAME="rmb-dev"
        ;;
    "maia-dev")
        SERVICE_NAME="maia-dev"
        ;;
    "production")
        SERVICE_NAME="default"
        echo -e "${RED}⚠️  WARNING: Rolling back PRODUCTION${NC}"
        read -p "Are you SURE you want to rollback PRODUCTION? (yes/no) " -r
        if [[ ! $REPLY == "yes" ]]; then
            echo "Rollback cancelled"
            exit 1
        fi
        ;;
    *)
        echo -e "${RED}Error: Invalid service '$SERVICE'${NC}"
        exit 1
        ;;
esac

echo -e "${YELLOW}Fetching version history for $SERVICE_NAME...${NC}"

# Get version list
gcloud app versions list --service=$SERVICE_NAME --project=future-footing-414610

echo ""
read -p "Enter the version ID to rollback to: " VERSION_ID

echo -e "${YELLOW}Rolling back $SERVICE_NAME to version $VERSION_ID...${NC}"

# Perform rollback by setting traffic
gcloud app services set-traffic $SERVICE_NAME \
    --splits=$VERSION_ID=1 \
    --project=future-footing-414610

echo -e "${GREEN}✓ Rollback complete!${NC}"
echo "Service $SERVICE_NAME is now running version $VERSION_ID"

# Log the rollback
echo "Rollback: $SERVICE_NAME to $VERSION_ID at $(date)" >> deployment.log