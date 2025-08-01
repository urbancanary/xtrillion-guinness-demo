# XTrillion Google Sheets Functions - Production Ready

## 📊 **xt_functions.gs - Professional Bond Analytics**

**Version:** 1.1 Production Ready with Settlement Date Support  
**Created:** August 1, 2025  
**File Location:** `/google_analysis10/xt_functions.gs`

### **🎯 Overview**
Professional-grade Google Sheets functions that connect directly to the XTrillion Core Bond Analytics API. Provides real-time bond calculations including yield, duration, accrued interest, and spread analytics.

### **🚀 Quick Start**

#### **Installation:**
1. Open Google Sheets
2. Extensions → Apps Script
3. Copy and paste the entire `xt_functions.gs` file
4. Save and authorize when prompted

#### **Basic Usage:**
```javascript
// US Treasury yield:
=xt_ytm("T 3 15/08/52", 71.66)

// Corporate bond duration:
=xt_duration("ECOPETROL SA, 5.875%, 28-May-2045", 69.31)

// Emerging market spread:
=xt_spread("PANAMA, 3.87%, 23-Jul-2060", 56.60)
```

#### **With Settlement Date:**
```javascript
// Using specific date:
=xt_ytm("T 3 15/08/52", 71.66, "2025-08-01")

// Using TODAY() function:
=xt_accrued_interest("T 3 15/08/52", 71.66, TODAY())

// Using date cell reference:
=xt_duration("T 3 15/08/52", 71.66, A1)
```

### **📋 Available Functions**

| Function | Description | Example |
|----------|-------------|---------|
| `xt_ytm(bond, price, [date])` | Yield to maturity (%) | `=xt_ytm("T 3 15/08/52", 71.66)` |
| `xt_duration(bond, price, [date])` | Modified duration (years) | `=xt_duration("T 3 15/08/52", 71.66)` |
| `xt_accrued_interest(bond, price, [date])` | Accrued interest (%) | `=xt_accrued_interest("T 3 15/08/52", 71.66)` |
| `xt_accrued_pm(bond, price, [date])` | Accrued per million (Bloomberg) | `=xt_accrued_pm("T 3 15/08/52", 71.66)` |
| `xt_spread(bond, price, [date])` | Spread over govt curve (bps) | `=xt_spread("ECOPETROL SA, 5.875%, 28-May-2045", 69.31)` |
| `xt_macaulay_duration(bond, price, [date])` | Macaulay duration (years) | `=xt_macaulay_duration("T 3 15/08/52", 71.66)` |
| `xt_convexity(bond, price, [date])` | Convexity | `=xt_convexity("T 3 15/08/52", 71.66)` |

### **🔍 Validation Functions**

| Function | Description | Example |
|----------|-------------|---------|
| `xt_accrued_compare(bond, price, bbg_value, [date])` | Compare vs Bloomberg | `=xt_accrued_compare("T 3 15/08/52", 71.66, 11123.60)` |
| `xt_validation_status(bond, price, bbg_value, [date])` | Match status | `=xt_validation_status("T 3 15/08/52", 71.66, 11123.60)` |
| `xt_test_date(test_date)` | Test date formatting | `=xt_test_date("2025-08-01")` |

### **🗓️ Settlement Date Support**

The functions now support optional settlement dates in multiple formats:

#### **Supported Date Formats:**
- **ISO Format:** `"2025-08-01"`
- **US Format:** `"08/01/2025"`
- **Google Sheets Functions:** `TODAY()`, `DATE(2025,8,1)`
- **Cell References:** `A1` (where A1 contains a date)
- **Various String Formats:** `"August 1, 2025"`, `"Aug 1 2025"`

#### **Examples:**
```javascript
// Different date formats all work:
=xt_ytm("T 3 15/08/52", 71.66, "2025-08-01")        // ISO format
=xt_ytm("T 3 15/08/52", 71.66, "08/01/2025")        // US format
=xt_ytm("T 3 15/08/52", 71.66, TODAY())             // Current date
=xt_ytm("T 3 15/08/52", 71.66, A1)                  // Cell reference
```

### **💡 Pro Tips**

#### **Portfolio Setup Example:**
| A | B | C | D | E |
|---|---|---|---|---|
| **Bond** | **Price** | **Yield** | **Duration** | **Spread** |
| T 3 15/08/52 | 71.66 | `=xt_ytm(A2,B2)` | `=xt_duration(A2,B2)` | `=xt_spread(A2,B2)` |
| PANAMA, 3.87%, 23-Jul-2060 | 56.60 | `=xt_ytm(A3,B3)` | `=xt_duration(A3,B3)` | `=xt_spread(A3,B3)` |

#### **Bloomberg Validation:**
| A | B | C | D | E |
|---|---|---|---|---|
| **Bond** | **Price** | **BBG Accrued** | **XT Accrued** | **Status** |
| T 3 15/08/52 | 71.66 | 11123.60 | `=xt_accrued_pm(A2,B2)` | `=xt_validation_status(A2,B2,C2)` |

### **🔧 Technical Details**

#### **API Configuration:**
- **Base URL:** `https://future-footing-414610.uc.r.appspot.com`
- **API Key:** `gax10_demo_3j5h8m9k2p6r4t7w1q` (demo key)
- **Version:** XTrillion Core 10.0.0

#### **Supported Bond Formats:**
- **US Treasuries:** `"T 3 15/08/52"`, `"UST 3% 08/15/52"`
- **Corporate Bonds:** `"AAPL 3.25 02/23/26"`
- **Sovereigns:** `"GERMANY 1.5 08/15/31"`
- **Emerging Markets:** `"PANAMA, 3.87%, 23-Jul-2060"`
- **Full Descriptions:** `"ECOPETROL SA, 5.875%, 28-May-2045"`

### **📝 Version History**

- **v1.1** (August 1, 2025): Added settlement date support
- **v1.0** (August 1, 2025): Initial production release

### **🔗 Integration**

This Google Sheets integration is part of the larger XTrillion ecosystem:
- **Main Project:** `/google_analysis10/`
- **API Specification:** See project documentation
- **Python Integration:** `XTrillion Bond Analytics Showcase.py`
- **Mac Excel Bridge:** `Mac Excel Bond API Bridge.py`

### **📞 Support**

For issues or questions:
1. Test API connection: Use `=xt_test_date(TODAY())` to verify functionality
2. Check function syntax: All functions support optional settlement date as 3rd parameter
3. Validate dates: Use `=xt_test_date("your_date")` to test date formatting

---
**🎯 Production-ready professional bond analytics for Google Sheets!**