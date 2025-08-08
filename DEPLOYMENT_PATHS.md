# All Deployment Paths

## 1. Normal Feature Development Path:
```
┌────────┐    ┌─────────┐    ┌──────────┐    ┌────────────┐
│ Local  │ → │ RMB Dev │ → │ Maia Dev │ → │ Production │
└────────┘    └─────────┘    └──────────┘    └────────────┘
```

## 2. Maia Dev Hotfix Path (Your Use Case):
```
┌────────┐    ┌──────────┐
│ Local  │ → │ Maia Dev │
└────────┘    └──────────┘
   ↓
(Skip RMB Dev when fixing Maia bugs)
```

## 3. Production Hotfix Path:
```
┌────────┐    ┌─────────┐    ┌────────────┐
│ Local  │ → │ Hotfix  │ → │ Production │
└────────┘    └─────────┘    └────────────┘
```

## Real-World Scenarios:

### Scenario 1: You're building a new feature
- Working in RMB Dev on "new-dashboard" feature
- It's 50% complete, lots of debug code
- Maia reports bug in their current version
- **Solution**: Hotfix directly to Maia Dev!

```bash
# Save your work
git stash

# Create hotfix from main
git checkout main
git checkout -b hotfix/maia-date-bug

# Fix the bug
vim bond_calculator.py

# Deploy directly to Maia Dev
./deploy.sh maia-dev
# Answer "y" to "Is this a hotfix?"

# Commit and push
git add -A
git commit -m "Fix date calculation bug in Maia Dev"
git push origin hotfix/maia-date-bug

# Return to your feature
git checkout feature/new-dashboard
git stash pop
```

### Scenario 2: Production emergency
- Users reporting wrong calculations
- Need immediate fix
- **Solution**: Use hotfix environment

```bash
# Create hotfix branch
git checkout main
git checkout -b hotfix/prod-calc-error

# Fix and test locally
# ...

# Deploy to hotfix env for testing
./deploy.sh hotfix

# Test at https://hotfix-dot-future-footing-414610.uc.r.appspot.com

# If good, deploy to production
./deploy.sh production
```

### Scenario 3: Normal feature release
- Feature complete in RMB Dev
- Ready for Maia to test
- **Solution**: Normal flow

```bash
# Deploy from RMB to Maia
./deploy.sh maia-dev
# Answer "n" to "Is this a hotfix?"
# Answer "y" to "Has this been tested in rmb-dev?"
```

## Key Benefits:
1. **Flexibility**: Can fix Maia Dev without contaminating with RMB work
2. **Speed**: Direct path for urgent fixes
3. **Safety**: Normal flow still enforced for features
4. **Clarity**: Version names show deployment type (maia-hotfix-* vs maia-*)

## Remember:
- **Feature branches** → Use normal flow
- **Bug fixes** → Can use hotfix paths
- **Always branch from main** for hotfixes
- **Merge back to main** after hotfixing