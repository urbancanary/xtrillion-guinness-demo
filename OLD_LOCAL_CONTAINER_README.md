# 🌸 **Local Container Testing - Quick Start**

## ⚡ **EXACTLY What To Run**

### **1. Start Local API Container**
```bash
cd /Users/andyseaman/Notebooks/json_receiver_project/google_analysis10
./local_container_setup.sh start
```

### **2. Test Your Portfolio**
```bash
python3 test_local_portfolio.py
```

### **3. Stop When Done**
```bash
./local_container_setup.sh stop
```

---

## 🎯 **Script Commands**

| Command | Purpose |
|---------|---------|
| `./local_container_setup.sh start` | **Build and start** local API |
| `./local_container_setup.sh status` | **Check** if running |
| `./local_container_setup.sh test` | **Test** API endpoints |
| `./local_container_setup.sh logs` | **View** container logs |
| `./local_container_setup.sh stop` | **Stop** container |
| `./local_container_setup.sh restart` | **Rebuild** and restart |

---

## 🧪 **Portfolio Testing**

```bash
# Interactive testing (choose what to test)
python3 test_local_portfolio.py

# Quick API test
curl http://localhost:8080/health
```

---

## 🔧 **Expected Results**

- **Local API**: http://localhost:8080
- **Portfolio Success Rate**: >90%
- **Portfolio Yield**: ~5-7% (EM bonds)
- **Portfolio Duration**: ~8-12 years

---

## 🐛 **If Something Fails**

```bash
# Check status
./local_container_setup.sh status

# View logs
./local_container_setup.sh logs

# Restart everything
./local_container_setup.sh restart
```

---

## 📋 **Prerequisites**

- **Podman**: Auto-installed via Homebrew if missing
- **Python 3**: For portfolio testing script
- **curl/jq**: For API testing (optional)

---

**🎯 For detailed information, see: `documentation.md`**
