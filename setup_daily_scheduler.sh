# Cloud Scheduler Configuration for Daily Database Updates
# Runs at 1am daily to update XTrillion GA10 bond databases

# Create Cloud Scheduler job
gcloud scheduler jobs create http xtrillion-ga10-daily-db-update \
    --schedule="0 1 * * *" \
    --uri="https://YOUR-REGION-YOUR-PROJECT.cloudfunctions.net/updateGA10Databases" \
    --http-method=POST \
    --time-zone="America/New_York" \
    --description="Daily database update for XTrillion GA10 bond analytics" \
    --max-retry-attempts=3 \
    --max-retry-duration=300s

# Alternative: Using Cloud Run Jobs
gcloud scheduler jobs create http xtrillion-ga10-daily-db-update-run \
    --schedule="0 1 * * *" \
    --uri="https://YOUR-REGION-YOUR-PROJECT.run.app/update-databases" \
    --http-method=POST \
    --time-zone="America/New_York" \
    --description="Daily database update via Cloud Run" \
    --headers="Content-Type=application/json" \
    --body='{"source": "scheduler", "task": "daily_db_update"}'

# Cloud Function deployment command
gcloud functions deploy updateGA10Databases \
    --runtime=python311 \
    --trigger=http \
    --allow-unauthenticated \
    --memory=2048MB \
    --timeout=900s \
    --source=./cloud_function_db_update \
    --entry-point=update_databases

echo "✅ Cloud Scheduler job created: Daily 1am database updates"
echo "🔧 Customize YOUR-REGION and YOUR-PROJECT placeholders"