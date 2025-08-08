# Hotfix Strategy - Multi-Environment

## The Problem You Identified:
Sometimes Maia Dev needs a quick fix while you're still working on new features in RMB Dev. You don't want to push your half-finished RMB Dev work to Maia Dev just to fix a small bug.

## Solution: Environment-Specific Hotfixes

### Hotfix Flows:

#### 1. Production Hotfix (Critical):
```
Local Fix → Hotfix Environment → Production
```

#### 2. Maia Dev Hotfix (Common):
```
Local Fix → Direct to Maia Dev (skip RMB Dev)
```

#### 3. RMB Dev Hotfix (Rare):
```
Local Fix → Direct to RMB Dev
```

## When to Use Each:

### Maia Dev Hotfix:
- Maia found a bug in their testing
- You're working on new features in RMB Dev
- The fix is small and isolated
- You don't want to pollute the fix with unfinished RMB work

### Production Hotfix:
- Critical bug affecting users
- Needs production-like testing
- Must be deployed ASAP
- CEO/customers complaining

## How to Execute:

### For Maia Dev Hotfix:
```bash
# 1. Create a clean branch from main (not from your feature branch!)
git checkout main
git pull origin main
git checkout -b hotfix/maia-dev-fix-description

# 2. Make the minimal fix
# edit files...

# 3. Deploy directly to Maia Dev
gcloud app deploy app.maia-dev.yaml --version=maia-hotfix-$(date +%Y%m%d-%H%M%S)

# 4. Test in Maia Dev
# If good, merge to main

# 5. Later, merge main back to your feature branch
git checkout feature/your-current-work
git merge main
```

### For Production Hotfix:
```bash
# 1. Create hotfix branch from main
git checkout main
git pull origin main  
git checkout -b hotfix/prod-critical-fix

# 2. Make fix and test locally

# 3. Deploy to hotfix environment
gcloud app deploy app.hotfix.yaml --version=hotfix-$(date +%Y%m%d-%H%M%S)

# 4. Test in hotfix environment

# 5. If tests pass, deploy to production
gcloud app deploy app.yaml --version=prod-hotfix-$(date +%Y%m%d-%H%M%S)

# 6. Immediately merge to main and tag
git checkout main
git merge hotfix/prod-critical-fix
git tag -a "hotfix-v1.0.1" -m "Emergency fix for XYZ"
git push origin main --tags
```

## Updated Environment Purposes:

### RMB Dev:
- Your feature development
- Experimental changes
- Can be broken/incomplete

### Maia Dev:
- Stable features for Maia
- **Can receive hotfixes directly**
- Should generally work

### Hotfix Environment:
- Production mirror
- Test production hotfixes
- Not for Maia Dev fixes

### Production:
- Live environment
- Only tested code
- Hotfixes must go through hotfix env first

## Key Insight:
You're right - we need flexibility to fix Maia Dev without pushing incomplete RMB Dev work. The solution is to:
1. Always branch from main for hotfixes
2. Deploy directly to the target environment
3. Skip intermediate environments when appropriate
4. Merge back to main immediately
5. Sync your feature branch with main later