# 🎯 CALCULATE_BOND_MASTER FUNCTION DOCUMENTATION

## 📍 QUICK REFERENCE - ALWAYS USE THIS!

**File Location:**
```
/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/bond_master_hierarchy.py
```

**Main Function:**
```python
from bond_master_hierarchy import calculate_bond_master
```

**With Weightings Function:**
```python
from bond_master_hierarchy import process_bonds_with_weightings
```

## 🚀 FUNCTION SIGNATURES

### Primary Function: calculate_bond_master
```python
def calculate_bond_master(
    isin: Optional[str] = None,
    description: str = "T 3 15/08/52", 
    price: float = 100.0,
    settlement_date: Optional[str] = None,
    db_path: str = './bonds_data.db',
    validated_db_path: str = './validated_quantlib_bonds.db',
    bloomberg_db_path: str = './bloomberg_index.db'
) -> Dict[str, Any]:
```

### Compatibility Function: process_bonds_with_weightings  
```python
def process_bonds_with_weightings(
    df: pd.DataFrame, 
    db_path: str, 
    record_number: int = 1
) -> pd.DataFrame:
```

## ✅ USAGE EXAMPLES

### 1. Single Bond with ISIN (Route 1: ISIN Hierarchy)
```python
from bond_master_hierarchy import calculate_bond_master

result = calculate_bond_master(
    isin='US912810TJ79',
    description='US TREASURY N/B, 3%, 15-Aug-2052',
    price=71.66
)

print(f"Yield: {result['yield']:.4f}%")
print(f"Duration: {result['duration']:.4f}")
print(f"Route: {result['route_used']}")
```

### 2. Single Bond without ISIN (Route 2: Parse Hierarchy)
```python
result = calculate_bond_master(
    isin=None,  # No ISIN - triggers parse hierarchy
    description='T 3 15/08/52',
    price=71.66
)
```

### 3. Multiple Bonds with DataFrame (Weightings Support)
```python
import pandas as pd
from bond_master_hierarchy import process_bonds_with_weightings

# Create DataFrame with bonds
df = pd.DataFrame([
    {'isin': 'US912810TJ79', 'Name': 'US TREASURY N/B, 3%, 15-Aug-2052', 'price': 71.66},
    {'isin': None, 'Name': 'T 3 15/08/52', 'price': 71.66}
])

# Process all bonds
results_df = process_bonds_with_weightings(df, './bonds_data.db')
```

## 🛣️ HOW IT WORKS - DUAL HIERARCHY SYSTEM

The function implements **TWO ROUTES** that converge to the same calculation engine:

### Route 1: ISIN Hierarchy (when ISIN provided)
1. Uses ISIN for database lookups
2. Falls back to ticker lookup if needed
3. Applies Treasury overrides if detected
4. Uses ISIN character patterns for clues
5. Defaults as final fallback

### Route 2: Parse Hierarchy (when no ISIN)  
1. Parses description for bond details
2. Extracts coupon, maturity, issuer
3. Applies convention detection
4. Uses SmartBondParser

### Convergence Point
Both routes feed into the same `process_bond_portfolio` function in `google_analysis10.py`

## 📊 RETURN FORMAT

```python
{
    'success': True,
    'isin': 'US912810TJ79',
    'description': 'US TREASURY N/B, 3%, 15-Aug-2052', 
    'price': 71.66,
    'yield': 4.9517212959087775,
    'duration': 0.16020858697288476,
    'spread': None,  # Calculated if treasury yields available
    'accrued_interest': None,
    'conventions': {...},
    'route_used': 'isin_hierarchy',  # or 'parse_hierarchy'
    'isin_provided': True,
    'calculation_method': 'shared_quantlib_engine',
    'settlement_date': None
}
```

## 🔧 KEY FIELD MAPPINGS (CRITICAL!)

The function expects these exact field names in bond_data:
- ✅ `'price'` (NOT `'CLOSING PRICE'`)
- ✅ `'isin'` (NOT `'BOND_CD'`)  
- ✅ `'description'` (correct)

**This was the source of the recent bug that was fixed!**

## 🎯 WHEN TO USE WHICH FUNCTION

### Use `calculate_bond_master` when:
- Processing a single bond
- Need detailed route information
- Want to specify ISIN vs parse hierarchy
- Working with individual bond calculations

### Use `process_bonds_with_weightings` when:
- Processing multiple bonds from DataFrame
- Working with comprehensive testing framework
- Need compatibility with existing tester code
- Processing portfolio-level data

## 🔍 SEARCH KEYWORDS FOR FUTURE REFERENCE

**To find this documentation quickly, search for:**
- `"calculate_bond_master function location"`
- `"bond_master_hierarchy.py documentation"`
- `"CALCULATE_BOND_MASTER_DOCS"`
- `"google_analysis10 master bond function"`
- `"process_bonds_with_weightings location"`

## ⚠️ CRITICAL DEPENDENCIES

### Required Files:
- `google_analysis10.py` - Contains `process_bond_portfolio`
- `bond_description_parser.py` - Contains `SmartBondParser`
- `bonds_data.db` - Main database
- `validated_quantlib_bonds.db` - Conventions database
- `bloomberg_index.db` - Bloomberg data

### Required Imports:
```python
import sys
import os
import pandas as pd
import logging
from typing import Dict, Any, Optional, Union
from google_analysis10 import process_bond_portfolio
```

## 🚀 QUICK TEST COMMANDS

### Test Single Bond:
```bash
cd /Users/andyseaman/Notebooks/json_receiver_project/google_analysis10
python3 -c "
from bond_master_hierarchy import calculate_bond_master
result = calculate_bond_master(isin='US912810TJ79', description='US TREASURY N/B, 3%, 15-Aug-2052', price=71.66)
print(f'Success: {result[\"success\"]}, Yield: {result[\"yield\"]:.4f}%')
"
```

### Test Both Routes:
```bash
cd /Users/andyseaman/Notebooks/json_receiver_project/google_analysis10
python3 bond_master_hierarchy.py
```

## 📝 RECENT FIXES (July 26, 2025)

**Fixed field name mapping issues:**
- Changed `'CLOSING PRICE'` → `'price'`
- Changed `'BOND_CD'` → `'isin'`
- Removed unnecessary `'Name'` and `'BOND_ENAME'` fields

**Results after fix:**
- ✅ ISIN correctly passed through
- ✅ Price correctly used (71.66 instead of defaulting to 100.0)
- ✅ Both ISIN and parse routes working
- ✅ Yields calculated correctly (4.9517% for test bond)

---

**🎯 BOTTOM LINE: Always import from `bond_master_hierarchy.py` - this is your proven, working bond calculation master function!**
