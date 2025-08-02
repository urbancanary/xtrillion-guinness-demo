# Cloud Treasury Update Strategy for Google App Engine

## Challenge

Google App Engine has limitations that prevent traditional scheduled updates:
1. **Read-only filesystem** - Can't write to local SQLite databases
2. **Ephemeral instances** - Scale up/down, losing local changes
3. **No system cron** - Must use App Engine's cron service

## Solution Architecture

### Option 1: App Engine Cron + Cloud SQL (Recommended for Production)
```
App Engine Cron → API Endpoint → Cloud SQL
```

**Pros:**
- Persistent database updates
- Scales with application
- Proper transaction support

**Cons:**
- Requires Cloud SQL setup (~$50/month minimum)
- More complex architecture

### Option 2: App Engine Cron + Cloud Storage (Current Architecture)
```
App Engine Cron → API Endpoint → Update GCS Database → Re-upload
```

**Implementation:**
1. Create cron.yaml:
```yaml
cron:
- description: "Update Treasury yields daily"
  url: /api/v1/admin/update-treasury-yields
  schedule: every day 18:00
  timezone: America/New_York
```

2. Deploy cron configuration:
```bash
gcloud app deploy cron.yaml
```

3. API endpoint (`/api/v1/admin/update-treasury-yields`):
   - Downloads current database from GCS
   - Updates Treasury yields
   - Re-uploads to GCS
   - Next instance deployment picks up new data

**Pros:**
- Works with existing GCS architecture
- No additional costs
- Maintains single source of truth

**Cons:**
- Updates not immediately visible (requires redeploy)
- Potential race conditions during update

### Option 3: External Update Service + GitHub Actions
```
GitHub Actions → Update Local DB → Commit → Auto-deploy
```

**Implementation:**
1. GitHub Action runs daily at 6 PM ET
2. Updates local database
3. Commits changes
4. Triggers automatic deployment

**Pros:**
- Version controlled updates
- Audit trail of all changes
- Works with embedded database strategy

**Cons:**
- Requires GitHub Actions minutes
- Deployment downtime during updates

## Recommended Approach

For the current architecture using embedded databases:

1. **Immediate**: Use Option 3 (GitHub Actions)
   - Set up `.github/workflows/update-treasury-yields.yml`
   - Run `us_treasury_yield_fetcher.py` daily
   - Commit and push changes
   - Auto-deploy via existing pipeline

2. **Future**: Migrate to Option 1 (Cloud SQL)
   - When scale justifies the cost
   - Provides real-time updates
   - Better for multiple instances

## Implementation Steps

### GitHub Actions Workflow
```yaml
name: Update Treasury Yields

on:
  schedule:
    # 6 PM ET daily (11 PM UTC)
    - cron: '0 23 * * 1-5'
  workflow_dispatch:  # Manual trigger

jobs:
  update-yields:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Update Treasury yields
      run: |
        python us_treasury_yield_fetcher.py
    
    - name: Commit changes
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add bonds_data.db
        git commit -m "🏦 Update Treasury yields for $(date +%Y-%m-%d)" || exit 0
    
    - name: Push changes
      uses: ad-m/github-push-action@master
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
```

### App Engine Cron (for future Cloud SQL)
```python
@app.route('/api/v1/admin/update-treasury-yields', methods=['GET', 'POST'])
def update_treasury_yields():
    # Verify request is from App Engine Cron
    if request.headers.get('X-Appengine-Cron') != 'true':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Update yields in Cloud SQL
    # ...
```

## Security Notes

1. **App Engine Cron**: Automatically adds `X-Appengine-Cron: true` header
2. **GitHub Actions**: Uses repository secrets for sensitive data
3. **API Endpoint**: Should verify cron header to prevent unauthorized access

## Monitoring

1. **App Engine**: Check logs in Cloud Console
2. **GitHub Actions**: Monitor workflow runs in Actions tab
3. **Database**: Query `tsys_enhanced` table for latest update timestamp