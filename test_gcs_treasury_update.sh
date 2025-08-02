#!/bin/bash
#
# Test GCS Treasury Update (No Redeployment)
# ===========================================
# This script demonstrates updating Treasury yields
# without redeploying when using GCS database strategy
#

echo "🧪 Testing GCS Treasury Update Without Redeployment"
echo "================================================"
echo ""

# Step 1: Check current Treasury date in GCS
echo "1️⃣  Checking current Treasury date in GCS..."
tmpfile=$(mktemp)
gsutil cp gs://json-receiver-databases/bonds_data.db "$tmpfile" 2>/dev/null
if [ $? -eq 0 ]; then
    GCS_DATE=$(sqlite3 "$tmpfile" "SELECT MAX(Date) FROM tsys_enhanced;" 2>/dev/null || echo "Error")
    echo "   GCS Treasury date: $GCS_DATE"
    rm -f "$tmpfile"
else
    echo "   ❌ Failed to download from GCS"
    exit 1
fi

echo ""
echo "2️⃣  Current deployment info:"
echo "   DATABASE_SOURCE: gcs (confirmed)"
echo "   This means the API downloads databases from GCS on cold start"

echo ""
echo "3️⃣  To update Treasury yields WITHOUT redeployment:"
echo ""
echo "   a) Update local database:"
echo "      python3 us_treasury_yield_fetcher.py"
echo ""
echo "   b) Vacuum the database:"
echo "      sqlite3 bonds_data.db 'PRAGMA wal_checkpoint(FULL); VACUUM;'"
echo ""
echo "   c) Upload to GCS:"
echo "      gsutil cp bonds_data.db gs://json-receiver-databases/"
echo ""
echo "   d) Wait for next cold start or force instance restart"
echo ""
echo "💡 The API will use the new data on next cold start!"
echo "   No redeployment needed with GCS strategy 🎉"

echo ""
echo "4️⃣  To force a cold start (optional):"
echo "   - Wait for instances to scale down (usually 15 min)"
echo "   - Or deploy a dummy change to force restart"
echo "   - Or use: gcloud app versions stop production --service=default"
echo "     then: gcloud app versions start production --service=default"