# 🚀 **Production Deployment - Quick Start**

## ⚡ **EXACTLY What To Run**

### **⚠️ IMPORTANT: Test Locally First**
```bash
# ALWAYS test locally before production deployment
./local_container_setup.sh start
python3 test_local_portfolio.py
./local_container_setup.sh stop
```

### **🚀 Deploy to Production**
```bash
# Only run when local tests pass
./deploy_appengine_fixed.sh
```

---

## 🎯 **Production Commands**

| Command | Purpose | Safety |
|---------|---------|--------|
| `./deploy_appengine_fixed.sh` | **Deploy to live API** | ⚠️ **Production** |
| `curl https://future-footing-414610.uc.r.appspot.com/health` | **Check production health** | ✅ **Safe** |

---

## 🔍 **Verification Steps**

```bash
# 1. Check deployment succeeded
curl https://future-footing-414610.uc.r.appspot.com/health

# 2. Test individual bond
curl -X POST "https://future-footing-414610.uc.r.appspot.com/api/v1/bond/parse-and-calculate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_demo_3j5h8m9k2p6r4t7w1q" \
  -d '{"description": "T 4.625 02/15/25", "price": 99.5}'

# 3. Test portfolio (optional)
# Use your portfolio testing script but change URL to production
```

---

## 🔒 **Safety Checklist**

- ✅ **Local tests pass** - All bonds calculate successfully
- ✅ **Local container works** - No database or path issues  
- ✅ **Ready for production** - Changes are tested and validated
- ✅ **Have backup plan** - Know how to rollback if needed

---

## 🐛 **If Deployment Fails**

```bash
# Check gcloud authentication
gcloud auth list

# Check project setting
gcloud config get-value project

# View deployment logs
gcloud app logs tail -s default

# Rollback if needed (check gcloud app versions list first)
gcloud app versions list
```

---

## 📋 **Prerequisites**

- **Google Cloud SDK**: Must be installed and authenticated
- **Project Access**: future-footing-414610 permissions
- **Local Testing**: Must pass before deployment

---

**🎯 For detailed information, see: `documentation.md`**
