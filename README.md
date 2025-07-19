# 🏦 Google Analysis9 - Institutional Bond Analytics

Advanced bond analytics system with QuantLib integration and Bloomberg-level accuracy.

## 🚨 **DEPLOYMENT AUTHORITY - READ THIS FIRST**
**📋 [CORRECT DEPLOYMENT FACTS - FINAL AUTHORITY](🚨_CORRECT_DEPLOYMENT_FACTS_FINAL.md)**

**🚀 One Command Deployment:**
```bash
cd /Users/andyseaman/Notebooks/json_receiver_project/google_analysis10
./env_manager_ga9.sh deploy prod
```

**⚠️ STOP creating new deployment code - use existing working patterns!**

## 🎯 Current Status: 85.5% PASS Rate Achieved

**Latest Validation Results:**
- **Total Bonds:** 12,343 in `all_bonds_calculations` table
- **PASS:** 10,548 bonds (85.5%) with ≤ 0.01 per million tolerance
- **FAIL:** 1,795 bonds (14.5%) exceeding 0.01 tolerance
- **Database:** `bloomberg_index.db` 
- **Last Updated:** July 12, 2025

## ✨ Key Features

### 🔬 Advanced Bond Analytics
- **Binary PASS/FAIL validation** with 0.01 per million tolerance
- **QuantLib Integration** with proper bond convention handling
- **Bloomberg comparison** for institutional-grade accuracy
- **Accrued Interest calculations** using 30/360 day count
- **Settlement Date:** 2025-04-18 (standardized)

### 📊 Database Architecture
- **all_bonds_calculations**: 12,343 bonds with Bloomberg vs QuantLib comparison
- **validated_calculations**: Additional validation dataset
- **pemex_calculations**: 19 PEMEX bonds for specialized analysis
- **validated_quantlib_bonds**: Bond convention reference data

### 🚀 Production Features
- **RESTful API** with comprehensive endpoints
- **Streamlit Dashboard** for interactive analysis
- **Docker containerization** for easy deployment
- **Binary status system** (PASS/FAIL only, no grades)

## 🏗️ Calculation Loop Architecture

### Core Calculation Process

The system uses `bbg_quantlib_calculations.py` as the main orchestrator:

```python
def calculate_comprehensive_enhanced(table_name, include_ytw_oad=True, include_pass_fail=True):
    """
    ENHANCED COMPREHENSIVE CALCULATION - The Complete Loop
    """
    # Step 0: Dynamic missing data detection and population
    # Step 1: Ensure all required columns exist
    # Step 2: Populate settlement_date (2025-04-18)
    # Step 3: Calculate bb_mkt_accrued using market value formula
    # Step 4: Calculate bloomberg_accrued (per million format)
    # Step 5: Calculate QuantLib accrued using bond_calculation_registry
    # Step 6: Calculate YTW and OAD (optional)
    # Step 7: Calculate differences (Bloomberg - QuantLib)
    # Step 8: Binary PASS/FAIL status (≤ 0.01 = PASS, > 0.01 = FAIL)
```

### Bond Calculation Registry

Central calculation function located in `calculators/bond_calculation_registry.py`:

```python
def get_working_accrued_calculation():
    """
    THE WORKING ACCRUED INTEREST CALCULATION
    
    Status: ✅ TESTED - 85.5% accuracy vs Bloomberg
    Settlement: 2025-04-18
    Convention: 30/360 Bond Basis, Unadjusted, Semiannual
    
    Returns function that calculates accrued interest per $1M
    """
```

### Calculation Flow

1. **Bloomberg Accrued Formula:**
   ```python
   bb_mkt_accrued = mv_usd - (par_val * price / 100)
   bloomberg_accrued = (bb_mkt_accrued / par_val) * 1,000,000
   ```

2. **QuantLib Calculation:**
   ```python
   # Uses bond_calculation_registry.get_working_accrued_calculation()
   # 30/360 day count, semiannual frequency, unadjusted calendar
   quantlib_accrued = calc_func(isin, coupon, maturity, '2025-04-18')
   ```

3. **Binary Status Decision:**
   ```python
   status = 'PASS' if abs(bloomberg_accrued - quantlib_accrued) <= 0.01 else 'FAIL'
   ```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- QuantLib
- Required dependencies: `pip install -r requirements.txt`

### Run Current Calculations
```bash
# Navigate to project directory
cd /Users/andyseaman/Notebooks/json_receiver_project/google_analysis9

# Run comprehensive calculations on all bonds
python3 -c "
from bbg_quantlib_calculations import calculate_comprehensive_enhanced
result = calculate_comprehensive_enhanced('all_bonds_calculations')
"

# Start the API server
python3 google_analysis9_api.py

# Start the Streamlit dashboard
streamlit run streamlit_demo.py
```

