# Deployment Strategy Guide

## ⚠️ CRITICAL: Choose the Right Deployment Strategy

We have **THREE deployment strategies** with different database handling:

### 1. 🌐 **GCS Dynamic (RECOMMENDED)** - `app.yaml`
```bash
./deploy_appengine.sh
```
- **Database Source**: Google Cloud Storage (GCS)
- **How it works**: Downloads databases from GCS on startup
- **Pros**: 
  - ✅ Treasury updates without redeployment
  - ✅ Update databases via GCS upload
  - ✅ Smaller deployments (code only)
- **Cons**: 
  - ❌ Slower cold starts (downloads databases)
  - ❌ Requires GCS permissions
- **Use when**: You need frequent database updates

### 2. 💾 **Embedded (FAST)** - `app.production.yaml`
```bash
./deploy_production_optimized.sh
```
- **Database Source**: Baked into container
- **How it works**: Databases included in Docker image
- **Pros**: 
  - ✅ Fastest startup (no downloads)
  - ✅ No external dependencies
  - ✅ Best performance
- **Cons**: 
  - ❌ Requires redeployment for updates
  - ❌ Larger container size
- **Use when**: Performance is critical, updates are rare

### 3. 🔄 **Persistent Storage** - `app.persistent.yaml`
```bash
./deploy_persistent_storage.sh
```
- **Database Source**: Downloads once, caches locally
- **How it works**: Downloads from GCS, stores on persistent disk
- **Pros**: 
  - ✅ Fast after first download
  - ✅ Can update via scheduler
- **Cons**: 
  - ❌ More complex setup
  - ❌ Requires persistent disk
- **Use when**: Need balance of performance and updates

## 🎯 Current Status (August 2025)

**We've been using**: Embedded strategy (`app.production.yaml`)
**Problem**: Treasury updates require full redeployment
**Solution**: Switch to GCS Dynamic strategy

## 📋 How to Switch to GCS Dynamic

1. **Ensure databases are in GCS**:
   ```bash
   gsutil cp bonds_data.db gs://json-receiver-databases/
   gsutil cp validated_quantlib_bonds.db gs://json-receiver-databases/
   gsutil cp bloomberg_index.db gs://json-receiver-databases/
   ```

2. **Deploy with GCS strategy**:
   ```bash
   ./deploy_appengine.sh  # Uses app.yaml with DATABASE_SOURCE: gcs
   ```

3. **Update Treasury yields without redeployment**:
   ```bash
   # Update local database
   python3 us_treasury_yield_fetcher.py
   
   # Vacuum and upload to GCS
   sqlite3 bonds_data.db "PRAGMA wal_checkpoint(FULL); VACUUM;"
   gsutil cp bonds_data.db gs://json-receiver-databases/
   
   # No redeployment needed! Next cold start uses new data
   ```

## 🔍 How to Check Current Deployment

```bash
# Check which app.yaml was used
gcloud app versions describe production --service=default | grep DATABASE_SOURCE
```

## 📊 Comparison Table

| Feature | GCS Dynamic | Embedded | Persistent |
|---------|-------------|----------|------------|
| Treasury Updates | ✅ No redeploy | ❌ Redeploy | ✅ Via scheduler |
| Cold Start | 🐢 10-15s | 🚀 2-3s | 🐇 5s |
| Deployment Size | 📦 50MB | 📦 200MB | 📦 50MB |
| Complexity | ⭐ Simple | ⭐ Simple | ⭐⭐⭐ Complex |
| Best For | Daily updates | Stable data | Hourly updates |

## 🚨 Action Required

**For Treasury yield updates without redeployment**, we should:
1. Switch to GCS Dynamic strategy
2. Use `./deploy_appengine.sh` (not the production-optimized one)
3. Update databases via GCS uploads

This allows Treasury updates via:
- GitHub Actions (upload to GCS)
- Manual updates (upload to GCS)
- App Engine cron (update GCS directly)