# Final 3-Stage Environment Setup

## Your Pipeline is Ready! 🚀

### 1. RMB Dev (Your Personal Playground)
- **Service**: `development` 
- **URL**: `https://development-dot-future-footing-414610.uc.r.appspot.com`
- **Purpose**: Your experimentation and development
- **Deploy**: `gcloud app deploy app.development.yaml`

### 2. Maia Dev (Stable Development)
- **Service**: `maia-dev`
- **URL**: `https://api-dev.x-trillion.ai` ✨
- **Purpose**: Maia's testing environment
- **Deploy**: `gcloud app deploy app.maia-dev-minimal.yaml`

### 3. Production
- **Service**: `default`
- **URL**: `https://api.x-trillion.ai`
- **Purpose**: Live production environment
- **Deploy**: `gcloud app deploy app.yaml` (with extreme caution!)

## Deployment Flow:

```
Your Development → Maia Dev → Production
(development)     (maia-dev)   (default)
```

## Quick Commands:

### Deploy to your dev:
```bash
gcloud app deploy app.development.yaml --version=dev-$(date +%Y%m%d-%H%M%S)
```

### Deploy to Maia dev:
```bash
# Normal feature promotion
./deploy.sh maia-dev

# Or hotfix directly
gcloud app deploy app.maia-dev-minimal.yaml --version=maia-$(date +%Y%m%d-%H%M%S)
```

### Check which environment you're in:
```bash
# Your dev
curl https://development-dot-future-footing-414610.uc.r.appspot.com/health

# Maia dev  
curl https://api-dev.x-trillion.ai/health

# Production
curl https://api.x-trillion.ai/health
```

## Advantages of Current Setup:

1. **No custom URL needed for your dev** - App Engine URL works fine
2. **Maia gets professional URL** - `api-dev.x-trillion.ai`
3. **Clear separation** - Different service names
4. **Already working** - No more setup needed!

## Future Options:

If you want a custom URL for your dev later:
1. Add DNS: `api-sandbox.x-trillion.ai`
2. Update dispatch.yaml
3. You'd have an easier-to-remember URL

But for now, bookmarking the App Engine URL works great!

## Important URLs to Bookmark:

```
🧪 Your Dev: https://development-dot-future-footing-414610.uc.r.appspot.com
👥 Maia Dev: https://api-dev.x-trillion.ai
🌍 Production: https://api.x-trillion.ai
```

## Skip_files Issue Workaround:

For now, use minimal yaml files or the existing app.development.yaml if it works. The skip_files error seems to be a gcloud CLI bug.