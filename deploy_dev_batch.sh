#!/bin/bash

# XTrillion Core - Development Deployment with Batch Processing
# Deploys DEV version to development-dot-future-footing-414610.uc.r.appspot.com

set -e

echo "🚀 XTrillion Core - DEV Deployment with Batch Processing"
echo "=================================================="

# Check if we're in the correct directory
if [ ! -f "google_analysis10_api_dev.py" ]; then
    echo "❌ Error: Must run from google_analysis10 directory"
    echo "   Expected to find google_analysis10_api_dev.py"
    exit 1
fi

if [ ! -f "app.dev.yaml" ]; then
    echo "❌ Error: app.dev.yaml not found"
    echo "   Run this script from the google_analysis10 directory"
    exit 1
fi

# Backup current production API
echo "📦 Creating backup of current production API..."
cp google_analysis10_api.py google_analysis10_api.py.backup_$(date +%Y%m%d_%H%M%S)

# Temporarily replace main API with DEV version for deployment
echo "🔄 Temporarily switching to DEV API for deployment..."
cp google_analysis10_api.py google_analysis10_api_production_backup.py
cp google_analysis10_api_dev.py google_analysis10_api.py

# Verify deployment configuration
echo "🔍 Verifying deployment configuration..."
echo "   Service: development"
echo "   Environment: development"
echo "   Batch processing: enabled"
echo "   Max instances: 2"

# Deploy to development service
echo "🚀 Deploying to development environment..."
echo "   Target: development-dot-future-footing-414610.uc.r.appspot.com"

gcloud app deploy app.dev.yaml --quiet --project=future-footing-414610

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    echo ""
    echo "🌐 Development API available at:"
    echo "   https://development-dot-future-footing-414610.uc.r.appspot.com"
    echo ""
    echo "🆕 NEW Batch Processing Endpoint:"
    echo "   POST https://development-dot-future-footing-414610.uc.r.appspot.com/api/v1/bonds/batch"
    echo ""
    echo "📊 Health Check:"
    echo "   GET https://development-dot-future-footing-414610.uc.r.appspot.com/health"
    echo ""
    echo "🧪 Test with curl:"
    echo '   curl -X POST "https://development-dot-future-footing-414610.uc.r.appspot.com/api/v1/bonds/batch" \'
    echo '     -H "Content-Type: application/json" \'
    echo '     -H "X-API-Key: gax10_dev_4n8s6k2x7p9v5m8p1z" \'
    echo '     -d '"'"'{'
    echo '       "bonds": ['
    echo '         ["T 3 15/08/52", 71.66, "2025-08-01"],'
    echo '         ["PANAMA, 3.87%, 23-Jul-2060", 56.60, "2025-08-01"]'
    echo '       ]'
    echo '     }'"'"
else
    echo "❌ Deployment failed!"
    echo "Restoring production API..."
    cp google_analysis10_api_production_backup.py google_analysis10_api.py
    exit 1
fi

# Restore production API
echo "🔄 Restoring production API..."
cp google_analysis10_api_production_backup.py google_analysis10_api.py
rm google_analysis10_api_production_backup.py

echo ""
echo "✅ Development deployment complete!"
echo "📝 Next steps:"
echo "   1. Test the health endpoint"
echo "   2. Test the new batch processing endpoint"
echo "   3. Validate backwards compatibility"
echo "   4. Create JavaScript batch functions for Excel integration"
echo ""
echo "🔗 Quick Health Check:"
echo "   curl 'https://development-dot-future-footing-414610.uc.r.appspot.com/health'"
