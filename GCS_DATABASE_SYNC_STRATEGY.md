# GCS Database Sync Strategy

## Problem

We need bidirectional sync between local and cloud databases to handle:
1. **Treasury yield updates** - Daily changes from Treasury API
2. **Bond data additions** - New bonds added locally
3. **Conflict resolution** - When both local and cloud change

## Solution Architecture

### 1. Sync Script (`sync_databases_with_gcs.py`)

**Features:**
- Downloads cloud databases to compare
- Calculates SHA256 hashes to detect changes
- Merges Treasury updates (takes most recent)
- Uploads merged result back to GCS
- Handles all three databases

**Usage:**
```bash
# Sync all databases
python3 sync_databases_with_gcs.py

# Sync specific database
python3 sync_databases_with_gcs.py --database bonds_data.db
```

### 2. Cloud Treasury Updater (`cloud_treasury_updater.py`)

**For App Engine cron jobs:**
- Downloads database from GCS
- Updates Treasury yields
- Uploads back to GCS
- Works in read-only App Engine environment

### 3. Deployment Scripts

#### `deploy_appengine_with_sync.sh` (Recommended)
```bash
./deploy_appengine_with_sync.sh
```
- Syncs databases before deployment
- Runs tests to verify
- Deploys to App Engine

#### `deploy_with_treasury_update.sh`
```bash
./deploy_with_treasury_update.sh
```
- Updates Treasury yields locally
- Commits to git
- Deploys to App Engine

## Sync Logic

### For Treasury Tables (`tsys_enhanced`, `treasury_securities`):
1. Compare `updated_at` timestamps
2. Take the most recent data
3. Merge missing rows

### For Other Tables:
1. If hashes differ, prefer local (assumes local has latest bonds)
2. Upload local to cloud

## Workflow Examples

### Daily Treasury Update (Cloud-initiated)
```
App Engine Cron → cloud_treasury_updater.py → Update GCS
                                              ↓
Next local sync ← sync_databases_with_gcs.py ←
```

### Manual Bond Addition (Local-initiated)
```
Add bonds locally → deploy_appengine_with_sync.sh → Upload to GCS
                                                    ↓
                    App Engine uses updated DB ←────
```

### Conflict Resolution
```
Local changes + Cloud changes → sync_databases_with_gcs.py
                                         ↓
                              Merge (Treasury: newest wins)
                              Other tables: local wins
                                         ↓
                              Upload merged to GCS
```

## Best Practices

1. **Before deployment:** Always run `deploy_appengine_with_sync.sh`
2. **After cloud updates:** Run `sync_databases_with_gcs.py` locally
3. **Regular sync:** Add to your daily workflow

## Monitoring

- Check GCS metadata for last update time
- Query `tsys_enhanced` for latest yield date
- Review sync script logs for conflicts

## Future Improvements

1. **Version tracking:** Add version numbers to track changes
2. **Automated conflict resolution:** Rules for specific tables
3. **Backup before sync:** Keep last N versions
4. **Real-time sync:** Cloud Functions for immediate propagation