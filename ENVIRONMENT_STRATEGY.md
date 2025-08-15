# Google Analysis 10 - Environment Strategy

## 3-Stage Development Pipeline

### 1. **Production** (default service)
- **URL**: https://future-footing-414610.uc.r.appspot.com
- **Purpose**: Live production environment for external users
- **Access**: Maia + External users
- **Deployment**: Only after thorough testing in maia-dev
- **Config**: app.production.yaml (or app.yaml for default)
- **Rules**: 
  - NO direct deployments without testing
  - Only deploy from maia-dev after verification
  - Requires explicit approval

### 2. **Maia Dev** (maia-dev service)
- **URL**: https://maia-dev-dot-future-footing-414610.uc.r.appspot.com
- **Purpose**: Development environment for Maia software company
- **Access**: Maia developers + RMB team
- **Deployment**: After testing in rmb-dev
- **Config**: app.maia-dev.yaml
- **Features**:
  - Stable development environment
  - Integration testing
  - Pre-production validation

### 3. **RMB Dev** (rmb-dev service)
- **URL**: https://rmb-dev-dot-future-footing-414610.uc.r.appspot.com
- **Purpose**: Andy's experimental development environment
- **Access**: RMB team only
- **Deployment**: Direct from local development
- **Config**: app.rmb-dev.yaml
- **Features**:
  - Rapid experimentation
  - Breaking changes allowed
  - Test new features before Maia

## Deployment Flow:
```
Local Development → RMB Dev → Maia Dev → Production
```

## Key Rules:
1. **NEVER deploy directly to production**
2. All changes must flow through the pipeline
3. Each stage must be verified before promoting
4. Production deployments require explicit approval
5. Rollback strategy for each environment

## Current Issues to Fix:
1. Development service has skip_files error
2. Need to create maia-dev and rmb-dev services
3. Need separate yaml configs for each environment
4. Need to set up proper access controls