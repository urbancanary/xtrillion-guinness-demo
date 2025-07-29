#!/bin/bash

# 📊 GCS Database Architecture - Production Monitoring Script
# ===========================================================
# Monitors production deployment to ensure GCS database architecture
# is working properly and databases are being fetched successfully

echo "📊 MONITORING GCS DATABASE ARCHITECTURE IN PRODUCTION"
echo "====================================================="
echo ""

# Configuration
PROJECT_ID="future-footing-414610"
APP_URL="https://${PROJECT_ID}.uc.r.appspot.com"
HEALTH_ENDPOINT="${APP_URL}/health"
BOND_ENDPOINT="${APP_URL}/api/v1/bond/analysis"

# Function to check API health
check_api_health() {
    echo "🔍 Checking API health endpoint..."
    
    # Test health endpoint
    HTTP_STATUS=$(curl -s -o /tmp/health_response.json -w "%{http_code}" "$HEALTH_ENDPOINT")
    
    if [ "$HTTP_STATUS" = "200" ]; then
        echo "✅ API is responding (HTTP $HTTP_STATUS)"
        
        # Check health response content
        if [ -f "/tmp/health_response.json" ]; then
            echo "📋 Health response preview:"
            head -3 /tmp/health_response.json
        fi
        
    elif [ "$HTTP_STATUS" = "503" ]; then
        echo "⚠️  API starting up (HTTP $HTTP_STATUS) - databases may be downloading"
        echo "   This is normal during first startup after deployment"
    else
        echo "❌ API error (HTTP $HTTP_STATUS)"
        return 1
    fi
    echo ""
}

# Function to test bond analysis endpoint
test_bond_analysis() {
    echo "🧪 Testing bond analysis endpoint..."
    
    # Simple test payload
    TEST_PAYLOAD='{
        "description": "T 3 15/08/52",
        "price": 71.66
    }'
    
    # Test bond analysis endpoint
    HTTP_STATUS=$(curl -s -o /tmp/bond_response.json -w "%{http_code}" \
        -X POST \
        -H "Content-Type: application/json" \
        -H "X-API-Key: gax10_demo_3j5h8m9k2p6r4t7w1q" \
        -d "$TEST_PAYLOAD" \
        "$BOND_ENDPOINT")
    
    if [ "$HTTP_STATUS" = "200" ]; then
        echo "✅ Bond analysis endpoint responding (HTTP $HTTP_STATUS)"
        
        # Check if response contains expected fields
        if [ -f "/tmp/bond_response.json" ]; then
            if grep -q "ytm\|duration\|analytics" /tmp/bond_response.json; then
                echo "✅ Bond analysis response contains expected analytics"
            else
                echo "⚠️  Bond analysis response may be incomplete"
            fi
            
            # Show key results
            echo "📊 Key bond analysis results:"
            if command -v jq &> /dev/null; then
                echo "   YTM: $(jq -r '.analytics.ytm // "N/A"' /tmp/bond_response.json 2>/dev/null)%"
                echo "   Duration: $(jq -r '.analytics.duration // "N/A"' /tmp/bond_response.json 2>/dev/null) years"
            else
                grep -o '"ytm":[^,]*' /tmp/bond_response.json | head -1
                grep -o '"duration":[^,]*' /tmp/bond_response.json | head -1
            fi
        fi
        
    elif [ "$HTTP_STATUS" = "503" ]; then
        echo "⚠️  Bond analysis not ready (HTTP $HTTP_STATUS) - databases may still be downloading"
        echo "   Try again in 30-60 seconds"
    else
        echo "❌ Bond analysis error (HTTP $HTTP_STATUS)"
        
        # Show error response if available
        if [ -f "/tmp/bond_response.json" ]; then
            echo "   Error response:"
            head -3 /tmp/bond_response.json
        fi
    fi
    echo ""
}

# Function to check App Engine logs for database activity
check_database_logs() {
    echo "📋 Checking App Engine logs for database activity..."
    
    if ! command -v gcloud &> /dev/null; then
        echo "⚠️  gcloud CLI not available - skipping log check"
        echo ""
        return
    fi
    
    # Set project
    gcloud config set project "$PROJECT_ID" >/dev/null 2>&1
    
    echo "   Checking recent logs for database-related messages..."
    
    # Look for GCS database activity in recent logs
    DB_LOG_ENTRIES=$(gcloud app logs read --service=default --limit=20 --format="value(textPayload)" 2>/dev/null | grep -i "database\|gcs\|fetch\|download\|bonds_data\|ensuring.*available" | head -5)
    
    if [ ! -z "$DB_LOG_ENTRIES" ]; then
        echo "✅ Database activity found in logs:"
        echo "$DB_LOG_ENTRIES" | while read line; do
            if [ ! -z "$line" ]; then
                echo "   📋 $line"
            fi
        done
    else
        echo "⚠️  No recent database activity in logs"
        echo "   This could mean:"
        echo "   - Databases were already cached"
        echo "   - App hasn't restarted recently"
    fi
    echo ""
}

# Function to run performance check
performance_check() {
    echo "⚡ Running performance check..."
    
    # Time the health check
    START_TIME=$(date +%s.%N)
    curl -s "$HEALTH_ENDPOINT" > /dev/null
    END_TIME=$(date +%s.%N)
    
    if command -v bc &> /dev/null; then
        RESPONSE_TIME=$(echo "$END_TIME - $START_TIME" | bc -l)
        RESPONSE_MS=$(echo "$RESPONSE_TIME * 1000" | bc -l | cut -d. -f1)
        
        if [ "$RESPONSE_MS" -lt 1000 ]; then
            echo "✅ Fast response time: ${RESPONSE_MS}ms"
        elif [ "$RESPONSE_MS" -lt 3000 ]; then
            echo "⚠️  Moderate response time: ${RESPONSE_MS}ms"
        else
            echo "❌ Slow response time: ${RESPONSE_MS}ms"
        fi
    else
        echo "⚠️  Could not measure response time (bc not available)"
    fi
    echo ""
}

# Main monitoring function
main() {
    echo "🌐 Production URL: $APP_URL"
    echo "🎯 Project: $PROJECT_ID"
    echo ""
    
    check_api_health
    test_bond_analysis
    check_database_logs
    performance_check
    
    echo "🎯 MONITORING SUMMARY"
    echo "===================="
    echo ""
    echo "📊 Production API: $APP_URL"
    echo "🔍 Health check: $HEALTH_ENDPOINT"
    echo "📋 View logs: gcloud app logs tail -s default"
    echo "🏗️  Manage versions: gcloud app versions list"
    echo ""
    echo "🚀 GCS Database Architecture Benefits:"
    echo "   ⚡ Fast code-only deployments (30-60 seconds)"
    echo "   💾 Automatic database fetching from GCS"
    echo "   🔄 Independent database updates"
    echo "   💰 Reduced bandwidth and storage costs"
    echo ""
    
    # Cleanup temp files
    rm -f /tmp/health_response.json /tmp/bond_response.json
}

# Run monitoring
main "$@"