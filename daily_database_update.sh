#!/bin/bash
# XTrillion GA10 - Daily Database Update Job (Scheduled for 1am)
# Updates databases in Cloud Storage for production API instances

set -e

echo "🕐 XTrillion GA10 - Daily Database Update (1am job)"
echo "=================================================="
echo "📅 $(date)"
echo ""

# Configuration
BUCKET_NAME="xtrillion-ga10-databases"
BACKUP_BUCKET="xtrillion-ga10-db-backups"
LOCAL_BACKUP_DIR="./db_backups_$(date +%Y%m%d)"

echo "🔧 Configuration:"
echo "   📦 Production bucket: ${BUCKET_NAME}"
echo "   💾 Backup bucket: ${BACKUP_BUCKET}"
echo "   📁 Local backup: ${LOCAL_BACKUP_DIR}"
echo ""

# Create backup directory
mkdir -p "${LOCAL_BACKUP_DIR}"

# Step 1: Backup current production databases
echo "💾 Step 1: Backing up current production databases..."
gsutil -m cp gs://${BUCKET_NAME}/*.db "${LOCAL_BACKUP_DIR}/" || echo "⚠️  No existing databases to backup"

# Upload backups to backup bucket with timestamp
if [ -n "$(ls -A ${LOCAL_BACKUP_DIR} 2>/dev/null)" ]; then
    echo "📤 Uploading backups to backup bucket..."
    gsutil -m cp "${LOCAL_BACKUP_DIR}/*.db" "gs://${BACKUP_BUCKET}/$(date +%Y%m%d_%H%M%S)/"
    echo "✅ Backup complete"
else
    echo "⚠️  No databases to backup"
fi
echo ""

# Step 2: Generate/update databases locally
echo "🔄 Step 2: Updating bond databases..."

# Check if we have database generation scripts
if [ -f "update_bonds_data.py" ]; then
    echo "📊 Running bond data update script..."
    python3 update_bonds_data.py
elif [ -f "download_latest_bond_data.py" ]; then
    echo "📥 Running bond data download script..."
    python3 download_latest_bond_data.py
else
    echo "⚠️  No database update script found. Using existing databases."
    echo "💡 Expected scripts: update_bonds_data.py or download_latest_bond_data.py"
fi

# Verify databases exist and get sizes
echo ""
echo "🔍 Step 3: Verifying updated databases..."
for db in bonds_data.db validated_quantlib_bonds.db bloomberg_index.db; do
    if [ -f "$db" ]; then
        size=$(du -h "$db" | cut -f1)
        echo "✅ $db: $size"
    else
        echo "⚠️  $db: Missing (will use previous version)"
    fi
done
echo ""

# Step 4: Upload updated databases to production bucket
echo "📤 Step 4: Uploading updated databases to production..."
upload_count=0
for db in bonds_data.db validated_quantlib_bonds.db bloomberg_index.db; do
    if [ -f "$db" ]; then
        echo "📤 Uploading $db..."
        gsutil cp "$db" "gs://${BUCKET_NAME}/"
        upload_count=$((upload_count + 1))
    fi
done

echo ""
echo "✅ Database update complete!"
echo "📊 Uploaded $upload_count database files"
echo "🕐 Completed at: $(date)"
echo ""

# Step 5: Optional - Trigger App Engine instances to refresh
echo "🔄 Step 5: App Engine instance refresh..."
echo "💡 Warm instances will pick up new databases on next restart"
echo "💡 Or trigger refresh via: gcloud app versions list"
echo ""

# Cleanup
rm -rf "${LOCAL_BACKUP_DIR}"

echo "🎯 Daily database update job complete!"
echo "📈 Production API instances will use updated databases"
echo "⏰ Next update: Tomorrow at 1am"