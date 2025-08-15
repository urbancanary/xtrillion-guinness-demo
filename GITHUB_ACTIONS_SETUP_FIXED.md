# GitHub Actions Setup Guide - Treasury Yield Updates

## Overview
This guide explains how to set up automated Treasury yield updates using GitHub Actions.

## Workflows Created

### 1. `update-treasury-yields-simple.yml`
- **Purpose**: Fetches daily Treasury yields and updates the local database
- **Schedule**: Runs at 6 PM ET every weekday
- **No cloud authentication required** - works out of the box

### 2. `sync-database-to-gcs.yml` (Optional)
- **Purpose**: Syncs the updated database to Google Cloud Storage
- **Trigger**: Runs after successful Treasury update
- **Requires**: Google Cloud authentication setup (see below)

## Setup Instructions

### Step 1: Enable GitHub Actions
1. Go to your repository on GitHub
2. Click on "Actions" tab
3. Enable workflows if not already enabled

### Step 2: Manual Trigger (Test)
1. Go to Actions tab
2. Select "Update Treasury Yields (Simplified)"
3. Click "Run workflow"
4. Select branch and run

### Step 3: Google Cloud Authentication (Optional)

If you want to sync to Google Cloud Storage, you need to set up authentication:

#### Option A: Service Account Key (Simpler)
1. Create a service account in Google Cloud Console:
   ```bash
   gcloud iam service-accounts create github-actions \
     --display-name="GitHub Actions Service Account"
   ```

2. Grant necessary permissions:
   ```bash
   gcloud projects add-iam-policy-binding future-footing-414610 \
     --member="serviceAccount:github-actions@future-footing-414610.iam.gserviceaccount.com" \
     --role="roles/storage.objectAdmin"
   ```

3. Create and download key:
   ```bash
   gcloud iam service-accounts keys create key.json \
     --iam-account=github-actions@future-footing-414610.iam.gserviceaccount.com
   ```

4. Add to GitHub Secrets:
   - Go to Settings → Secrets and variables → Actions
   - Create new secret named `GCP_SA_KEY`
   - Paste the contents of `key.json`

#### Option B: Workload Identity Federation (More Secure)
See [Google's guide](https://github.com/google-github-actions/auth#setup) for detailed setup.

## Fixed Issues

### 1. ✅ SQLite3 Import Error
- **Problem**: `pip install sqlite3` fails because sqlite3 is built-in
- **Solution**: Removed sqlite3 from pip install command

### 2. ✅ Deprecated Actions
- **Problem**: Using outdated action versions (v3)
- **Solution**: Updated all actions to latest versions (v4/v5)

### 3. ✅ Authentication Error
- **Problem**: Missing Google Cloud credentials
- **Solution**: Made GCS sync optional with proper auth setup

## Testing the Workflows

### Test Treasury Update (No Auth Required)
```bash
# This should work immediately without any setup
gh workflow run "Update Treasury Yields (Simplified)"
```

### Monitor Workflow
```bash
# Watch the workflow run
gh run watch

# View workflow runs
gh run list --workflow="Update Treasury Yields (Simplified)"
```

## Troubleshooting

### If workflow fails with "Permission denied"
1. Check repository settings → Actions → General
2. Ensure "Read and write permissions" is enabled for GITHUB_TOKEN

### If database update fails
1. Check that `us_treasury_yield_fetcher.py` exists in `google_analysis10/`
2. Verify the script doesn't require additional dependencies

### If GCS sync fails
1. Verify `GCP_SA_KEY` secret is set correctly
2. Check service account has storage.objectAdmin permission
3. Verify bucket `gs://json-receiver-databases/` exists

## Alternative: Manual Updates

If you prefer not to use GitHub Actions, you can update manually:

```bash
# Local update
cd google_analysis10
python us_treasury_yield_fetcher.py

# Upload to GCS
gsutil cp bonds_data.db gs://json-receiver-databases/bonds_data.db
```

## Summary

The workflows are now fixed and ready to use:
- ✅ No more sqlite3 import errors
- ✅ Updated to latest action versions
- ✅ Works without Google Cloud authentication
- ✅ Optional GCS sync with proper auth setup