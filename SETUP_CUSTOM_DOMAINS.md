# Setting Up Custom Domains for App Engine Services

## The Modern Approach (2024+)

Google App Engine now handles custom domains differently. You can't map domains directly to services anymore. Instead:

1. **Map domain to the app** (not a specific service)
2. **Use dispatch.yaml** to route by hostname

## Step-by-Step Setup:

### 1. First Deploy the Services

```bash
# Deploy maia-dev service (if not done)
gcloud app deploy app.maia-dev.yaml --version=maia-v1 --quiet

# Deploy rmb-dev service (if not done)
gcloud app deploy app.rmb-dev.yaml --version=rmb-v1 --quiet
```

### 2. Create Domain Mapping

```bash
# Map the domain to your app (not service-specific)
gcloud app domain-mappings create api-dev.xtrillion.ai \
  --project=future-footing-414610
```

### 3. Deploy Dispatch Rules

```bash
# Deploy the dispatch.yaml to route by hostname
gcloud app deploy dispatch.yaml --project=future-footing-414610
```

### 4. Verify Setup

```bash
# List domain mappings
gcloud app domain-mappings list --project=future-footing-414610

# List dispatch rules
gcloud app dispatch-rules list --project=future-footing-414610
```

## How It Works:

1. **DNS** points `api-dev.xtrillion.ai` to Google's IPs
2. **App Engine** receives the request
3. **Dispatch rules** check the hostname
4. **Routes** to `maia-dev` service based on hostname

## Testing:

```bash
# Test production (default service)
curl https://api.xtrillion.ai/health

# Test Maia Dev (after DNS propagates)
curl https://api-dev.xtrillion.ai/health
```

## Alternative: Path-Based Routing

If hostname routing doesn't work, use path-based:

```yaml
# dispatch.yaml for path-based routing
dispatch:
  - url: "*/maia-dev/*"
    service: maia-dev
  - url: "*/rmb-dev/*"
    service: rmb-dev
  - url: "*/*"
    service: default
```

Then access via:
- Production: `https://api.xtrillion.ai/api/v1/...`
- Maia Dev: `https://api.xtrillion.ai/maia-dev/api/v1/...`

## Troubleshooting:

If you get errors:
1. Make sure services are deployed first
2. Check that DNS records are added in Cloudflare
3. Wait 15-30 minutes for SSL certificates
4. Use `--verbosity=debug` for detailed errors