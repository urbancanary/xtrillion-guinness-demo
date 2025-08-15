# XTrillion Core Bond Analytics API - External User Guide

**🔒 STABLE VERSION: v10.0.0**  
**📅 Last Updated:** August 2, 2025  
**🌐 Production URL:** https://future-footing-414610.uc.r.appspot.com/api/v1

---

## 🎯 **FOR EXTERNAL USERS**

### **API Stability Guarantee**
- ✅ **No Breaking Changes** - Your integration will continue to work
- ✅ **Stable Response Formats** - JSON structure remains consistent  
- ✅ **Backward Compatibility** - We maintain compatibility for 12+ months
- ✅ **Transparent Updates** - Bug fixes are deployed transparently
- ✅ **Advance Notice** - 6+ months notice for any major changes

---

## 🚀 **QUICK START**

### **Authentication**
```http
X-API-Key: gax10_demo_3j5h8m9k2p6r4t7w1q
```

### **Base URL**
```
https://future-footing-414610.uc.r.appspot.com/api/v1
```

### **Health Check**
```bash
curl -s "https://future-footing-414610.uc.r.appspot.com/health" | jq '.'
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "10.0.0",
  "service": "XTrillion Core Bond Analytics API"
}
```

---

## 📊 **CORE ENDPOINTS**

### **1. Individual Bond Analysis**
```bash
curl -X POST "https://future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_demo_3j5h8m9k2p6r4t7w1q" \
  -d '{
    "description": "T 3 15/08/52",
    "price": 71.66
  }'
```

**Response:**
```json
{
  "status": "success",
  "analytics": {
    "ytm": 4.8991,
    "duration": 16.35,
    "accrued_interest": 1.112,
    "clean_price": 71.66,
    "dirty_price": 72.772,
    "macaulay_duration": 16.75,
    "convexity": 370.21,
    "pvbp": 0.1172
  }
}
```

### **2. Portfolio Analysis**
```bash
curl -X POST "https://future-footing-414610.uc.r.appspot.com/api/v1/portfolio/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_demo_3j5h8m9k2p6r4t7w1q" \
  -d '{
    "data": [
      {
        "BOND_CD": "T 3 15/08/52",
        "CLOSING PRICE": 71.66,
        "WEIGHTING": 60.0
      },
      {
        "BOND_CD": "PANAMA, 3.87%, 23-Jul-2060",
        "CLOSING PRICE": 56.60,
        "WEIGHTING": 40.0
      }
    ]
  }'
```

**Response:**
```json
{
  "status": "success",
  "portfolio_metrics": {
    "portfolio_yield": "5.87%",
    "portfolio_duration": "15.3 years",
    "portfolio_spread": "126.4 bps",
    "total_bonds": 2,
    "success_rate": "100.0%"
  },
  "bond_data": [...]
}
```

---

## 📋 **SUPPORTED BOND FORMATS**

### **Treasury Bonds**
```json
{"description": "T 3 15/08/52"}
{"description": "UST 3% 08/15/52"}
{"description": "TREASURY 3.0 08/15/52"}
```

### **Corporate Bonds**
```json
{"description": "AAPL 3.25 02/23/26"}
{"description": "Apple Inc 3.25% 02/23/26"}
```

### **Government Bonds**
```json
{"description": "GERMANY 1.5 08/15/31"}
{"description": "PANAMA, 3.87%, 23-Jul-2060"}
```

### **ISIN Codes**
```json
{"isin": "US912810TJ79"}
{"isin": "XS2249741674"}
```

---

## 🔧 **ERROR HANDLING**

### **HTTP Status Codes**
- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized (invalid API key)
- `500` - Internal server error

### **Error Response Format**
```json
{
  "status": "error",
  "code": 400,
  "message": "Either 'description' or 'isin' must be provided"
}
```

---

## 📈 **RATE LIMITS**

- **Individual Bonds**: 1000 requests/hour
- **Portfolio Analysis**: 100 requests/hour
- **Health Checks**: Unlimited

*Contact us for higher limits if needed*

---

## 🎯 **CALCULATION ACCURACY**

- **Bloomberg Compatible**: Verified against Bloomberg Terminal
- **QuantLib Engine**: Industry-standard mathematical library
- **Institutional Grade**: Suitable for trading and risk management
- **Precision**: Sub-basis point accuracy for major bond types

---

## 📞 **SUPPORT**

### **Documentation**
- **API Reference**: https://future-footing-414610.uc.r.appspot.com/docs
- **Examples**: See this document
- **Status Page**: https://future-footing-414610.uc.r.appspot.com/health

### **Contact**
- **API Documentation**: Available at base URL /docs endpoint
- **Service Status**: Check /health endpoint for system status

### **Issue Reporting**
If you encounter any issues:
1. Check the health endpoint first
2. Verify your API key is correct
3. Ensure request format matches examples
4. Contact support with request details

---

## 📝 **CHANGELOG**

### **v10.0.0 (Current - Stable)**
- Production-ready bond analytics API
- Bloomberg-compatible calculations
- Portfolio analysis with weighted metrics
- Universal bond parser (ISIN + descriptions)
- Comprehensive error handling

### **Future Updates**
- Bug fixes will be deployed transparently
- New features will be additive (no breaking changes)
- API v2 may be introduced in the future (optional upgrade)

---

## 🛡️ **SERVICE LEVEL AGREEMENT**

### **Uptime**
- **Target**: >99.9% availability
- **Maintenance**: Scheduled during low-usage periods
- **Notifications**: Advance notice for planned maintenance

### **Performance**
- **Response Time**: <500ms for individual bond calculations
- **Portfolio Analysis**: <2 seconds for 10-bond portfolios
- **Health Checks**: <100ms

### **Data Quality**
- **Accuracy**: Institutional-grade calculations
- **Consistency**: Stable results across requests
- **Validation**: Continuous testing against market standards

---

## 🎉 **INTEGRATION EXAMPLES**

### **Python**
```python
import requests

def analyze_bond(description, price):
    url = "https://future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "gax10_demo_3j5h8m9k2p6r4t7w1q"
    }
    data = {
        "description": description,
        "price": price
    }
    
    response = requests.post(url, json=data, headers=headers)
    return response.json()

# Example usage
result = analyze_bond("T 3 15/08/52", 71.66)
print(f"Yield: {result['analytics']['ytm']:.4f}%")
```

### **JavaScript**
```javascript
async function analyzeBond(description, price) {
    const response = await fetch(
        'https://future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis',
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': 'gax10_demo_3j5h8m9k2p6r4t7w1q'
            },
            body: JSON.stringify({
                description: description,
                price: price
            })
        }
    );
    
    return await response.json();
}

// Example usage
analyzeBond('T 3 15/08/52', 71.66)
    .then(result => {
        console.log(`Yield: ${result.analytics.ytm.toFixed(4)}%`);
    });
```

### **cURL**
```bash
#!/bin/bash
# Save as analyze_bond.sh

DESCRIPTION="$1"
PRICE="$2"

curl -s -X POST "https://future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_demo_3j5h8m9k2p6r4t7w1q" \
  -d "{\"description\": \"$DESCRIPTION\", \"price\": $PRICE}" \
  | jq '.analytics'

# Usage: ./analyze_bond.sh "T 3 15/08/52" 71.66
```

---

**🔒 Your integration is safe with our stable v10.0.0 API!**  
**📧 Contact us with any questions or for higher rate limits.**
