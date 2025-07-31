# 📖 Claude Code Instructions - API Fixes

## 🚀 Quick Start for Claude Code

### **What to Do:**
1. **Read the task document:** `CLAUDE_CODE_API_FIXES.md`
2. **Follow the tasks in order:** Task 1 → Task 2 → Task 3 → Task 4 → Final Validation
3. **Check off boxes** as you complete each step
4. **Test after each task** using the provided commands

### **Command to Get Started:**
```bash
cd /Users/andyseaman/Notebooks/json_receiver_project/google_analysis10
cat CLAUDE_CODE_API_FIXES.md
```

---

## 📋 **Task Summary (Read Full Details in CLAUDE_CODE_API_FIXES.md)**

### **Task 1: Fix Empty Portfolio Validation** ⏱️ 5 min
- **Problem:** Empty portfolio returns 200, should return 400
- **File:** `google_analysis10_api.py` 
- **Action:** Add validation after `data = request.get_json()`
- **Test:** `curl -d '{"data": []}' → should return 400`

### **Task 2: Fix Field Name Inconsistencies** ⏱️ 15 min  
- **Problem:** Field names don't match specification 
- **File:** `google_analysis10_api.py`
- **Action:** Update `raw_analytics` and `field_descriptions` sections
- **Test:** Response should include `duration_annual` field

### **Task 3: Add Portfolio Metrics Aggregation** ⏱️ 30 min
- **Problem:** Missing portfolio-level metrics from specification
- **File:** `google_analysis10_api.py`
- **Action:** Add `calculate_portfolio_metrics()` function and use it
- **Test:** Response should include `portfolio_metrics` object

### **Task 4: Update Documentation** ⏱️ 10 min
- **Problem:** Test scripts default to offline URL
- **Files:** Test scripts and documentation
- **Action:** Update default URLs to localhost
- **Test:** Scripts should run without URL errors

---

## ✅ **Success Criteria**

### **Before Fixes:**
- 95.5% API test success rate (21/22 tests)
- 3 specification compliance issues

### **After Fixes (Target):**  
- 98%+ API test success rate (22/22 tests)
- 100% specification compliance
- All documented examples working perfectly

### **Final Validation Commands:**
```bash
# Should show 100% success
python3 validate_specification_examples.py

# Should show 98%+ success rate  
python3 test_api_specification_systematically.py local
```

---

## 🎯 **For Claude Code: Step-by-Step Process**

1. **Open the main task file:**
   ```bash
   code CLAUDE_CODE_API_FIXES.md
   # or
   cat CLAUDE_CODE_API_FIXES.md
   ```

2. **Start with Task 1** (quickest win - 5 minutes)
3. **Check off boxes [ ]** → `[x]` as you complete steps  
4. **Test each fix** before moving to next task
5. **Add notes** about any issues in the "Notes" sections
6. **Run final validation** when all tasks complete

### **Key File to Modify:**
- **Main File:** `/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/google_analysis10_api.py`
- **Search Patterns:** Use the search terms provided in each task
- **Backup Recommended:** Consider copying the file before making changes

### **Expected Total Time:** ~1 hour for all fixes

---

## 🆘 **If You Need Help**

### **Check These First:**
1. **API still running?** `curl http://localhost:8080/health`
2. **Syntax errors?** Check the API console for error messages
3. **Test commands working?** Try the simple curl examples first

### **Progress Tracking:**
- Use the checkboxes in `CLAUDE_CODE_API_FIXES.md` to track progress
- Update the "Progress Tracking" section at the bottom
- Note any issues in the "Notes" sections

---

**🎯 Goal: Fix 4 API issues to achieve 98%+ specification compliance**

**📖 Full Instructions: Read `CLAUDE_CODE_API_FIXES.md` for complete details**
