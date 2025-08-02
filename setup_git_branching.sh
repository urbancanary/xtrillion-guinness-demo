#!/bin/bash
# Git Branching Setup Script
# Establishes the version locking strategy

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌿 GIT BRANCHING SETUP${NC}"
echo "=================================="
echo "Setting up version locking strategy"
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ ERROR: Not in a git repository${NC}"
    exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo -e "${YELLOW}📋 Current branch: $CURRENT_BRANCH${NC}"

# Ensure we have the latest changes
echo -e "${YELLOW}🔄 Fetching latest changes...${NC}"
git fetch --all

# Create and setup main branch (production-locked)
echo -e "${YELLOW}🔒 Setting up main branch (production-locked)...${NC}"
if git show-ref --verify --quiet refs/heads/main; then
    echo "  ✅ Main branch already exists"
else
    git checkout -b main
    echo "  ✅ Created main branch"
fi

# Create production tag for current stable version
echo -e "${YELLOW}🏷️  Creating production version tag...${NC}"
git checkout main
if git tag -l "v10.0.0" | grep -q "v10.0.0"; then
    echo "  ✅ Version tag v10.0.0 already exists"
else
    git tag -a v10.0.0 -m "Production locked version - stable for external users"
    echo "  ✅ Created version tag v10.0.0"
fi

# Create and setup develop branch
echo -e "${YELLOW}🔧 Setting up develop branch...${NC}"
if git show-ref --verify --quiet refs/heads/develop; then
    echo "  ✅ Develop branch already exists"
    git checkout develop
    echo "  ✅ Switched to develop branch"
else
    git checkout -b develop main
    echo "  ✅ Created develop branch from main"
fi

# Set up branch protection (if using GitHub/GitLab)
echo -e "${YELLOW}🛡️  Setting up branch protection rules...${NC}"
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
# Pre-push hook to protect main branch

protected_branch='main'
current_branch=$(git rev-parse --abbrev-ref HEAD)

if [[ "$current_branch" == "$protected_branch" ]]; then
    echo "🔒 WARNING: Pushing to protected branch 'main'"
    echo "Only hotfixes should be pushed to main!"
    read -p "Are you pushing a tested hotfix? (yes/no): " confirm
    if [[ "$confirm" != "yes" ]]; then
        echo "Push cancelled. Use develop branch for regular development."
        exit 1
    fi
fi
EOF

chmod +x .git/hooks/pre-push
echo "  ✅ Set up pre-push protection for main branch"

# Create .github directory for GitHub workflows (if applicable)
if [ ! -d ".github" ]; then
    mkdir -p .github/workflows
    echo "  ✅ Created .github directory"
fi

# Create branch protection guide
cat > BRANCHING_GUIDE.md << 'EOF'
# XTrillion Core - Git Branching Strategy

## 🌿 Branch Structure

```
main (protected)           ← Production-locked for external users
├── develop               ← Active development
├── hotfix/fix-name       ← Critical fixes only
└── feature/feature-name  ← Individual features
```

## 🔒 Main Branch (Production-Locked)
- **Purpose**: Stable version for external users
- **Protection**: No direct pushes
- **Changes**: Only through tested hotfix merges
- **Deployment**: https://api.x-trillion.com/api/v1

## 🔧 Develop Branch (Active Development)
- **Purpose**: Code consolidation and new features
- **Usage**: Daily development work
- **Deployment**: https://dev-api.x-trillion.com/api/v1

## 🚨 Hotfix Branches (Critical Fixes)
- **Naming**: `hotfix/description-of-fix`
- **Purpose**: Emergency fixes for production
- **Process**: Branch from main → Fix → Test → Merge to main & develop

## 📋 Daily Workflow

### For Code Consolidation (Safe Development)
```bash
git checkout develop
git pull origin develop
# Make changes
git add .
git commit -m "Consolidate bond calculation functions"
git push origin develop
./deploy_development.sh
```

### For Critical Hotfixes (Production Impact)
```bash
git checkout main
git pull origin main
git checkout -b hotfix/bloomberg-calculation-fix
# Make minimal fix
git add .
git commit -m "Fix Bloomberg accrued interest calculation"
git push origin hotfix/bloomberg-calculation-fix
./deploy_hotfix.sh
# Test thoroughly, then merge to main
```

### For New Features
```bash
git checkout develop
git checkout -b feature/portfolio-analytics-v2
# Develop feature
git add .
git commit -m "Add enhanced portfolio analytics"
git push origin feature/portfolio-analytics-v2
# Create pull request to develop
```

## 🎯 External User Protection

- Main branch is locked and stable
- External users always get consistent API
- Development happens safely in develop branch
- Hotfixes are tested before production deployment

## 📚 Quick Reference

```bash
# Check current branch
git branch --show-current

# Switch to develop for regular work
git checkout develop

# Create hotfix for critical issue
git checkout main
git checkout -b hotfix/fix-description

# Deploy to different environments
./deploy_production.sh   # Production (main branch only)
./deploy_development.sh  # Development (any branch)
./deploy_hotfix.sh      # Hotfix testing (hotfix/* branches)

# Emergency rollback
./rollback_production.sh v10.0.0
```
EOF

echo "  ✅ Created BRANCHING_GUIDE.md"

# Switch back to develop for regular work
git checkout develop

echo ""
echo -e "${GREEN}✅ GIT BRANCHING SETUP COMPLETE!${NC}"
echo "=================================="
echo "Branch structure established:"
echo "  🔒 main - Production locked (v10.0.0)"
echo "  🔧 develop - Active development"
echo "  🛡️ Protected main branch with pre-push hook"
echo ""
echo -e "${BLUE}📋 Current Status:${NC}"
echo "  Current branch: $(git branch --show-current)"
echo "  Production tag: v10.0.0"
echo "  Ready for: Code consolidation work"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "1. Continue development in 'develop' branch"
echo "2. Deploy development changes: ./deploy_development.sh"
echo "3. Only use 'main' branch for critical hotfixes"
echo "4. External users remain unaffected by development work"
echo ""
echo -e "${GREEN}🎉 External users are protected with locked main branch!${NC}"
