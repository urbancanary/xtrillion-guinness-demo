# Cloudflare Setup for Professional URLs

## Current Setup:
- **Production API**: Probably already using xtrillion.ai domain
- **App Engine Services**: Running on Google Cloud subdomains

## Proposed Professional URLs:

### For Maia Dev:
```
api-dev.xtrillion.ai → Maia Dev App Engine
```
or
```
dev-api.xtrillion.ai → Maia Dev App Engine
```

### For RMB Dev (Optional):
```
api-sandbox.xtrillion.ai → RMB Dev App Engine
```
or just use App Engine URL directly since it's internal only

### For Production:
```
api.xtrillion.ai → Production App Engine
```

## How to Set Up in Cloudflare:

### Option 1: Subdomain Approach (Recommended)

1. **Add DNS Records in Cloudflare**:
   ```
   Type: CNAME
   Name: api-dev
   Target: ghs.googlehosted.com
   Proxy: Yes (orange cloud)
   ```

2. **Configure App Engine**:
   ```bash
   # Add custom domain to Maia Dev service
   gcloud app domain-mappings create api-dev.xtrillion.ai \
     --service=maia-dev \
     --project=future-footing-414610
   ```

3. **Verify Domain** (if not already verified):
   ```bash
   gcloud domains verify api-dev.xtrillion.ai
   ```

### Option 2: Path-Based Routing (Single Domain)

Use Cloudflare Workers to route based on path:

```javascript
// Cloudflare Worker Script
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)
  
  // Route based on path
  if (url.pathname.startsWith('/dev/')) {
    // Route to Maia Dev
    const newUrl = 'https://maia-dev-dot-future-footing-414610.uc.r.appspot.com' + url.pathname.replace('/dev', '')
    return fetch(newUrl, request)
  } else {
    // Route to Production
    const newUrl = 'https://future-footing-414610.uc.r.appspot.com' + url.pathname
    return fetch(newUrl, request)
  }
}
```

### Option 3: Header-Based Routing (API Key Approach)

Keep single domain but route based on API key prefix:

```javascript
// Cloudflare Worker
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const apiKey = request.headers.get('X-API-Key')
  
  if (apiKey && apiKey.startsWith('maia_dev_')) {
    // Route to Maia Dev
    return fetch('https://maia-dev-dot-future-footing-414610.uc.r.appspot.com' + new URL(request.url).pathname, request)
  } else {
    // Route to Production
    return fetch('https://future-footing-414610.uc.r.appspot.com' + new URL(request.url).pathname, request)
  }
}
```

## Recommended Approach:

**For Maia**: Use subdomain `api-dev.xtrillion.ai`
- Professional looking
- Clear separation from production
- Easy to communicate to Maia team
- Can add SSL certificate

**For RMB Dev**: Keep App Engine URL
- It's just for you
- Saves DNS complexity
- Can always add later if needed

## Steps to Implement:

1. **In Cloudflare Dashboard**:
   - Add CNAME record for `api-dev`
   - Point to `ghs.googlehosted.com`
   - Enable proxy (orange cloud)

2. **In Google Cloud Console**:
   ```bash
   # Map custom domain to maia-dev service
   gcloud app domain-mappings create api-dev.xtrillion.ai \
     --service=maia-dev \
     --project=future-footing-414610
   ```

3. **Update Documentation for Maia**:
   ```
   Development API Endpoint: https://api-dev.xtrillion.ai
   Production API Endpoint: https://api.xtrillion.ai
   ```

## Benefits:
- ✅ Professional appearance for Maia
- ✅ Clear environment separation  
- ✅ Consistent branding
- ✅ Easy to remember
- ✅ Cloudflare protection/caching if needed

## No Custom URL Needed For:
- **RMB Dev**: You can use App Engine URL directly
- **Hotfix**: Internal only, App Engine URL is fine