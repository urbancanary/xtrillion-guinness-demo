#!/bin/bash
# Google Analysis 10 - Deployment Script
# Enforces proper deployment pipeline

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if environment is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Please specify environment${NC}"
    echo "Usage: ./deploy.sh [rmb-dev|maia-dev|production|hotfix]"
    echo ""
    echo "Normal flow: rmb-dev → maia-dev → production"
    echo "Emergency: hotfix → production (use sparingly!)"
    exit 1
fi

ENVIRONMENT=$1
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

case $ENVIRONMENT in
    "hotfix")
        echo -e "${RED}⚠️  HOTFIX DEPLOYMENT${NC}"
        echo "This is for CRITICAL fixes only!"
        
        read -p "Is this a critical production fix? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}Use normal flow: rmb-dev → maia-dev → production${NC}"
            exit 1
        fi
        
        # Deploy to hotfix
        gcloud app deploy app.hotfix.yaml \
            --version="hotfix-${TIMESTAMP}" \
            --quiet \
            --project=future-footing-414610
            
        echo -e "${GREEN}✓ Deployed to: https://hotfix-dot-future-footing-414610.uc.r.appspot.com${NC}"
        echo -e "${YELLOW}Test thoroughly before deploying to production!${NC}"
        ;;
        
    "rmb-dev")
        echo -e "${GREEN}Deploying to RMB Development Environment${NC}"
        echo "This is Andy's experimental environment - breaking changes allowed"
        
        # Deploy to rmb-dev
        gcloud app deploy app.rmb-dev.yaml \
            --version="rmb-${TIMESTAMP}" \
            --quiet \
            --project=future-footing-414610
        
        echo -e "${GREEN}✓ Deployed to: https://rmb-dev-dot-future-footing-414610.uc.r.appspot.com${NC}"
        ;;
        
    "maia-dev")
        echo -e "${YELLOW}Deploying to Maia Development Environment${NC}"
        echo "This is the stable development environment for Maia"
        
        # Check if this is a hotfix
        read -p "Is this a hotfix for Maia Dev? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}Hotfixing Maia Dev directly${NC}"
            VERSION="maia-hotfix-${TIMESTAMP}"
        else
            # Normal flow - confirm rmb-dev was tested
            read -p "Has this been tested in rmb-dev? (y/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo -e "${RED}Please test in rmb-dev first${NC}"
                exit 1
            fi
            VERSION="maia-${TIMESTAMP}"
        fi
        
        # Deploy to maia-dev
        gcloud app deploy app.maia-dev.yaml \
            --version="${VERSION}" \
            --quiet \
            --project=future-footing-414610
            
        echo -e "${GREEN}✓ Deployed to: https://maia-dev-dot-future-footing-414610.uc.r.appspot.com${NC}"
        if [[ $VERSION == maia-hotfix-* ]]; then
            echo -e "${YELLOW}Remember to merge this hotfix back to main!${NC}"
        fi
        ;;
        
    "production")
        echo -e "${RED}⚠️  PRODUCTION DEPLOYMENT${NC}"
        echo "This will deploy to the live production environment"
        
        # Multiple confirmations for production
        read -p "Has this been tested in maia-dev? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${RED}Please test in maia-dev first${NC}"
            exit 1
        fi
        
        read -p "Are you SURE you want to deploy to PRODUCTION? (yes/no) " -r
        if [[ ! $REPLY == "yes" ]]; then
            echo -e "${YELLOW}Production deployment cancelled${NC}"
            exit 1
        fi
        
        echo -e "${YELLOW}Deploying to production...${NC}"
        
        # Deploy to production
        gcloud app deploy app.production.yaml \
            --version="prod-${TIMESTAMP}" \
            --quiet \
            --project=future-footing-414610
            
        echo -e "${GREEN}✓ Deployed to: https://future-footing-414610.uc.r.appspot.com${NC}"
        
        # Log the deployment
        echo "Production deployment completed at $(date)" >> deployment.log
        ;;
        
    *)
        echo -e "${RED}Error: Invalid environment '$ENVIRONMENT'${NC}"
        echo "Valid environments: rmb-dev, maia-dev, production"
        exit 1
        ;;
esac

echo ""
echo "Deployment complete!"
echo "Remember the deployment flow: rmb-dev → maia-dev → production"