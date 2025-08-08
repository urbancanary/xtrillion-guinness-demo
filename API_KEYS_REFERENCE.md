# API Keys Reference

## Your Keys

### RMB Admin Master Key (NEW)
```
gax10_admin_9k3m7p5w2r8t6v4x1z
```
- Use this for testing all environments
- Full admin access
- Not for sharing

### Development Key
```
gax10_dev_4n8s6k2x7p9v5m1w8z
```

### Demo Key (Safe for demos)
```
gax10_demo_3j5h8m9k2p6r4t7w1q
```

## Maia's Key
```
gax10_maia_7k9d2m5p8w1e6r4t3y2x
```
- Give this to Maia
- Works in both production and maia-dev
- Usage is logged with 💰 emoji

## Quick Test Commands

### Test Maia Dev
```bash
curl -X POST https://api-dev.x-trillion.ai/api/v1/bond/analysis \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_admin_9k3m7p5w2r8t6v4x1z" \
  -d '{"description":"T 3 15/08/52","price":71.66}'
```

### Test Production
```bash
curl -X POST https://api.x-trillion.ai/api/v1/bond/analysis \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_admin_9k3m7p5w2r8t6v4x1z" \
  -d '{"description":"T 3 15/08/52","price":71.66}'
```

### Test Your Dev (No key needed!)
```bash
curl -X POST https://development-dot-future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis \
  -H "Content-Type: application/json" \
  -d '{"description":"T 3 15/08/52","price":71.66}'
```

## Environment Summary

| Environment | Requires API Key | Your Access |
|-------------|------------------|-------------|
| Your Dev | ❌ NO | Always open |
| Maia Dev | ✅ YES | Use admin key |
| Production | ✅ YES | Use admin key |