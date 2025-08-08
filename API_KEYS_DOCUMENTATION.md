# API Keys Documentation

## 🔑 Master Key List

### Your Keys (RMB)

| Key | Purpose | Works In | Notes |
|-----|---------|----------|-------|
| `gax10_admin_9k3m7p5w2r8t6v4x1z` | Admin Master Key | All environments | Your personal master key |
| `gax10_demo_3j5h8m9k2p6r4t7w1q` | Demo/Sheets Key | Production, Maia-dev | Used in Google Sheets |
| `gax10_dev_4n8s6k2x7p9v5m1w8z` | Development Key | All environments | General development |

### Client Keys

| Key | Client | Purpose | Billing |
|-----|--------|---------|---------|
| `gax10_maia_7k9d2m5p8w1e6r4t3y2x` | Maia Software | Production API access | PAID - Track usage |

### Other Keys (for future use)

| Key | Purpose |
|-----|---------|
| `gax10_inst_7k9d2m5p8w1e6r4t3y` | Institutional clients |
| `gax10_test_9r4t7w2k5m8p1z6x3v` | Internal testing |
| `gax10_trial_6k8p2r9w4m7v1t5z8x` | Trial access |
| `gax10_stage_2p6k9r4w7t1m5v8z3x` | Staging environment |
| `gax10_prod_8w5r9k2t6p1v4z7m3x` | Production deployment |
| `gax10_api_5t8k2w7r4p9v1z6m3x` | General API access |

## 🌐 Environment Access Rules

### 1. Your Development Environment
- **URL**: `https://development-dot-future-footing-414610.uc.r.appspot.com`
- **API Key Required**: ❌ NO
- **Purpose**: Your personal playground for testing

### 2. Maia Development
- **URL**: `https://api-dev.x-trillion.ai`
- **API Key Required**: ✅ YES
- **Valid Keys**: All keys listed above
- **Purpose**: Maia's testing environment

### 3. Production
- **URL**: `https://api.x-trillion.ai`
- **API Key Required**: ✅ YES
- **Valid Keys**: All keys listed above
- **Purpose**: Live production API

## 📊 Google Sheets Configuration

### Current Setup (NO CHANGES NEEDED)
Your Google Sheets functions are already configured correctly:

```javascript
// In xt_functions.gs
var API_BASE = "https://future-footing-414610.uc.r.appspot.com";
var API_KEY = "gax10_demo_3j5h8m9k2p6r4t7w1q";

// In xt_functions_batch_dev.gs (for dev testing)
var DEV_API_BASE = "https://development-dot-future-footing-414610.uc.r.appspot.com";
var DEV_API_KEY = "gax10_dev_4n8s6k2x7p9v5m8p1z";
```

### If You Need to Update Sheets

1. **For Production Sheets**: Use the demo key
   ```javascript
   var API_KEY = "gax10_demo_3j5h8m9k2p6r4t7w1q";
   ```

2. **For Your Test Sheets**: Use dev environment (no key needed)
   ```javascript
   var API_BASE = "https://development-dot-future-footing-414610.uc.r.appspot.com";
   // No API key needed!
   ```

## 🔍 Testing Commands

### Test Your Admin Access
```bash
# Production
curl -X POST https://api.x-trillion.ai/api/v1/bond/analysis \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_admin_9k3m7p5w2r8t6v4x1z" \
  -d '{"description":"T 3 15/08/52","price":71.66}'

# Maia Dev
curl -X POST https://api-dev.x-trillion.ai/api/v1/bond/analysis \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_admin_9k3m7p5w2r8t6v4x1z" \
  -d '{"description":"T 3 15/08/52","price":71.66}'

# Your Dev (no key needed!)
curl -X POST https://development-dot-future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis \
  -H "Content-Type: application/json" \
  -d '{"description":"T 3 15/08/52","price":71.66}'
```

## 💰 Monitoring Maia's Usage

Look for these log entries:
```
💰 MAIA API USAGE: Maia Software API Access accessing /api/v1/bond/analysis at api.x-trillion.ai
```

### View Logs
```bash
# Production logs
gcloud app logs tail -s default | grep "💰"

# Maia-dev logs
gcloud app logs tail -s maia-dev | grep "💰"
```

## 🚨 Important Notes

1. **NEVER share your admin key** (`gax10_admin_9k3m7p5w2r8t6v4x1z`)
2. **Maia only gets their key** (`gax10_maia_7k9d2m5p8w1e6r4t3y2x`)
3. **Google Sheets continue to work** with existing keys
4. **Your dev environment needs NO key**

## 📝 Key Distribution

### For Maia
Send them this:
```
API Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x
Works in both:
- Production: https://api.x-trillion.ai
- Testing: https://api-dev.x-trillion.ai

Include in header: X-API-Key: [your-key]
```

### For Future Clients
Create new keys following pattern:
```
gax10_[client]_[24-random-chars]
```

## 🔄 Key Rotation

If you need to rotate keys:
1. Add new key to VALID_API_KEYS in google_analysis10_api.py
2. Deploy to maia-dev first
3. Test thoroughly
4. Deploy to production
5. Update client with new key
6. Remove old key after transition period