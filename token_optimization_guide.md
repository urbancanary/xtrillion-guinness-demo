# Token Optimization Guide for Claude Code

## 🎯 Quick Wins (Immediate 50-80% Reduction)

### 1. **Use Grep Before Read**
```bash
# ❌ BAD: Reading entire files
claude: Read the google_analysis10_api.py file

# ✅ GOOD: Search first, read specific sections
claude: Search for "calculate_bond" in the codebase
claude: Show me lines 100-150 of google_analysis10_api.py
```

### 2. **Target Specific Directories**
```bash
# ❌ BAD: Scanning entire project
python3 code_duplication_agent.py --scan

# ✅ GOOD: Target specific areas
python3 code_duplication_agent.py --scan --dir ./src
python3 orphaned_code_agent.py --scan --pattern "*test*.py"
```

### 3. **Use Quick Modes**
```bash
# For rapid checks (when implemented)
python3 doc_maintenance_agent.py --quick
python3 code_duplication_agent.py --quick --top 5
```

## 📊 Token Usage by Operation

| Operation | Tokens (Approx) | Optimization |
|-----------|----------------|--------------|
| Read large file (1500 lines) | 3,000-5,000 | Use grep first, read sections |
| Full project scan (400 files) | 50,000-100,000 | Target specific directories |
| Agent Task execution | 10,000-30,000 | Run less frequently |
| Creating new files | 1,000-3,000 | Update existing when possible |

## 🔧 Optimized Agent Commands

### **Documentation Agent (Lowest Token Use)**
```bash
# Check specific endpoint only
python3 doc_maintenance_agent.py --endpoint "/api/v1/bond/analysis"

# Validate without fixing
python3 doc_maintenance_agent.py --check --no-update
```

### **Duplication Agent (Medium Token Use)**  
```bash
# Scan only Python files in src
python3 code_duplication_agent.py --quick --pattern "*.py" --dir ./src

# Find top 5 duplications only
python3 code_duplication_agent.py --top 5
```

### **Orphaned Code Agent (Highest Token Use)**
```bash
# Check only files older than 90 days
python3 orphaned_code_agent.py --days 90

# Skip import analysis (faster)
python3 orphaned_code_agent.py --skip-imports
```

## 💡 Claude Code Best Practices

### **1. Batch Operations**
```bash
# ❌ BAD: Multiple separate commands
claude: Read file1.py
claude: Read file2.py  
claude: Read file3.py

# ✅ GOOD: Single focused request
claude: Show me the calculate_bond functions in file1.py, file2.py, and file3.py
```

### **2. Use Search Strategically**
```bash
# Find patterns without reading files
claude: How many files contain "calculate_bond"?
claude: List files with "test_" prefix
```

### **3. Incremental Analysis**
```bash
# Start small, expand if needed
1. Quick scan for obvious issues
2. Deep dive only on problem areas
3. Full scan only when necessary
```

## 📅 Efficient Scheduling

### **Daily (Low Token)**
- Quick doc validation (API examples only)
- Check for new orphaned test files

### **Weekly (Medium Token)**  
- Duplication scan on changed files only
- Orphaned code quick scan

### **Monthly (High Token)**
- Full comprehensive scans
- Deep dependency analysis
- Complete documentation validation

## 🚀 Advanced Optimizations

### **1. Caching Results**
```python
# Add to agents
--use-cache          # Reuse results from last run
--cache-duration 7   # Cache valid for 7 days
```

### **2. Incremental Scanning**
```python
# Only scan files changed since last run
--since-last-run
--git-changes-only
```

### **3. Sampling Strategy**
```python
# Scan representative sample
--sample-rate 0.1    # Check 10% of files
--confidence 0.95    # Statistical confidence
```

## 📈 Token Estimation Formula

```
Tokens ≈ (Files × AvgLinesPerFile × 2) + (Operations × 100)

Example:
- 100 files × 200 lines × 2 = 40,000 tokens
- Plus 50 operations × 100 = 5,000 tokens
- Total: ~45,000 tokens per full scan
```

## 🎯 80/20 Rule for Agents

**Focus 80% effort on:**
1. Changed files only
2. Specific problem areas
3. Quick validation checks

**Reserve 20% for:**
1. Monthly deep scans
2. Comprehensive analysis
3. New pattern detection

## 💰 ROI Calculation

```
Manual code review: 4 hours × $100/hr = $400
Agent scan tokens: 50,000 × $0.00002 = $1
ROI: 400:1

Break-even: Even at 100x token use, still valuable!
```