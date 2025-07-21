#!/bin/bash
# XTrillion-GA10 Database Download Script
# Downloads all required databases from Google Cloud Storage

set -e

# Configuration
GCS_BUCKET="json-receiver-databases"
DATA_DIR="/app/data"
PROJECT_ID="future-footing-414610"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔽 XTrillion-GA10 Database Download${NC}"
echo "📦 Downloading databases from GCS..."
echo "🪣 Bucket: ${GCS_BUCKET}"
echo "📁 Target: ${DATA_DIR}"
echo ""

# Create data directory
mkdir -p ${DATA_DIR}

# Database files to download
DATABASES=(
    "bonds_data.db"
    "validated_quantlib_bonds.db" 
    "bloomberg_index.db"
    "bond_database.db"
)

# Download each database
for db in "${DATABASES[@]}"; do
    echo -e "${YELLOW}⬇️  Downloading ${db}...${NC}"
    
    # Try to download from GCS
    if gsutil -q cp "gs://${GCS_BUCKET}/databases/${db}" "${DATA_DIR}/" 2>/dev/null; then
        size=$(du -h "${DATA_DIR}/${db}" | cut -f1)
        echo -e "${GREEN}✅ Downloaded ${db} (${size})${NC}"
    else
        echo -e "${RED}❌ Failed to download ${db}${NC}"
        
        # Check if database exists locally as fallback
        if [ -f "/app/${db}" ]; then
            echo -e "${YELLOW}🔄 Using local fallback for ${db}${NC}"
            cp "/app/${db}" "${DATA_DIR}/"
            size=$(du -h "${DATA_DIR}/${db}" | cut -f1)
            echo -e "${GREEN}✅ Copied local ${db} (${size})${NC}"
        else
            echo -e "${RED}⚠️  ${db} not available locally or in GCS${NC}"
        fi
    fi
done

echo ""
echo -e "${BLUE}📊 Database Download Summary:${NC}"
for db in "${DATABASES[@]}"; do
    if [ -f "${DATA_DIR}/${db}" ]; then
        size=$(du -h "${DATA_DIR}/${db}" | cut -f1)
        echo -e "${GREEN}✅ ${db}: ${size}${NC}"
    else
        echo -e "${RED}❌ ${db}: Missing${NC}"
    fi
done

echo ""
echo -e "${GREEN}🎯 Database download complete!${NC}"
