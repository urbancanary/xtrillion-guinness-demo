#!/bin/bash

# 🚀 Quick Multi-Region Cloud Run Deployment
# ==========================================
# Deploys to 3 regions for geographic performance testing

set -e

PROJECT_ID="future-footing-414610"
SERVICE_NAME="bond-analytics"

echo "🌍 Quick Multi-Region Deployment for Performance Testing"
echo "========================================================"

# Check if logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1 > /dev/null; then
    echo "❌ Please login to gcloud first: gcloud auth login"
    exit 1
fi

# Set project
gcloud config set project $PROJECT_ID

# Enable APIs
echo "🔧 Enabling APIs..."
gcloud services enable cloudbuild.googleapis.com run.googleapis.com --quiet

# Create simple Dockerfile
echo "📦 Creating Dockerfile..."
cat > Dockerfile.cloudrun << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y gcc g++ curl && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

ENV PORT=8080
ENV PYTHONPATH=/app
ENV DATABASE_SOURCE=gcs

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "2", "--timeout", "0", "google_analysis10_api:app"]
EOF

# Deploy to regions
declare -a regions=("us-central1" "europe-west1" "asia-northeast1")
declare -a region_names=("US-Central" "Europe-West" "Asia-Northeast")

echo ""
echo "🚀 Deploying to all regions..."

for i in "${!regions[@]}"; do
    region="${regions[$i]}"
    name="${region_names[$i]}"
    service="${SERVICE_NAME}-${region}"
    
    echo ""
    echo "📍 Deploying to $name ($region)..."
    
    # Deploy with minimal configuration for speed
    gcloud run deploy $service \
        --source . \
        --region $region \
        --allow-unauthenticated \
        --memory 2Gi \
        --cpu 1 \
        --max-instances 2 \
        --timeout 60s \
        --quiet || echo "⚠️  $name deployment had issues but continuing..."
    
    # Get URL
    URL=$(gcloud run services describe $service --region $region --format='value(status.url)' 2>/dev/null || echo "URL unavailable")
    echo "🔗 $name: $URL"
    
    # Quick test (don't block on failures)
    if [[ "$URL" != "URL unavailable" ]]; then
        echo "🧪 Testing $name..."
        if timeout 10s curl -s "$URL/health" > /dev/null 2>&1; then
            echo "✅ $name is responding"
        else
            echo "⏳ $name may still be starting up"
        fi
    fi
done

echo ""
echo "🎉 Multi-region deployment initiated!"
echo ""
echo "📊 Service URLs:"
for i in "${!regions[@]}"; do
    region="${regions[$i]}"
    service="${SERVICE_NAME}-${region}"
    URL=$(gcloud run services describe $service --region $region --format='value(status.url)' 2>/dev/null || echo "Check console")
    echo "   ${region_names[$i]}: $URL"
done

echo ""
echo "⏱️  Wait 2-3 minutes for cold start, then test with:"
echo "python3 timing_test_production.py"

# Clean up
rm -f Dockerfile.cloudrun

echo ""
echo "🎯 Ready for geographic performance testing!"