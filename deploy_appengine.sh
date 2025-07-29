#!/bin/bash

# 🚀 Google App Engine Deployment Script - GCS Database Architecture
# ====================================================================
# Deploys code-only to App Engine. Databases fetched from GCS on startup.
# Much faster deployments - no more 166MB database uploads!

echo "🚀 Deploying Google Analysis 10 to App Engine..."
echo "💻 Code-only deployment - databases fetched from GCS!"
echo "⚡ No more 166MB database uploads!"
echo ""

# Check if we're in the right directory
if [ ! -f "google_analysis10_api.py" ]; then
    echo "❌ ERROR: google_analysis10_api.py not found"
    echo "📂 Please run this script from the google_analysis10 directory"
    exit 1
fi

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo "❌ ERROR: gcloud CLI not found"
    echo "📥 Please install Google Cloud SDK"
    exit 1
fi

# Set project
PROJECT_ID="future-footing-414610"
echo "🎯 Setting project: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Enable App Engine API
echo "🔧 Enabling App Engine API..."
gcloud services enable appengine.googleapis.com

# Check GCS database availability (don't block deployment if unavailable)
echo "🔍 Checking GCS database availability..."
if gsutil ls gs://json-receiver-databases/bonds_data.db > /dev/null 2>&1; then
    echo "   ✅ bonds_data.db found in GCS"
else
    echo "   ⚠️  bonds_data.db not found in GCS - app will need access"
fi

if gsutil ls gs://json-receiver-databases/validated_quantlib_bonds.db > /dev/null 2>&1; then
    echo "   ✅ validated_quantlib_bonds.db found in GCS"
else
    echo "   ⚠️  validated_quantlib_bonds.db not found in GCS - app will need access"
fi

# Check essential files exist
echo "🔍 Checking essential code files..."
ESSENTIAL_FILES=(
    "google_analysis10_api.py"
    "google_analysis10.py"
    "bond_master_hierarchy_enhanced.py"
    "gcs_database_manager.py"
    "app.yaml"
    "requirements.txt"
)

for file in "${ESSENTIAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file found"
    else
        echo "   ❌ $file missing - deployment may fail"
    fi
done

# Deploy to App Engine - GCS ARCHITECTURE
echo ""
echo "🚀 Deploying to Google App Engine..."
echo "💻 Uploading Python code only (databases fetched from GCS)"
echo "💡 Using 'production' version - will replace existing code"
echo "⏱️  Estimated time: 30-60 seconds (much faster without databases!)"
echo ""

# Deploy with version management and auto-cleanup
gcloud app deploy app.yaml --version=production --promote --quiet

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 DEPLOYMENT SUCCESSFUL!"
    echo ""
    
    # Clean up old versions automatically
    echo "🧹 Cleaning up old versions..."
    
    # Get list of old versions (exclude current 'production' version)
    OLD_VERSIONS=$(gcloud app versions list --service=default --format="value(version.id)" --filter="version.id != production AND traffic_split = 0")
    
    if [ ! -z "$OLD_VERSIONS" ]; then
        echo "🗑️  Deleting unused versions: $OLD_VERSIONS"
        echo $OLD_VERSIONS | xargs gcloud app versions delete --service=default --quiet
        echo "✅ Cleanup complete!"
    else
        echo "✅ No old versions to clean up"
    fi
    
    # Get the App Engine URL
    APP_URL="https://${PROJECT_ID}.ue.r.appspot.com"
    echo ""
    echo "🌐 Your API is live at: $APP_URL"
    echo "🔍 Health check: $APP_URL/health"
    echo "📊 Bond analysis: $APP_URL/api/v1/bond/analysis"
    echo "📈 Portfolio analysis: $APP_URL/api/v1/portfolio/analysis"
    echo ""
    
    # Test the deployment
    echo "🧪 Testing deployment..."
    if curl -s "$APP_URL/health" > /dev/null; then
        echo "✅ API is responding!"
        echo ""
        echo "🎯 Ready for bond analysis!"
        echo "🚀 GCS Database Architecture: Fast deployments + automatic database updates!"
        echo "💡 Database updates can now happen independently of code deployments!"
    else
        echo "⚠️  API may still be starting up (databases downloading from GCS)..."
        echo "📝 Check logs: gcloud app logs tail -s default"
        echo "🕐 Database download typically takes 30-60 seconds on first startup"
    fi
else
    echo "❌ Deployment failed"
    echo "📋 Check the error messages above"
    exit 1
fi

echo ""
echo "📊 Current versions:"
gcloud app versions list --service=default
