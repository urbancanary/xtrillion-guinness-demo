#!/bin/bash
#
# Deploy with Treasury Update
# Updates yields before deployment
#

set -e  # Exit on error

echo "🚀 Deploy with Treasury Update"
echo "============================"
echo ""

# Step 1: Update Treasury yields
echo "Step 1: Updating Treasury yields..."
./manual_treasury_update.sh

if [ $? -ne 0 ]; then
    echo "❌ Treasury update failed. Aborting deployment."
    exit 1
fi

echo ""
echo "Step 2: Vacuuming database..."
sqlite3 bonds_data.db "PRAGMA wal_checkpoint(FULL); VACUUM;"
echo "✅ Database vacuumed"

echo ""
echo "Step 3: Committing changes..."

# Check if there are changes to commit
if git diff --quiet bonds_data.db; then
    echo "ℹ️  No yield changes detected"
else
    git add bonds_data.db
    git commit -m "🏦 Update Treasury yields for $(date +%Y-%m-%d)"
    echo "✅ Changes committed"
fi

echo ""
echo "Step 4: Deploying to App Engine..."
./deploy_appengine.sh

echo ""
echo "🎉 Deployment complete with updated Treasury yields!"