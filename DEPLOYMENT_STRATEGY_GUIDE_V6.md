# Three-Tier Deployment Strategy Guide
## Version 6.0 - Multi-Environment Support with Full Precision

---

## 🎯 Overview: Three-Tier Environment Strategy

XTrillion v6.0 implements a professional three-tier deployment strategy for safe development and testing:

```
testing (local) → maia_dev → production
     ↓               ↓           ↓
  localhost      Maia team   Live users
```

### Key Benefits
- 🧪 **Safe testing** - Isolate changes in testing environments
- 🤝 **Team collaboration** - Maia team tests before production
- 🎯 **Quality assurance** - Catch issues before they reach users
- 🔄 **Easy rollback** - Production remains stable during testing
- 📊 **Full precision** - All environments return raw numeric values

---

## 🌐 Environment Configurations

### 1. Testing Environment ("testing")
- **Purpose**: Your local development and testing
- **URL**: `http://localhost:8081`
- **Database**: Local files
- **Usage**: `=XT_ARRAY(A2:A10, B2:B10, , "testing")`
- **Start**: `FLASK_APP=google_analysis10_api.py flask run --port 8081`

**When to use:**
- Testing new features
- Debugging Google Sheets formulas
- Development workflow
- Performance testing

### 2. Maia Development Environment ("maia_dev")
- **Purpose**: Maia team testing before production
- **URL**: `https://maia-dev-dot-future-footing-414610.uc.r.appspot.com`
- **Database**: Google Cloud Storage (GCS)
- **Usage**: `=XT_ARRAY(A2:A10, B2:B10, , "maia_dev")`
- **Deploy**: `./deploy_maia_dev.sh`

**When to use:**
- Final testing before production
- Maia team validation
- Integration testing
- Performance validation in cloud

### 3. Production Environment ("production")
- **Purpose**: Live production for end users
- **URL**: `https://future-footing-414610.uc.r.appspot.com`
- **Database**: Embedded + GCS fallback
- **Usage**: `=XT_ARRAY(A2:A10, B2:B10)` (default)
- **Deploy**: `./deploy_production.sh`

**When to use:**
- Live client usage
- Public demonstrations
- Production workloads
- Final user experience

---

## 🚀 Deployment Workflow

### Step 1: Local Testing
```bash
# Start local API server
FLASK_APP=google_analysis10_api.py flask run --port 8081

# Test Google Sheets functions
=XT_AUTO(A2:A100, B2:B100, , "testing")
=XT_DEBUG("T 3 15/08/52", 70, , "testing")
```

**Checklist:**
- [ ] API starts without errors
- [ ] Google Sheets functions return full precision values
- [ ] All test cases pass
- [ ] Error handling works correctly

### Step 2: Deploy to Maia Development
```bash
# Switch to develop branch
git checkout develop

# Deploy to maia-dev
./deploy_maia_dev.sh
```

**Checklist:**
- [ ] Deployment succeeds
- [ ] Health check passes: `=XT_HEALTH_CHECK("maia_dev")`
- [ ] Functions work: `=XT_AUTO(A2:A10, B2:B10, , "maia_dev")`
- [ ] Notify Maia team for testing

### Step 3: Maia Team Testing
Maia team tests using `environment = "maia_dev"`:

```excel
=XT_ARRAY(A2:A100, B2:B100, , "maia_dev")
=XT_PORTFOLIO_SUMMARY(A2:A50, B2:B50, C2:C50, , "maia_dev")
=XT_TEST_ENV("maia_dev")
```

**Validation points:**
- [ ] Full precision values (6+ decimal places)
- [ ] Portfolio calculations accurate
- [ ] Performance acceptable
- [ ] No errors in typical usage

### Step 4: Deploy to Production
```bash
# Switch to main branch
git checkout main

# Merge approved changes
git merge develop

# Deploy to production
./deploy_production.sh
```

**Final checklist:**
- [ ] Maia team approval ✅
- [ ] All tests pass
- [ ] Production deployment succeeds
- [ ] Health check: `=XT_HEALTH_CHECK("production")`
- [ ] Spot check key functions

---

## 📋 Deployment Commands Reference

### Environment Scripts
```bash
# Local testing
FLASK_APP=google_analysis10_api.py flask run --port 8081

# Maia development
./deploy_maia_dev.sh

# Production
./deploy_production.sh
```

### Verification Commands
```bash
# Check deployments
gcloud app versions list --service=maia-dev
gcloud app versions list --service=default

# Health checks
curl https://maia-dev-dot-future-footing-414610.uc.r.appspot.com/health
curl https://future-footing-414610.uc.r.appspot.com/health
```

### Google Sheets Testing
```excel
# Environment connectivity
=XT_ENVIRONMENTS()              // Show all environments
=XT_TEST_ENV("testing")         // Test local
=XT_TEST_ENV("maia_dev")        // Test maia-dev
=XT_HEALTH_CHECK("production")  // Test production

# Function testing
=XT_AUTO(A2:A10, B2:B10, , "testing")
=XT_AUTO(A2:A10, B2:B10, , "maia_dev") 
=XT_AUTO(A2:A10, B2:B10)                   // Production

# Debug functions
=XT_DEBUG("T 3 15/08/52", 70, , "testing")
=XT_API_STATS("maia_dev")
```

---

## 🏗️ Database Strategies by Environment

### Testing Environment
- **Strategy**: Local files
- **Database files**: 
  - `./bonds_data.db`
  - `./validated_quantlib_bonds.db`
  - `./bloomberg_index.db`
- **Updates**: Manual file replacement
- **Performance**: Fastest (local disk)

