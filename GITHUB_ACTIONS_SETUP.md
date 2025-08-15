# GitHub Actions Setup for Treasury Updates

## Issue
The automated treasury yield update workflow is failing because the `GCP_SA_KEY` secret is not configured in the GitHub repository.

## Solution
To enable automatic treasury yield updates, you need to add the following secret to your GitHub repository:

1. Go to your repository settings: https://github.com/urbancanary/xtrillion-guinness-demo/settings/secrets/actions

2. Click "New repository secret"

3. Add the following secret:
   - **Name**: `GCP_SA_KEY`
   - **Value**: Your Google Cloud Service Account JSON key

## Getting the Service Account Key

1. Go to Google Cloud Console: https://console.cloud.google.com/iam-admin/serviceaccounts?project=future-footing-414610

2. Find or create a service account with the following permissions:
   - Storage Object Admin (for uploading to GCS)
   - App Engine Deployer (if needed)

3. Create a JSON key for the service account

4. Copy the entire JSON content and paste it as the secret value

## Alternative: Manual Updates

If you cannot set up the GitHub Actions workflow, you can manually update treasury yields:

```bash
# 1. Update treasury data locally
python3 update_treasury_manual.py

# 2. Deploy to production
gcloud app deploy app.production-simple.yaml --quiet

# 3. Verify the update
curl -s "https://api.x-trillion.ai/api/v1/treasury/status" -H "X-API-Key: your_key" | jq '.treasury_data.is_fresh'
```

## Current Status
- Treasury data last updated: 2025-08-08 (manually)
- Workflow status: ❌ Failing due to missing GCP_SA_KEY secret
- Next scheduled run: 11 PM UTC (if secret is added)