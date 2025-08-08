# Google Analysis 10 - Complete Environment Strategy

## How the Environment Pipeline Works

### Normal Development Flow:
```
Local Development → RMB Dev → Maia Dev → Production
```

### Emergency Hotfix Flow:
```
Local Fix → Hotfix Environment → Production (with approval)
```

## All Environments:

### 1. **Production** (default service)
- **URL**: https://future-footing-414610.uc.r.appspot.com
- **Purpose**: Live production environment
- **Access**: Maia + External users
- **When to use**: Only after thorough testing
- **Config**: app.yaml or app.production.yaml

### 2. **Maia Dev** (maia-dev service)
- **URL**: https://maia-dev-dot-future-footing-414610.uc.r.appspot.com
- **Purpose**: Stable development for Maia
- **Access**: Maia developers + RMB team
- **When to use**: After RMB dev testing succeeds
- **Config**: app.maia-dev.yaml

### 3. **RMB Dev** (rmb-dev service)
- **URL**: https://rmb-dev-dot-future-footing-414610.uc.r.appspot.com
- **Purpose**: Andy's experimental environment
- **Access**: RMB team only
- **When to use**: For all new features and experiments
- **Config**: app.rmb-dev.yaml

### 4. **Hotfix** (hotfix service)
- **URL**: https://hotfix-dot-future-footing-414610.uc.r.appspot.com
- **Purpose**: Emergency fixes that bypass normal flow
- **Access**: RMB team only
- **When to use**: Critical production bugs only
- **Config**: app.hotfix.yaml
- **Special**: Uses production-like settings for accurate testing

### 5. **Development** (development service) - DEPRECATED
- Currently has deployment issues
- Will be replaced by rmb-dev and maia-dev

## How It Works:

### Normal Feature Development:
1. Develop locally
2. Deploy to **rmb-dev** for experimentation
3. Once stable, deploy to **maia-dev** for Maia to test
4. After Maia approves, deploy to **production**

### Emergency Hotfix Process:
1. Identify critical bug in production
2. Fix locally with minimal changes
3. Deploy to **hotfix** environment
4. Test thoroughly (hotfix mimics production)
5. If tests pass, deploy directly to **production**
6. Later, backport fix through normal flow

### Key Differences:

**RMB Dev**:
- Experimental features allowed
- Can break things
- Minimal resources (scales to 0)
- Debug mode enabled
- Your personal playground

**Maia Dev**:
- Stable features only
- Should not break
- Moderate resources
- Debug mode disabled
- Shared with Maia team

**Hotfix**:
- Production-identical settings
- Only for critical fixes
- Full production resources
- No experimental features
- Direct path to production

## Current Status:
- ✅ Production: Working
- ❌ Development: Has skip_files error
- ❌ RMB Dev: Not deployed yet (skip_files error)
- ❌ Maia Dev: Not deployed yet
- ❓ Hotfix: Not tested recently

## Deployment Commands:

### Normal deployment:
```bash
./deploy.sh rmb-dev      # Your experiments
./deploy.sh maia-dev     # For Maia testing
./deploy.sh production   # Final deployment (requires confirmations)
```

### Emergency hotfix:
```bash
# Deploy to hotfix environment
gcloud app deploy app.hotfix.yaml --version=hotfix-$(date +%Y%m%d-%H%M%S)

# If successful, deploy to production
gcloud app deploy app.yaml --version=prod-hotfix-$(date +%Y%m%d-%H%M%S)
```

### Rollback if needed:
```bash
./rollback.sh production  # Emergency rollback
./rollback.sh maia-dev   # Rollback Maia dev
./rollback.sh rmb-dev    # Rollback your dev
```

## Important Notes:
1. **Never skip stages** except for hotfixes
2. **Always test** before promoting
3. **Document hotfixes** - they bypass normal review
4. **Communicate** with Maia before their deployments
5. **Monitor** after production deployments