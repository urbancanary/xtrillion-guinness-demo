# Cloudflare DNS Setup for Maia Dev

## Current Setup (Production):
You have 4 A records for `api.xtrillion.ai`:
- 216.239.32.21
- 216.239.34.21
- 216.239.36.21
- 216.239.38.21

These are Google's IP addresses for App Engine custom domains.

## Add for Maia Dev:

### Option 1: A Records (Match Production Setup)
Add these 4 A records for `api-dev`:

```
Type: A
Name: api-dev
Value: 216.239.32.21
Proxy: DNS only (gray cloud)
TTL: Auto

Type: A
Name: api-dev
Value: 216.239.34.21
Proxy: DNS only (gray cloud)
TTL: Auto

Type: A
Name: api-dev
Value: 216.239.36.21
Proxy: DNS only (gray cloud)
TTL: Auto

Type: A
Name: api-dev
Value: 216.239.38.21
Proxy: DNS only (gray cloud)
TTL: Auto
```

### Option 2: CNAME Record (Simpler)
OR add a single CNAME record:

```
Type: CNAME
Name: api-dev
Value: ghs.googlehosted.com
Proxy: DNS only (gray cloud)
TTL: Auto
```

## After Adding DNS Records:

1. **Map the domain in App Engine**:
```bash
gcloud app domain-mappings create api-dev.xtrillion.ai \
  --service=maia-dev \
  --project=future-footing-414610
```

2. **Verify the mapping**:
```bash
gcloud app domain-mappings list --project=future-footing-414610
```

3. **Test the new URL**:
```bash
# Should work after DNS propagates (5-10 minutes)
curl https://api-dev.xtrillion.ai/health
```

## Important Notes:

1. **DNS Only vs Proxied**:
   - Your production uses "DNS only" (gray cloud)
   - Keep the same for consistency
   - This means traffic goes directly to Google, not through Cloudflare's proxy

2. **SSL Certificate**:
   - Google automatically provisions SSL certificates
   - May take 15-30 minutes to activate
   - The URL will show security warnings until cert is ready

3. **Why 4 A Records?**:
   - Google uses multiple IPs for redundancy
   - If one IP fails, others take over
   - Standard App Engine setup

## Recommended Approach:
Since your production uses A records with "DNS only", I recommend using the same pattern for consistency:
- Add 4 A records for `api-dev`
- Use the same Google IPs
- Keep "DNS only" setting

This ensures both environments work identically.