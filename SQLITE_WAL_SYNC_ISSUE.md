# SQLite WAL (Write-Ahead Logging) Sync Issue

## Problem Discovered

When copying SQLite databases for cloud sync, the Write-Ahead Log (WAL) file may contain uncommitted changes that don't get included in the copy. This causes:

1. **Data inconsistency**: Local shows updated data, cloud shows old data
2. **Same file hash**: Both files appear identical but contain different data
3. **Silent failures**: Uploads succeed but data doesn't match

## Root Cause

SQLite uses Write-Ahead Logging for performance:
- Changes are written to a `.db-wal` file first
- Main `.db` file is updated later
- Simple file copies only get the main file, missing WAL changes

## Solution

Always run `VACUUM` before copying/uploading SQLite databases:

```sql
PRAGMA wal_checkpoint(FULL);  -- Flush WAL to main database
VACUUM;                       -- Rebuild database file
```

## Implementation

### 1. Manual Command
```bash
sqlite3 database.db "PRAGMA wal_checkpoint(FULL); VACUUM;"
```

### 2. Python Helper
```bash
python3 vacuum_databases.py
```

### 3. Integrated in Scripts
- `sync_databases_with_gcs.py` - Vacuums before sync
- `deploy_appengine_with_sync.sh` - Vacuums all databases
- `manual_treasury_update.sh` - Vacuums after update
- `cloud_treasury_updater.py` - Vacuums before GCS upload

## Benefits

1. **Data consistency**: Ensures all changes are included
2. **Smaller files**: VACUUM removes unused space (we saw 63% reduction)
3. **No WAL issues**: Eliminates WAL-related sync problems
4. **Better performance**: Optimized database structure

## Monitoring

Check for large WAL files:
```bash
ls -la *.db-wal
```

If WAL files are large (>1MB), run vacuum before operations.

## Lessons Learned

1. **Always vacuum** before cloud operations
2. **Check WAL size** as indicator of pending changes
3. **Test with downloads** to verify sync worked
4. **File size changes** after vacuum indicate it was needed