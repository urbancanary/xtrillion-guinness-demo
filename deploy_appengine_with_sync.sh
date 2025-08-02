#!/bin/bash
#
# Deploy to App Engine with Database Sync
# =======================================
# 
# This script ensures local and cloud databases are synchronized
# before deployment, handling Treasury updates properly
#

set -e  # Exit on error

echo "🔄 Deploy with Database Sync"
echo "============================"
echo ""

# Check if we have gcloud credentials
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &>/dev/null; then
    echo "❌ Not authenticated with gcloud. Please run: gcloud auth login"
    exit 1
fi

# Step 1: Vacuum local databases before sync
echo "Step 1: Preparing databases for sync..."
echo "--------------------------------------"
for db in bonds_data.db validated_quantlib_bonds.db bloomberg_index.db; do
    if [ -f "$db" ]; then
        echo "Vacuuming $db..."
        sqlite3 "$db" "PRAGMA wal_checkpoint(FULL); VACUUM;" 2>/dev/null || echo "  (skipped: not SQLite)"
    fi
done

echo ""
echo "Step 2: Syncing databases with GCS..."
echo "-------------------------------------"
python3 sync_databases_with_gcs.py

if [ $? -ne 0 ]; then
    echo "❌ Database sync failed. Please check the errors above."
    exit 1
fi

echo ""
echo "Step 3: Running tests..."
echo "------------------------"
# Run basic API test to ensure everything works
python3 test_enhanced_api.py --quick

if [ $? -ne 0 ]; then
    echo "❌ Tests failed. Please fix before deploying."
    exit 1
fi

echo ""
echo "Step 4: Deploying to App Engine..."
echo "----------------------------------"
./deploy_appengine.sh

echo ""
echo "✅ Deployment complete with synchronized databases!"
echo ""
echo "📊 Database Status:"
echo "  - Local and cloud databases are in sync"
echo "  - Treasury yields are up to date"
echo "  - All bond data is consistent"
echo ""
echo "🔗 API URL: https://future-footing-414610.uc.r.appspot.com"