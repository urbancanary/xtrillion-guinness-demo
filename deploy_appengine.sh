#!/bin/bash

# 🚀 Google App Engine Deployment Script
# =====================================
# Much simpler than Cloud Run containers!

echo "🚀 Deploying Google Analysis 10 to App Engine..."
echo "📦 No Docker needed - just Python code!"
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

# Check if databases exist
echo "🔍 Checking database files..."
if [ -f "bonds_data.db" ]; then
    size=$(du -h bonds_data.db | cut -f1)
    echo "   ✅ bonds_data.db found ($size)"
else
    echo "   ❌ bonds_data.db missing"
    exit 1
fi

if [ -f "validated_quantlib_bonds.db" ]; then
    size=$(du -h validated_quantlib_bonds.db | cut -f1)
    echo "   ✅ validated_quantlib_bonds.db found ($size)"
else
    echo "   ❌ validated_quantlib_bonds.db missing"
    exit 1
fi

# Deploy to App Engine
echo ""
echo "🚀 Deploying to Google App Engine..."
echo "📤 This will upload your Python code + databases directly"
echo "⏱️  Estimated time: 2-3 minutes"
echo ""

gcloud app deploy app.yaml --quiet

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 DEPLOYMENT SUCCESSFUL!"
    echo ""
    
    # Get the App Engine URL
    APP_URL="https://${PROJECT_ID}.ue.r.appspot.com"
    echo "🌐 Your API is live at: $APP_URL"
    echo "🔍 Health check: $APP_URL/health"
    echo "📊 Bond analysis: $APP_URL/api/v1/bond/parse-and-calculate"
    echo ""
    
    # Test the deployment
    echo "🧪 Testing deployment..."
    if curl -s "$APP_URL/health" > /dev/null; then
        echo "✅ API is responding!"
        echo ""
        echo "🎯 Ready for bond analysis!"
        echo "💡 No containers, no Docker, no complexity!"
    else
        echo "⚠️  API may still be starting up..."
        echo "📝 Check logs: gcloud app logs tail -s default"
    fi
else
    echo "❌ Deployment failed"
    echo "📋 Check the error messages above"
    exit 1
fi
