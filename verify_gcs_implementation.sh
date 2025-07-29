#!/bin/bash

# 🔍 GCS Database Architecture - Deployment Verification Script
# =============================================================
# Verifies that GCS database architecture is properly implemented
# and prevents reversion to database upload approach

echo "🔍 VERIFYING GCS DATABASE ARCHITECTURE IMPLEMENTATION"
echo "===================================================="
echo ""

# Set colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track verification status
VERIFICATION_PASSED=true

# Function to check if we're in the right directory
check_directory() {
    echo "📂 Checking project directory..."
    if [ ! -f "google_analysis10_api.py" ]; then
        echo -e "${RED}❌ ERROR: Not in google_analysis10 directory${NC}"
        echo "📂 Please run from: /Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/"
        exit 1
    fi
    echo -e "${GREEN}✅ Correct directory confirmed${NC}"
    echo ""
}

# Function to verify essential files exist
verify_essential_files() {
    echo "📋 Verifying essential GCS architecture files..."
    
    ESSENTIAL_FILES=(
        "gcs_database_manager.py"
        ".gcloudignore"
        "deploy_appengine.sh"
        "requirements.txt"
        "app.yaml"
    )
    
    for file in "${ESSENTIAL_FILES[@]}"; do
        if [ -f "$file" ]; then
            echo -e "   ${GREEN}✅ $file${NC}"
        else
            echo -e "   ${RED}❌ $file MISSING${NC}"
            VERIFICATION_PASSED=false
        fi
    done
    echo ""
}

# Function to verify .gcloudignore excludes databases  
verify_gcloudignore() {
    echo "🚫 Verifying .gcloudignore excludes databases..."
    
    if [ ! -f ".gcloudignore" ]; then
        echo -e "${RED}❌ .gcloudignore missing${NC}"
        VERIFICATION_PASSED=false
        return
    fi
    
    # Check for database exclusions
    if grep -q "*.db" .gcloudignore && grep -q "bonds_data.db" .gcloudignore; then
        echo -e "${GREEN}✅ Database files properly excluded${NC}"
    else
        echo -e "${RED}❌ Database files NOT excluded - will cause uploads!${NC}"
        VERIFICATION_PASSED=false
    fi
    echo ""
}

# Function to verify API includes GCS manager
verify_api_integration() {
    echo "🔧 Verifying API includes GCS database manager..."
    
    if grep -q "from gcs_database_manager import ensure_databases_available" google_analysis10_api.py; then
        echo -e "${GREEN}✅ GCS manager imported${NC}"
    else
        echo -e "${RED}❌ GCS manager import MISSING${NC}"
        VERIFICATION_PASSED=false
    fi
    
    if grep -q "ensure_databases_available()" google_analysis10_api.py; then
        echo -e "${GREEN}✅ Database fetching called on startup${NC}"
    else
        echo -e "${RED}❌ Database fetching call MISSING${NC}"
        VERIFICATION_PASSED=false
    fi
    echo ""
}

# Function to verify requirements.txt includes GCS dependencies
verify_requirements() {
    echo "📦 Verifying requirements.txt includes GCS dependencies..."
    
    if grep -q "google-cloud-storage" requirements.txt; then
        echo -e "${GREEN}✅ google-cloud-storage dependency included${NC}"
    else
        echo -e "${RED}❌ google-cloud-storage dependency MISSING${NC}"
        VERIFICATION_PASSED=false
    fi
    echo ""
}

# Function to verify deployment script is GCS-optimized
verify_deployment_script() {
    echo "🚀 Verifying deployment script uses GCS architecture..."
    
    if [ ! -f "deploy_appengine.sh" ]; then
        echo -e "${RED}❌ deploy_appengine.sh missing${NC}"
        VERIFICATION_PASSED=false
        return
    fi
    
    if grep -q "Code-only deployment" deploy_appengine.sh; then
        echo -e "${GREEN}✅ Deployment script uses code-only approach${NC}"
    else
        echo -e "${RED}❌ Deployment script may still check for local databases${NC}"
        VERIFICATION_PASSED=false
    fi
    
    if [ -x "deploy_appengine.sh" ]; then
        echo -e "${GREEN}✅ Deployment script is executable${NC}"
    else
        echo -e "${YELLOW}⚠️  Making deployment script executable...${NC}"
        chmod +x deploy_appengine.sh
    fi
    echo ""
}

