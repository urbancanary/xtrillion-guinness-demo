# Environment Flow Diagram

## Normal Development Flow:
```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐     ┌────────────┐
│   LOCAL     │ --> │  RMB DEV    │ --> │  MAIA DEV    │ --> │ PRODUCTION │
│ Development │     │ (Andy Only) │     │ (Maia+RMB)   │     │ (Everyone) │
└─────────────┘     └─────────────┘     └──────────────┘     └────────────┘
     ↓                    ↓                     ↓                    ↓
  You Code          Experiment            Maia Tests           Live Users
                    Break Things          Integration          Must Work!
                    Debug Mode            Pre-Prod             No Debug
```

## Emergency Hotfix Flow:
```
┌─────────────┐     ┌─────────────┐     ┌────────────┐
│   LOCAL     │ --> │   HOTFIX    │ --> │ PRODUCTION │
│   Fix Bug   │     │ Prod Mirror │     │   Live     │
└─────────────┘     └─────────────┘     └────────────┘
     ↓                    ↓                    ↓
  Quick Fix         Test Carefully        Deploy Fast
                    Prod Settings         Skip Stages
```

## Service URLs:

**RMB Dev**: `https://rmb-dev-dot-future-footing-414610.uc.r.appspot.com`
- Your personal sandbox
- Can deploy anytime
- Break things freely
- Test wild ideas

**Maia Dev**: `https://maia-dev-dot-future-footing-414610.uc.r.appspot.com`
- Shared with Maia
- Should be stable
- Integration testing
- Pre-production validation

**Hotfix**: `https://hotfix-dot-future-footing-414610.uc.r.appspot.com`
- Emergency fixes only
- Production mirror
- Skip normal flow
- Use sparingly!

**Production**: `https://future-footing-414610.uc.r.appspot.com`
- Live environment
- External users
- Must be stable
- No direct deploys!

## When to Use Each:

### Use RMB Dev when:
- Trying new features
- Testing breaking changes
- Experimenting with APIs
- Personal development

### Use Maia Dev when:
- Feature is stable in RMB Dev
- Ready for Maia to test
- Need integration testing
- Preparing for production

### Use Hotfix when:
- Production is broken
- Critical bug found
- Can't wait for normal flow
- CEO is calling!

### Deploy to Production when:
- Maia Dev fully tested
- Maia team approves
- All tests passing
- Ready for users

## Remember:
1. **Normal flow**: Local → RMB → Maia → Prod
2. **Emergency only**: Local → Hotfix → Prod
3. **Never**: Local → Prod (what I did wrong!)
4. **Always**: Test before promoting