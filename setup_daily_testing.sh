#!/bin/bash

# Setup Daily Testing with Google Cloud Scheduler
# This script configures automated daily testing with email notifications

set -e

echo "🔧 Setting up Daily API Testing with Google Cloud..."
echo "=================================================="

# Configuration
PROJECT_ID="future-footing-414610"
REGION="us-central1"
SERVICE_ACCOUNT="api-tester@${PROJECT_ID}.iam.gserviceaccount.com"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if gcloud is configured
if ! gcloud config get-value project >/dev/null 2>&1; then
    echo -e "${RED}❌ Please configure gcloud first: gcloud init${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Current Configuration:${NC}"
echo "   Project: $PROJECT_ID"
echo "   Region: $REGION"
echo ""

# Step 1: Enable required APIs
echo -e "${GREEN}1. Enabling required Google Cloud APIs...${NC}"
gcloud services enable cloudscheduler.googleapis.com \
    cloudfunctions.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com \
    --project=$PROJECT_ID

# Step 2: Create Cloud Function for testing
echo -e "${GREEN}2. Creating Cloud Function for daily testing...${NC}"

# Create function directory
mkdir -p cloud_function_tester
cp daily_test_suite.py cloud_function_tester/main.py

# Create requirements.txt for Cloud Function
cat > cloud_function_tester/requirements.txt << EOF
requests==2.31.0
google-cloud-secret-manager==2.16.3
EOF

# Create Cloud Function wrapper
cat > cloud_function_tester/main.py << 'EOF'
import os
import json
from daily_test_suite import XTrillionAPITester
from google.cloud import secretmanager

def run_daily_tests(request):
    """HTTP Cloud Function to run daily tests"""
    
    # Get email credentials from Secret Manager
    client = secretmanager.SecretManagerServiceClient()
    project_id = os.environ.get('GCP_PROJECT')
    
    try:
        # Retrieve email credentials
        email_secret = client.access_secret_version(
            request={"name": f"projects/{project_id}/secrets/email-credentials/versions/latest"}
        )
        email_config = json.loads(email_secret.payload.data.decode("UTF-8"))
        
        # Set environment variables
        os.environ['SENDER_EMAIL'] = email_config['sender_email']
        os.environ['SENDER_PASSWORD'] = email_config['sender_password']
        os.environ['RECIPIENT_EMAIL'] = email_config['recipient_email']
        
    except Exception as e:
        print(f"Warning: Could not load email credentials: {e}")
        # Continue without email notifications
        
    # Run tests
    tester = XTrillionAPITester("production")
    summary = tester.run_all_tests()
    
    # Return results
    return {
        'statusCode': 200 if summary['failed'] == 0 else 500,
        'body': json.dumps(summary)
    }
EOF

# Copy the test suite
cp daily_test_suite.py cloud_function_tester/

echo -e "${YELLOW}📧 Email Configuration${NC}"
echo "To enable email notifications, you need to set up email credentials."
echo ""
echo "Option 1: Gmail with App Password (Recommended)"
echo "   1. Enable 2-factor authentication on your Gmail account"
echo "   2. Generate an app password: https://myaccount.google.com/apppasswords"
echo "   3. Use the app password (not your regular password)"
echo ""
echo "Option 2: SendGrid or other SMTP service"
echo ""
read -p "Enter sender email address: " SENDER_EMAIL
read -s -p "Enter sender password/app password: " SENDER_PASSWORD
echo ""
read -p "Enter recipient email address (for notifications): " RECIPIENT_EMAIL

# Step 3: Store email credentials in Secret Manager
echo -e "${GREEN}3. Storing email credentials securely...${NC}"

# Create secret
cat > /tmp/email_credentials.json << EOF
{
    "sender_email": "$SENDER_EMAIL",
    "sender_password": "$SENDER_PASSWORD",
    "recipient_email": "$RECIPIENT_EMAIL",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587
}
EOF

# Create or update secret
gcloud secrets create email-credentials \
    --data-file=/tmp/email_credentials.json \
    --project=$PROJECT_ID 2>/dev/null || \
gcloud secrets versions add email-credentials \
    --data-file=/tmp/email_credentials.json \
    --project=$PROJECT_ID

rm /tmp/email_credentials.json

# Step 4: Deploy Cloud Function
echo -e "${GREEN}4. Deploying Cloud Function...${NC}"

gcloud functions deploy xtrillion-daily-tests \
    --runtime=python310 \
    --trigger-http \
    --entry-point=run_daily_tests \
    --source=cloud_function_tester \
    --region=$REGION \
    --timeout=540s \
    --memory=512MB \
    --allow-unauthenticated \
    --set-env-vars="ALWAYS_SEND_EMAIL=false" \
    --project=$PROJECT_ID

# Get function URL
FUNCTION_URL=$(gcloud functions describe xtrillion-daily-tests \
    --region=$REGION \
    --format="value(httpsTrigger.url)" \
    --project=$PROJECT_ID)

# Step 5: Create Cloud Scheduler Job
echo -e "${GREEN}5. Creating Cloud Scheduler job...${NC}"

# Create scheduler job (runs at 8 AM daily)
gcloud scheduler jobs create http xtrillion-daily-api-tests \
    --location=$REGION \
    --schedule="0 8 * * *" \
    --time-zone="America/New_York" \
    --uri="$FUNCTION_URL" \
    --http-method=GET \
    --description="Daily automated testing of XTrillion Bond Analytics API" \
    --project=$PROJECT_ID

echo -e "${GREEN}✅ Daily testing setup complete!${NC}"
echo ""
echo "📊 Test Schedule:"
echo "   - Tests run daily at 8:00 AM Eastern Time"
echo "   - Email notifications sent only on failures"
echo "   - Results stored in Cloud Function logs"
echo ""
echo "🔧 Useful Commands:"
echo "   View schedule:     gcloud scheduler jobs list --location=$REGION"
echo "   Run test now:      gcloud scheduler jobs run xtrillion-daily-api-tests --location=$REGION"
echo "   View logs:         gcloud functions logs read xtrillion-daily-tests"
echo "   Update schedule:   gcloud scheduler jobs update http xtrillion-daily-api-tests --schedule='0 9 * * *' --location=$REGION"
echo ""
echo "📧 Email Settings:"
echo "   To update email settings, update the secret:"
echo "   gcloud secrets versions add email-credentials --data-file=new_credentials.json"
echo ""
echo "🧪 Manual Testing:"
echo "   You can also run tests manually:"
echo "   python3 daily_test_suite.py"