# Function to verify GCS bucket contains databases
verify_gcs_databases() {
    echo "☁️  Verifying databases exist in GCS bucket..."
    
    # Check if gcloud is available
    if ! command -v gsutil &> /dev/null; then
        echo -e "${YELLOW}⚠️  gsutil not available - skipping GCS verification${NC}"
        echo ""
        return
    fi
    
    # Set project (from deployment script)
    gcloud config set project future-footing-414610 >/dev/null 2>&1
    
    # Check for databases in GCS
    REQUIRED_DBS=("bonds_data.db" "validated_quantlib_bonds.db")
    
    for db in "${REQUIRED_DBS[@]}"; do
        if gsutil ls "gs://json-receiver-databases/$db" >/dev/null 2>&1; then
            echo -e "   ${GREEN}✅ $db found in GCS${NC}"
        else
            echo -e "   ${RED}❌ $db MISSING from GCS${NC}"
            VERIFICATION_PASSED=false
        fi
    done
    echo ""
}

# Function to check for forbidden database files locally
check_local_databases() {
    echo "🚫 Checking for local database files (should not be committed)..."
    
    DB_FILES=("bonds_data.db" "validated_quantlib_bonds.db" "bloomberg_index.db")
    LOCAL_DBS_FOUND=false
    
    for db in "${DB_FILES[@]}"; do
        if [ -f "$db" ]; then
            echo -e "   ${YELLOW}⚠️  $db found locally (OK if needed for development)${NC}"
            LOCAL_DBS_FOUND=true
        fi
    done
    
    if [ "$LOCAL_DBS_FOUND" = false ]; then
        echo -e "${GREEN}✅ No local database files (clean deployment)${NC}"
    fi
    echo ""
}

# Function to test GCS database manager
test_gcs_manager() {
    echo "🧪 Testing GCS database manager functionality..."
    
    if ! python3 -c "import gcs_database_manager" 2>/dev/null; then
        echo -e "${RED}❌ Cannot import gcs_database_manager${NC}"
        VERIFICATION_PASSED=false
        return
    fi
    
    echo -e "${GREEN}✅ GCS database manager imports successfully${NC}"
    
    # Test the module (but don't force download to avoid auth issues)
    echo "   Running basic functionality test..."
    if python3 -c "
from gcs_database_manager import GCSDatabaseManager
manager = GCSDatabaseManager()
status = manager.check_local_databases()
print(f'Local database check completed: {len(status)} databases checked')
" 2>/dev/null; then
        echo -e "${GREEN}✅ GCS manager basic functionality working${NC}"
    else
        echo -e "${RED}❌ GCS manager basic functionality failed${NC}"
        VERIFICATION_PASSED=false
    fi
    echo ""
}

# Function to check for anti-reversion measures
check_anti_reversion() {
    echo "🔒 Verifying anti-reversion measures..."
    
    # Check for specific bad patterns that indicate database uploading (not just mentioning databases)
    if grep -q "if.*-f.*bonds_data.db\|upload.*bonds_data.db\|deploy.*bonds_data.db" deploy_appengine.sh; then
        echo -e "${RED}❌ Deployment script contains database upload logic${NC}"
        VERIFICATION_PASSED=false
    else
        echo -e "${GREEN}✅ No database upload logic in deployment script${NC}"
    fi
    
    # Check that GCS fetching is mandatory in API
    if grep -A5 -B5 "ensure_databases_available" google_analysis10_api.py | grep -q "if.*ensure_databases_available"; then
        echo -e "${GREEN}✅ Database fetching is checked and logged${NC}"
    else
        echo -e "${YELLOW}⚠️  Database fetching result not checked${NC}"
    fi
    echo ""
}

# Main verification flow
main() {
    check_directory
    verify_essential_files
    verify_gcloudignore
    verify_api_integration
    verify_requirements
    verify_deployment_script
    verify_gcs_databases
    check_local_databases
    test_gcs_manager
    check_anti_reversion
    
    # Final verification result
    echo "🎯 VERIFICATION RESULTS"
    echo "====================="
    
    if [ "$VERIFICATION_PASSED" = true ]; then
        echo -e "${GREEN}🎉 ALL VERIFICATIONS PASSED!${NC}"
        echo -e "${GREEN}✅ GCS Database Architecture is properly implemented${NC}"
        echo -e "${GREEN}✅ Ready for fast, code-only deployments${NC}"
        echo ""
        echo -e "${BLUE}🚀 To deploy:${NC}"
        echo "   ./deploy_appengine.sh"
        echo ""
        echo -e "${BLUE}🔍 To monitor deployment:${NC}"
        echo "   gcloud app logs tail -s default"
        echo ""
        exit 0
    else
        echo -e "${RED}❌ VERIFICATION FAILED${NC}"
        echo -e "${RED}⚠️  GCS Database Architecture has issues${NC}"
        echo ""
        echo -e "${YELLOW}🔧 Fix the issues above before deploying${NC}"
        echo ""
        exit 1
    fi
}

# Run main function
main "$@"