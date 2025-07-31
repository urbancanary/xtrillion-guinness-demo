#!/bin/bash

# 🌍 Multi-Region Deployment Script for Geographic Performance Testing
# ====================================================================
# Deploys the bond analytics API to multiple Google Cloud regions
# for comprehensive geographic performance analysis.

set -e  # Exit on any error

echo "🌍 Multi-Region Bond Analytics API Deployment"
echo "=============================================="
echo ""

# Configuration
PROJECT_ID="future-footing-414610"
API_NAME="bond-analytics"

# Regional configurations
declare -A REGIONS=(
    ["us"]="us-central1"
    ["europe"]="europe-west1" 
    ["asia"]="asia-northeast1"
)

declare -A REGION_NAMES=(
    ["us"]="US Central"
    ["europe"]="Europe West"
    ["asia"]="Asia Northeast"
)

# Check prerequisites
echo "🔍 Checking prerequisites..."
if ! command -v gcloud &> /dev/null; then
    echo "❌ ERROR: gcloud CLI not found"
    echo "📥 Please install Google Cloud SDK"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ ERROR: Docker not found"
    echo "📥 Please install Docker"
    exit 1
fi

# Set project
echo "🎯 Setting project: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable storage.googleapis.com

# Function to deploy to a specific region
deploy_to_region() {
    local region_key=$1
    local region=${REGIONS[$region_key]}
    local region_name=${REGION_NAMES[$region_key]}
    local service_name="${API_NAME}-${region_key}"
    
    echo ""
    echo "🚀 Deploying to ${region_name} (${region})"
    echo "================================================"
    
    # Create Dockerfile for Cloud Run
    cat > Dockerfile.${region_key} << EOF
# Multi-region Bond Analytics API - ${region_name}
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PORT=8080
ENV ENVIRONMENT=production-${region_key}
ENV DATABASE_SOURCE=gcs
ENV PYTHONPATH=/app
ENV REGION=${region}

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \\
    CMD curl -f http://localhost:8080/health || exit 1

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "2", "--timeout", "0", "google_analysis10_api:app"]
EOF

    # Build and deploy to Cloud Run
    echo "🏗️  Building container for ${region_name}..."
    gcloud builds submit --tag gcr.io/${PROJECT_ID}/${service_name} --file=Dockerfile.${region_key} .
    
    echo "☁️  Deploying to Cloud Run in ${region_name}..."
    gcloud run deploy ${service_name} \\
        --image gcr.io/${PROJECT_ID}/${service_name} \\
        --region ${region} \\
        --platform managed \\
        --allow-unauthenticated \\
        --memory 2Gi \\
        --cpu 1 \\
        --timeout 300 \\
        --concurrency 10 \\
        --min-instances 0 \\
        --max-instances 3 \\
        --set-env-vars="ENVIRONMENT=production-${region_key},DATABASE_SOURCE=gcs,REGION=${region}" \\
        --quiet
    
    # Get the service URL
    SERVICE_URL=\$(gcloud run services describe ${service_name} --region ${region} --format='value(status.url)')
    
    echo "✅ ${region_name} deployment complete!"
    echo "🔗 URL: \$SERVICE_URL"
    
    # Test the deployment
    echo "🧪 Testing ${region_name} deployment..."
    if curl -s "\$SERVICE_URL/health" > /dev/null; then
        echo "✅ ${region_name} API is responding!"
    else
        echo "⚠️  ${region_name} API may still be starting up..."
    fi
    
    # Store URL for testing
    echo "\$SERVICE_URL" > "url_${region_key}.txt"
    
    # Clean up region-specific Dockerfile
    rm -f Dockerfile.${region_key}
}

# Main deployment sequence
echo ""
echo "📋 Deployment Plan:"
echo "=================="
for region_key in "\${!REGIONS[@]}"; do
    echo "   - ${REGION_NAMES[$region_key]} (${REGIONS[$region_key]})"
done
echo ""

read -p "🚀 Proceed with multi-region deployment? [y/N] " -n 1 -r
echo
if [[ \$REPLY =~ ^[Yy]\$ ]]; then
    
    # Deploy to each region
    for region_key in "\${!REGIONS[@]}"; do
        deploy_to_region \$region_key
    done
    
    # Summary
    echo ""
    echo "🎉 MULTI-REGION DEPLOYMENT COMPLETE!"
    echo "===================================="
    echo ""
    echo "📊 Regional Endpoints:"
    for region_key in "\${!REGIONS[@]}"; do
        if [ -f "url_${region_key}.txt" ]; then
            url=\$(cat "url_${region_key}.txt")
            echo "   ${REGION_NAMES[$region_key]:.<20} \$url"
        fi
    done
    
    echo ""
    echo "🧪 Next Steps:"
    echo "1. Wait 2-3 minutes for all instances to warm up"
    echo "2. Run geographic performance tests:"
    echo "   python3 geographic_performance_test.py"
    echo "3. Use timing data for contract negotiations"
    
    # Create updated test configuration
    echo ""
    echo "📝 Updating test configuration with actual URLs..."
    
    # Update the geographic performance test with real URLs
    python3 -c "
import json

# Read URLs
urls = {}
regions = ['us', 'europe', 'asia']
region_names = {'us': 'US Central', 'europe': 'Europe West', 'asia': 'Asia Northeast'}

for region in regions:
    try:
        with open(f'url_{region}.txt', 'r') as f:
            urls[region] = f.read().strip()
    except FileNotFoundError:
        print(f'Warning: url_{region}.txt not found')

# Update configuration
config = {
    'Local Development': {
        'url': 'http://localhost:8080',
        'region': 'Local',
        'description': 'Development server (baseline)'
    }
}

for region, url in urls.items():
    config[f'{region_names[region]} Production'] = {
        'url': url,
        'region': region,
        'description': f'Cloud Run {region_names[region]}'
    }

print('Updated endpoint configuration:')
for name, info in config.items():
    print(f'  {name}: {info[\"url\"]}')

# Save to file for easy access
with open('multi_region_endpoints.json', 'w') as f:
    json.dump(config, f, indent=2)
"
    
    # Clean up temporary files
    rm -f url_*.txt
    
    echo ""
    echo "✅ Configuration saved to multi_region_endpoints.json"
    echo "🎯 Ready for geographic performance testing!"
    
else
    echo "❌ Deployment cancelled"
    exit 1
fi