### Check Current Status
```bash
# Check current PASS/FAIL counts
python3 -c "
import sqlite3
conn = sqlite3.connect('bloomberg_index.db')
cursor = conn.cursor()
cursor.execute('SELECT status, COUNT(*) FROM all_bonds_calculations GROUP BY status')
for status, count in cursor.fetchall():
    print(f'{status}: {count}')
conn.close()
"
```

## 📋 Current API Endpoints

### Bond Analysis
- `POST /api/v1/portfolio/analyze` - Portfolio analysis with binary PASS/FAIL
- `GET /api/v1/bonds/{isin}` - Individual bond analytics
- `POST /api/v1/bonds/calculate` - Custom bond calculations

### Health & Status
- `GET /health` - Service health check
- `GET /api/v1/status` - System status with PASS/FAIL counts

## 🔬 Technical Implementation

### Binary Status System
**Strict 0.01 per million tolerance - NO EXCEPTIONS**

```sql
UPDATE all_bonds_calculations 
SET status = CASE 
  WHEN bloomberg_accrued IS NOT NULL 
   AND quantlib_accrued IS NOT NULL 
   AND quantlib_accrued > 0
   AND ABS(bloomberg_accrued - quantlib_accrued) <= 0.01 THEN 'PASS'
  ELSE 'FAIL'
END
```

### Key Files and Functions

1. **Main Orchestrator:** `bbg_quantlib_calculations.py`
   - `calculate_comprehensive_enhanced()` - Complete calculation loop

2. **Calculation Engine:** `calculators/bond_calculation_registry.py`
   - `get_working_accrued_calculation()` - QuantLib calculation function

3. **Database:** `bloomberg_index.db`
   - `all_bonds_calculations` table - Main dataset with PASS/FAIL status

### Current Results Analysis

**PASS Bonds (10,548):**
- Perfect or near-perfect Bloomberg matches
- ≤ 0.01 per million difference
- Institutional-grade accuracy achieved

**FAIL Bonds (1,795):**
- > 0.01 per million difference
- Require investigation and fixes
- 14.5% of total dataset

## 🛠️ Recent Bug Fixes

### Function Reference Bug (Fixed)
**Issue:** `bond_calculation_registry.py` line 184 was calling function instead of referencing it:
```python
# ❌ BROKEN - Calls function immediately
'function': get_working_accrued_calculation(),

# ✅ FIXED - Stores function reference
'function': get_working_accrued_calculation,
```

**Result:** Fixed 99.5% calculation failures, achieved 85.5% PASS rate.

### Status Column Standardization (Fixed)
**Issue:** Multiple status variants (PASS_EXCELLENT, PASS_GOOD, PASS_ACCEPTABLE)
**Fix:** Binary PASS/FAIL only based on 0.01 tolerance

## 📊 Validation Results

### Current Performance (July 12, 2025)
- **Total Bonds:** 12,343
- **PASS Rate:** 85.5% (10,548 bonds)
- **FAIL Rate:** 14.5% (1,795 bonds)
- **Tolerance:** 0.01 per million (institutional standard)
- **Settlement Date:** 2025-04-18 (standardized)

### Database Verification
```sql
-- Source verification
SELECT 
  COUNT(*) as total,
  COUNT(CASE WHEN status = 'PASS' THEN 1 END) as pass_count,
  COUNT(CASE WHEN status = 'FAIL' THEN 1 END) as fail_count
FROM all_bonds_calculations;
-- Results: 12343 total, 10548 PASS, 1795 FAIL
```

## 🚢 Deployment Status

### Current State
- **Local Development:** ✅ Working
- **Docker Container:** ✅ Ready  
- **GCP Deployment:** ✅ Scripts available
- **Database:** ✅ bloomberg_index.db populated and validated

### Known Issues
- 1,795 bonds still failing 0.01 tolerance (14.5%)
- Day count precision differences between QuantLib and Bloomberg
- Some bonds with massive calculation differences (>1000 per million)

## 🎯 Next Steps

1. **Investigate FAIL bonds** - Debug the 1,795 failing calculations
2. **Day count precision** - Fine-tune QuantLib day count to match Bloomberg exactly
3. **Scale to 100% PASS rate** - Goal is zero tolerance failures
4. **Production deployment** - Deploy to GCP with current 85.5% accuracy

## 📚 Documentation

- [Demo Instructions](DEMO_INSTRUCTIONS.md) - Getting started guide
- [Google Cloud Deployment](GOOGLE_CLOUD_DEPLOYMENT.md) - Production deployment
- [Settlement Date Policy](SETTLEMENT_DATE_POLICY.md) - Date standardization

## 🏛️ Status

**Active Development** 🚧
- 85.5% PASS rate achieved (10,548/12,343 bonds)
- Binary PASS/FAIL system implemented
- 0.01 per million tolerance enforced
- Ready for FAIL bond investigation and optimization

---

**Built for institutional bond analytics with zero-tolerance precision requirements.**
