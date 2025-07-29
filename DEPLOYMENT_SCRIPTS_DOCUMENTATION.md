# 🌸 **Google Analysis 10 - Deployment Scripts Documentation**

**Definitive Guide for Bond Analytics API Deployment & Testing**

---

## 📋 **Script Overview**

This is the **definitive documentation** for all deployment and testing scripts in Google Analysis 10.

| Script | Purpose | Quick Start Guide |
|--------|---------|-------------------|
| **`local_container_setup.sh`** | ✨ **LOCAL TESTING** | `LOCAL_CONTAINER_TESTING_README.md` |
| **`test_local_portfolio.py`** | 🧪 **PORTFOLIO TESTING** | `LOCAL_CONTAINER_TESTING_README.md` |
| **`deploy_appengine_fixed.sh`** | 🚀 **PRODUCTION DEPLOYMENT** | `PRODUCTION_DEPLOYMENT_README.md` |
| **`show_script_reference.sh`** | 🔍 **SCRIPT STATUS** | Run directly for current status |

---

## 🎯 **Documentation Hierarchy**

### **📋 This File (Definitive Documentation)**
- **`DEPLOYMENT_SCRIPTS_DOCUMENTATION.md`** ← **YOU ARE HERE**
- Authoritative source for all deployment information
- References all other relevant documentation

### **⚡ Quick Start Guides (Immediate Instructions)**
- **`LOCAL_CONTAINER_TESTING_README.md`** - Exactly which commands for local testing
- **`PRODUCTION_DEPLOYMENT_README.md`** - Exactly which commands for production

### **📖 Supporting Documentation (Detailed References)**
- **`API_SPECIFICATION_LATEST_FORMATTED.md`** - Complete API documentation
- **`api_spec_developer.md`** - Developer-focused API guide
- **`DEPLOYMENT_ARCHITECTURE.md`** - System architecture overview
- **`README.md`** - General project information

---

## 🔧 **Local Development Scripts**

### **`local_container_setup.sh` ✨ (LOCAL TESTING)**

**Purpose**: Run exact production API locally using Podman container
**Safety**: ✅ **SAFE** - Only affects your local machine
**Use Case**: 
- Daily development and testing
- Validate portfolio calculations
- Debug issues without affecting production

**Quick Start**: See `LOCAL_CONTAINER_TESTING_README.md`

**Commands**:
```bash
./local_container_setup.sh start     # Build and start local API
./local_container_setup.sh status    # Check if running
./local_container_setup.sh test      # Test API endpoints
./local_container_setup.sh logs      # View container logs
./local_container_setup.sh stop      # Stop container
./local_container_setup.sh restart   # Rebuild and restart
```

### **`test_local_portfolio.py` 🧪 (PORTFOLIO TESTING)**

**Purpose**: Test your 25-bond portfolio against local container API
**Safety**: ✅ **SAFE** - Tests against local container only
**Use Case**:
- Validate your portfolio data
- Check calculation success rates
- Verify expected yields and durations

**Prerequisites**: Local container must be running
**Usage**: `python3 test_local_portfolio.py`

---

## 🚀 **Production Deployment Scripts**

### **`deploy_appengine_fixed.sh` 🚀 (PRODUCTION DEPLOYMENT)**

**Purpose**: Deploy to live Google App Engine API
**Safety**: ⚠️ **CAREFUL** - Affects production API used by others
**Use Case**: Deploy tested updates to live environment

**Quick Start**: See `PRODUCTION_DEPLOYMENT_README.md`

**Safety Checklist**:
- ✅ Local tests pass completely
- ✅ Local container testing successful
- ✅ Ready for production deployment

---

## 🗑️ **Legacy/Archive Scripts**

### **Scripts to Archive**
- **`deploy_appengine.sh`** - Superseded by "fixed" version

---

## 🎯 **Recommended Workflows**

### **Daily Development (Safe)**
1. **Start local environment**: See `LOCAL_CONTAINER_TESTING_README.md`
2. **Test your portfolio**: Use portfolio testing script
3. **Iterate**: Make changes, test locally
4. **Stop when done**: Clean up local environment

### **Production Deployment (When Ready)**
1. **Validate locally**: Ensure all tests pass
2. **Deploy**: See `PRODUCTION_DEPLOYMENT_README.md`
3. **Verify**: Test production API endpoints

---

## 🔒 **Safety Guidelines**

### **Local Scripts (Always Safe)**
- `local_container_setup.sh` - Only affects local machine
- `test_local_portfolio.py` - Only tests local container
- Safe to run anytime for development and testing

### **Production Scripts (Use With Caution)**
- `deploy_appengine_fixed.sh` - Deploys to live API
- **Always test locally first** before production deployment
- Affects API used by external clients

---

## 🗂️ **File Organization**

### **Active Scripts (Keep in Root)**
- ✅ `local_container_setup.sh` - Local testing
- ✅ `test_local_portfolio.py` - Portfolio testing  
- ✅ `deploy_appengine_fixed.sh` - Production deployment
- ✅ `show_script_reference.sh` - Status checker

### **Active Documentation (Keep in Root)**
- ✅ `DEPLOYMENT_SCRIPTS_DOCUMENTATION.md` - This file
- ✅ `LOCAL_CONTAINER_TESTING_README.md` - Local quick start
- ✅ `PRODUCTION_DEPLOYMENT_README.md` - Production quick start
- ✅ `API_SPECIFICATION_LATEST_FORMATTED.md` - API reference
- ✅ `api_spec_developer.md` - Developer API guide
- ✅ `DEPLOYMENT_ARCHITECTURE.md` - Architecture overview
- ✅ `README.md` - General project info

### **Historical Documents (Archive)**
All timestamped reports, completed plans, and legacy documentation should be moved to `archive/` directory.

---

## 📊 **Expected Results**

### **Local Container Testing**
- **API Base**: http://localhost:8080
- **Portfolio Success Rate**: >90%
- **Portfolio Yield**: ~5-7% (emerging market bonds)
- **Portfolio Duration**: ~8-12 years

### **Production Deployment**
- **API Base**: https://future-footing-414610.uc.r.appspot.com
- **Health Check**: Should return "healthy" status
- **Same Results**: Identical to local testing

---

## 🐛 **Troubleshooting**

### **Local Container Issues**
See `LOCAL_CONTAINER_TESTING_README.md` for detailed troubleshooting

### **Production Deployment Issues**  
See `PRODUCTION_DEPLOYMENT_README.md` for deployment troubleshooting

### **Quick Script Status**
```bash
./show_script_reference.sh    # Shows current status of all scripts
```

---

## 📞 **Getting Help**

1. **Immediate instructions**: Check appropriate `*_README.md` file
2. **API questions**: See `API_SPECIFICATION_LATEST_FORMATTED.md`
3. **Architecture questions**: See `DEPLOYMENT_ARCHITECTURE.md`
4. **Developer API info**: See `api_spec_developer.md`
5. **Script status**: Run `./show_script_reference.sh`

---

## 🎉 **Success Criteria**

Your deployment system is working correctly when:
- ✅ **Local container** starts and responds to health checks
- ✅ **Portfolio testing** achieves >90% success rate
- ✅ **Production deployment** completes without errors
- ✅ **Live API** responds correctly to test requests
- ✅ **Documentation** is clear and up-to-date

---

**📋 This is the definitive documentation for Google Analysis 10 deployment scripts.**

**🎯 For immediate instructions, see the appropriate `*_README.md` file.**