### Maia Development Environment
- **Strategy**: GCS Dynamic Download
- **Database source**: Google Cloud Storage
- **Updates**: Upload new files to GCS bucket
- **Performance**: Slower cold start, fast warm requests
- **Config**: `app.maia_dev.yaml`

### Production Environment
- **Strategy**: Embedded + GCS Fallback
- **Primary**: Databases baked into container
- **Fallback**: GCS download if embedded missing
- **Updates**: Requires redeployment for embedded, GCS for fallback
- **Performance**: Fastest startup, most reliable
- **Config**: `app.production.yaml`

---

## 🛠️ Alternative Naming Schemes

### Option 1: Descriptive (Recommended)
```excel
=XT_AUTO(A2:A100, B2:B100, , "testing")     // Your local testing
=XT_AUTO(A2:A100, B2:B100, , "maia_dev")    // Maia team testing
=XT_AUTO(A2:A100, B2:B100, , "production")  // Live production
```

### Option 2: Greek Letters
```excel
=XT_AUTO(A2:A100, B2:B100, , "alpha")       // Your testing
=XT_AUTO(A2:A100, B2:B100, , "beta")        // Maia testing
=XT_AUTO(A2:A100, B2:B100, , "production")  // Production
```

Both naming schemes map to the same environments and are fully supported.

---

## 🔍 Troubleshooting by Environment

### Testing Environment Issues
```excel
// Check if local server is running
=XT_HEALTH_CHECK("testing")

// Verify database files exist
ls -la *.db

// Check for port conflicts
lsof -i :8081
```

### Maia Development Issues
```excel
// Check deployment status
=XT_TEST_ENV("maia_dev")

// Verify GCS database access
=XT_API_STATS("maia_dev")

// Check App Engine logs
gcloud app logs tail --service=maia-dev
```

### Production Issues
```excel
// Health check
=XT_HEALTH_CHECK("production")

// Performance check
=XT_API_STATS("production")

// Check recent deployments
gcloud app versions list --service=default
```

---

## 📊 Performance Optimizations

### Array Functions (Recommended)
Use array functions for multiple bonds:
```excel
// Instead of 100 individual calls
=XT_ARRAY(A2:A101, B2:B101, , "maia_dev")  // 1 API call

// Instead of individual functions
=XT_BATCH_PROCESS(A2:A1000, B2:B1000, 100, , "production")  // Batched
```

### Smart Caching
Use intelligent caching for frequently updated data:
```excel
// Only recalculates changed bonds
=XT_SMART(A2:A100, B2:B100, , FALSE, "production")

// Force refresh when needed
=XT_SMART(A2:A100, B2:B100, , TRUE, "maia_dev")
```

### Environment-Specific Optimizations
- **Testing**: Use for debugging, accuracy over speed
- **Maia Dev**: Test performance with realistic data sizes
- **Production**: Optimize for speed and reliability

---

## 🔐 Security & Access Control

### API Keys by Environment
- **Testing**: Uses demo key (local only)
- **Maia Dev**: Uses development key (team access)
- **Production**: Uses production key (live access)

### Database Access
- **Testing**: Local file access only
- **Maia Dev**: GCS bucket access required
- **Production**: Embedded databases, GCS fallback

### Network Access
- **Testing**: Local network only
- **Maia Dev**: HTTPS required, team IP access
- **Production**: HTTPS required, global access

---

## 📈 Monitoring & Observability

### Health Monitoring
```excel
// Environment status dashboard
=XT_ENVIRONMENTS()

// Detailed health checks
=XT_HEALTH_CHECK("testing")
=XT_HEALTH_CHECK("maia_dev") 
=XT_HEALTH_CHECK("production")
```

### Performance Monitoring
```excel
// API usage statistics
=XT_API_STATS("production")

// Cache performance
=XT_CACHE_SIZE()
```

### Error Tracking
All functions include environment-aware error messages:
- "Service temporarily unavailable (Local Testing)"
- "API Error (Maia Development): Connection timeout"
- "Unable to calculate yield (Production)"

---

## 🎯 Best Practices

### Development Workflow
1. **Always test locally first** with `environment = "testing"`
2. **Deploy to maia-dev** for team validation
3. **Only deploy to production** after Maia approval
4. **Use environment parameters** during development
5. **Remove environment parameters** for public release (optional)

### Function Usage
1. **Use XT_AUTO** for most use cases (most flexible)
2. **Use XT_ARRAY** for specific ranges
3. **Use XT_SMART** for frequently updated data
4. **Use environment parameters** for testing

### Performance Guidelines
1. **Array functions** for multiple bonds (much faster)
2. **Batch processing** for large portfolios
3. **Smart caching** for repeated calculations
4. **Environment-specific optimization**

### Error Handling
1. **Test error scenarios** in each environment
2. **Use debug functions** for troubleshooting
3. **Check health status** regularly
4. **Monitor API statistics**

---

## 🚀 Migration from v5.0 to v6.0

### Backward Compatibility
All existing functions continue to work:
```excel
// v5.0 functions still work
=XT_ARRAY(A2:A10, B2:B10)        // Defaults to production
=xt_ytm("T 3 15/08/52", 70)      // Defaults to production
```

### New Features
```excel
// v6.0 multi-environment functions
=XT_ARRAY(A2:A10, B2:B10, , "maia_dev")
=XT_ENVIRONMENTS()
=XT_TEST_ENV("testing")
```

### Precision Improvements
- **Old**: Portfolio functions returned formatted strings ("5.04%")
- **New**: Portfolio functions return raw numbers (5.0449628829956055)
- **Result**: Full institutional-grade precision maintained

---

Perfect for professional bond analytics with enterprise-grade deployment practices! 🎯

**Version 6.0 - Three-Tier Deployment Strategy with Full Precision Support**