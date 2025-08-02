# 🚀 Deploy to Production Guide - August 2, 2025

## 📋 Changes Ready for Production

**Commit**: `efd0a2a` - feat: Add flexible input ordering and enhanced fallback mechanisms

### Features Included:
- ✅ Flexible input ordering endpoint (`/api/v1/bond/analysis/flexible`)
- ✅ Smart input detector for automatic parameter detection
- ✅ Fixed spread calculations in production (GCS database init)
- ✅ Fixed App Engine deployment (using /tmp/ directory)
- ✅ Enhanced ISIN fallback hierarchy
- ✅ Treasury date fallback for weekends/holidays
- ✅ Fixed Google Sheets numeric input handling

## 🛡️ Safe Deployment Steps

### Step 1: Create Pull Request
```bash
# Push develop branch to GitHub
git push origin develop

# Create PR on GitHub from develop → main
# Or use GitHub CLI:
gh pr create --base main --head develop \
  --title "feat: Add flexible input ordering and enhanced fallback mechanisms" \
  --body "## Summary
- Added flexible bond analysis endpoint
- Fixed production spread calculations
- Enhanced fallback mechanisms for robust operation

## Testing
- ✅ All tests passing locally
- ✅ Deployed and tested on test version
- ✅ API endpoints verified working

Test URL: https://test-20250802-203308-dot-future-footing-414610.uc.r.appspot.com"
```

### Step 2: Merge Pull Request
1. Review the changes on GitHub
2. Approve and merge the PR
3. This updates the main branch

### Step 3: Deploy to Production
```bash
# Switch to main branch
git checkout main
git pull origin main

# Deploy to production
./deploy_production.sh
```

### Step 4: Verify Production
```bash
# Check health
curl -s "https://future-footing-414610.uc.r.appspot.com/health" | jq '.'

# Test flexible endpoint
curl -s -X POST "https://future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis/flexible" \
  -H "Content-Type: application/json" \
  -d '[71.66, "T 3 15/08/52", "2025-07-31"]' | jq '.analytics.ytm'
```

## ⚡ Quick Alternative (if urgent)

If you need to deploy immediately without the PR process:

```bash
# Option A: Promote test version
gcloud app versions migrate test-20250802-203308 --service=default

# Option B: Direct deploy from develop (not recommended)
git checkout develop
./deploy_production.sh
```

## 🔄 Rollback Plan

If anything goes wrong:
```bash
./rollback_production.sh
```

## 📞 Support

If you encounter any issues:
1. Check logs: `gcloud app logs tail -s default`
2. Run health check
3. Use rollback if needed

---

**Remember**: External users depend on the production API. Always test thoroughly!