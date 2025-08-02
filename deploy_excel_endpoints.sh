#!/bin/bash
# Quick deployment script to add Excel GET endpoints to your cloud API

echo "🚀 DEPLOYING EXCEL ONLINE ENDPOINTS..."
echo "📍 Target: https://future-footing-414610.uc.r.appspot.com"

# Step 1: Add the new endpoints to your existing API
echo "📝 Step 1: Adding GET endpoints to google_analysis10_api.py"
cd /Users/andyseaman/Notebooks/json_receiver_project/google_analysis10

# Backup existing API
cp google_analysis10_api.py google_analysis10_api.py.backup

# Add the new endpoints (you'll need to manually integrate these)
echo "✅ Excel GET endpoints code ready in: excel_get_endpoints.py"
echo "   📋 Manual step: Copy the route functions into google_analysis10_api.py"

# Step 2: Test locally first
echo "📝 Step 2: Testing locally"
echo "   Run: python3 google_analysis10_api.py"
echo "   Test: curl http://localhost:8080/excel/test"

# Step 3: Deploy to Google Cloud
echo "📝 Step 3: Deploy to Google Cloud"
echo "   Command: gcloud app deploy"

echo "🎯 Expected Excel Online URLs:"
echo "   Yield: https://future-footing-414610.uc.r.appspot.com/excel/yield?bond=T 3 15/08/52&price=71.66"
echo "   Duration: https://future-footing-414610.uc.r.appspot.com/excel/duration?bond=T 3 15/08/52&price=71.66"
echo "   Spread: https://future-footing-414610.uc.r.appspot.com/excel/spread?bond=ECOPETROL SA, 5.875%, 28-May-2045&price=69.31"

echo "✅ Ready for Excel Online WEBSERVICE functions!"
