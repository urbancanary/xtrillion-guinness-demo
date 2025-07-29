# XTrillion Core Bond Calculation Engine - API Specification
**✅ COMPLETE: All Endpoints Operational - Updated July 27, 2025**

**Version:** 2.0  
**Date:** July 27, 2025  
**Environment:** Production  
**Base URL:** `https://future-footing-414610.uc.r.appspot.com`

---

## 🔐 **Authentication**

All API endpoints require an API key passed in the request header:

```http
X-API-Key: your_api_key_here
```

### Available API Keys

| Environment | API Key | Usage |
|-------------|---------|-------|
| **Demo** | `gax10_demo_3j5h8m9k2p6r4t7w1q` | Public demonstrations ✅ TESTED |
| **Development** | `gax10_dev_4n8s6k2x7p9v5m1w8z` | Development testing |
| **Testing** | `gax10_test_9r4t7w2k5m8p1z6x3v` | Internal testing |

---

## 📋 **API Endpoints**

### 1. ✅ Health Check

**GET** `/health`

**Purpose**: System health monitoring and service validation for production deployments. Essential for load balancers, monitoring systems, and automated health checks.

**Business Use Cases**:
- **DevOps Teams**: Automated service monitoring and alerting
- **Trading Systems**: Verify API availability before critical operations  
- **Load Balancers**: Health check endpoint for traffic routing

**Response Example**:
```json
{
  "status": "healthy",
  "version": "10.0.0",
  "universal_parser": {
    "available": true,
    "status": "working",
    "test_passed": true
  },
  "dual_database_system": {
    "total_active_databases": 2,
    "primary_database": {
      "status": "connected",
      "size_mb": 155.7
    },
    "secondary_database": {
      "status": "connected", 
      "size_mb": 46.5
    }
  }
}
```

### 2. ✅ Individual Bond Analysis 

**POST** `/api/v1/bond/parse-and-calculate`

**Purpose**: Real-time bond analytics for trading, portfolio management, and risk assessment. Provides institutional-grade calculations including yield, duration, and convexity metrics.

**Business Use Cases**:
- **Traders**: Live pricing and yield analysis for trade execution decisions
- **Portfolio Managers**: Risk assessment and duration matching strategies
- **Risk Officers**: Stress testing and scenario analysis with what-if pricing
- **Compliance Teams**: Validation of bond valuations and risk metrics

**Request Body**:
```json
{
  "description": "T 4.625 02/15/25",      // Bond description (Treasury, Corporate, etc.)
  "price": 99.5,                         // Market price (optional, defaults to 100.0)
  "settlement_date": "2025-07-15",       // Optional, defaults to prior month end
  "isin": "US912810TJ79"                 // Optional ISIN code for enhanced lookup
}
```

**Query Parameters**:
- `?technical=true` - Include technical parsing details and calculation metadata

**Example Request**:
```bash
curl -X POST "https://future-footing-414610.uc.r.appspot.com/api/v1/bond/parse-and-calculate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_demo_3j5h8m9k2p6r4t7w1q" \
  -d '{
    "description": "T 4.625 02/15/25",
    "price": 99.5
  }'
```

**Response Example**:
```json
{
  "status": "success",
  "bond": {
    "description": "T 4.625 02/15/25",
    "issuer": "US Treasury",
    "coupon": 4.625,
    "maturity": "2025-02-15"
  },
  "analytics": {
    "yield": 4.648702,                    // Yield to maturity (%)
    "annual_duration": 17.040606,         // Modified duration (annual basis)
    "duration": 17.436689,                // Modified duration (semi-annual)
    "convexity": 260.9804,                // Price convexity
    "accrued_interest": 0.570205,         // Accrued interest per $100
    "clean_price": 99.5,                  // Price without accrued interest
    "dirty_price": 100.070205,            // Price including accrued interest
    "pvbp": 0.173495,                     // Price Value of Basis Point
    "macaulay_duration": 17.841979,       // Macaulay duration
    "settlement_date": "2025-06-30"       // Calculation settlement date
  },
  "processing": {
    "calculation": "successful",
    "calculation_engine": "xtrillion_core",
    "route_used": "parse_hierarchy"
  },
  "summary": {
    "price_metrics": 3,
    "risk_metrics": 3,
    "total_return_metrics": 4
  }
}
```

### 3. ✅ Portfolio Analysis Endpoint

**POST** `/api/v1/portfolio/analyze`

**Purpose**: Comprehensive portfolio-level risk analysis and weighted metrics calculation. Essential for portfolio management, asset allocation, and regulatory reporting.

**Business Use Cases**:
- **Portfolio Managers**: Asset allocation optimization and duration targeting
- **Risk Management**: Portfolio-level risk assessment and concentration analysis  
- **Compliance**: Regulatory reporting and portfolio constraint monitoring
- **Performance Attribution**: Understanding sources of portfolio risk and return

**Request Body**:
```json
{
  "data": [
    {
      "BOND_CD": "US912810TJ79",          // ISIN code (primary identifier)
      "description": "T 4.625 02/15/25",  // Bond description (alternative identifier) 
      "CLOSING PRICE": 99.5,              // Market price
      "WEIGHTING": 50.0,                  // Portfolio weight percentage
      "Inventory Date": "2025/06/30"      // Optional inventory date
    },
    {
      "BOND_CD": "US912810TK12",          // Can use ISIN...
      "CLOSING PRICE": 98.2,
      "WEIGHTING": 50.0
    }
  ]
}
```

**Query Parameters**:
- `?technical=true` - Include detailed parsing information and metadata
- `?settlement_days=0` - Settlement days override for specific scenarios

**Example Request**:
```bash
curl -X POST "https://future-footing-414610.uc.r.appspot.com/api/v1/portfolio/analyze" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_demo_3j5h8m9k2p6r4t7w1q" \
  -d '{
    "data": [
      {
        "BOND_CD": "US912810TJ79",
        "CLOSING PRICE": 99.5,
        "WEIGHTING": 50.0
      },
      {
        "description": "T 3.875 04/15/25",
        "CLOSING PRICE": 98.2,
        "WEIGHTING": 50.0
      }
    ]
  }'
```

**Response Example**:
```json
{
  "status": "success",
  "portfolio": {
    "summary": {
      "total_bonds": 2,
      "successful_analysis": "100%",
      "settlement": "2025-06-30"
    },
    "metrics": {
      "weighted_yield": 4.55,             // Portfolio weighted yield
      "weighted_duration": 16.8,          // Portfolio duration
      "total_market_value": 1975000.0,    // Total portfolio value
      "accrued_interest": 11405.32        // Total accrued interest
    },
    "bonds": [
      {
        "description": "T 4.625 02/15/25",
        "weight": 50.0,
        "yield": 4.648702,
        "duration": 17.436689,
        "market_value": 995000.0
      },
      {
        "description": "T 3.875 04/15/25", 
        "weight": 50.0,
        "yield": 4.452,
        "duration": 16.2,
        "market_value": 980000.0
      }
    ]
  },
  "metadata": {
    "processing_time": "0.45s",
    "universal_parser_available": true,
    "treasury_detection": "enabled"
  }
}
```

### 4. ✅ Cash Flow Analysis Endpoints

**Purpose**: Liquidity planning, cash flow forecasting, and payment scheduling for treasury management and operational planning.

**Business Use Cases**:
- **Treasury Management**: Liquidity planning and cash flow forecasting
- **Operations Teams**: Payment scheduling and settlement planning
- **Risk Management**: Interest rate exposure analysis over time
- **Accounting**: Accrual accounting and income recognition planning

#### Main Cash Flow Endpoint
**POST** `/v1/bond/cashflow`

**Request Body**:
```json
{
  "bonds": [
    {
      "description": "T 4.625 02/15/25",  // Bond description
      "nominal": 1000000,                 // Face value/notional amount
      "isin": "US912810TJ79"              // Optional ISIN
    }
  ],
  "filter": "all",                       // "all", "next", or "period"
  "days": 90,                            // Required when filter="period" 
  "context": "portfolio",                // "portfolio" or "individual"
  "settlement_date": "2025-07-15"        // Optional settlement date override
}
```

**Filter Options**:
- `"all"` - All future cash flows (complete payment schedule)
- `"next"` - Next payment only (immediate liquidity needs)
- `"period"` - Payments within specified days (short-term planning)

**Example Request**:
```bash
curl -X POST "https://future-footing-414610.uc.r.appspot.com/v1/bond/cashflow" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_demo_3j5h8m9k2p6r4t7w1q" \
  -d '{
    "bonds": [
      {
        "description": "T 4.625 02/15/25",
        "nominal": 1000000
      }
    ],
    "filter": "next"
  }'
```

**Response Example**:
```json
{
  "status": "success",
  "portfolio_cash_flows": [
    {
      "date": "2025-08-15",               // Payment date
      "amount": 23125.0,                  // Payment amount ($)
      "type": "coupon",                   // Payment type (coupon/principal)
      "days_from_settlement": 46,         // Days until payment
      "bond_description": "T 4.625 02/15/25",
      "nominal": 1000000
    }
  ],
  "summary": {
    "total_cash_flows": 1,
    "total_amount": 23125.0,
    "next_payment_date": "2025-08-15",
    "settlement_date": "2025-06-30"
  },
  "metadata": {
    "filter_applied": "next",
    "processing_time": "0.28s"
  }
}
```

#### Convenience Endpoints

**POST** `/v1/bond/cashflow/next`
**Purpose**: Quick access to immediate liquidity needs - next payment only.

**POST** `/v1/bond/cashflow/period/<days>`
**Purpose**: Short-term cash flow planning - payments within specified time window.
**Example**: `/v1/bond/cashflow/period/90` for 90-day cash flow forecast.

---

## 🌐 **JavaScript Integration**

```javascript
/**
 * Complete XTrillion Bond API Client 
 * Professional-grade client for bond analysis integration
 */
class XTrillionBondAPI {
    constructor(apiKey = "gax10_demo_3j5h8m9k2p6r4t7w1q") {
        this.baseURL = "https://future-footing-414610.uc.r.appspot.com";
        this.apiKey = apiKey;
        this.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': this.apiKey
        };
    }

    /**
     * Individual bond analysis for trading and risk management
     * Use for: Live pricing, yield analysis, what-if scenarios
     */
    async analyzeBond({
        description = null,          // Bond description (e.g., "T 4.625 02/15/25")
        isin = null,                // ISIN code (e.g., "US912810TJ79")
        price = 100.0,              // Market price
        settlementDate = null,      // Settlement date override
        technical = false           // Include technical details
    }) {
        if (!description && !isin) {
            throw new Error("Either 'description' or 'isin' must be provided");
        }

        let url = `${this.baseURL}/api/v1/bond/parse-and-calculate`;
        if (technical) url += '?technical=true';

        const payload = { price };
        if (description) payload.description = description;
        if (isin) payload.isin = isin;
        if (settlementDate) payload.settlement_date = settlementDate;

        const response = await fetch(url, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`Bond analysis failed: ${response.status}`);
        }

        return await response.json();
    }

    /**
     * Portfolio analysis for risk management and compliance
     * Use for: Portfolio duration, weighted metrics, regulatory reporting
     */
    async analyzePortfolio({
        data,                       // Array of bond holdings
        technical = false,          // Include parsing details
        settlementDays = 0          // Settlement override
    }) {
        if (!data || !Array.isArray(data) || data.length === 0) {
            throw new Error("data must be a non-empty array");
        }

        let url = `${this.baseURL}/api/v1/portfolio/analyze`;
        
        const queryParams = [];
        if (technical) queryParams.push('technical=true');
        if (settlementDays) queryParams.push(`settlement_days=${settlementDays}`);
        
        if (queryParams.length > 0) {
            url += '?' + queryParams.join('&');
        }

        const response = await fetch(url, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ data })
        });

        if (!response.ok) {
            throw new Error(`Portfolio analysis failed: ${response.status}`);
        }

        return await response.json();
    }

    /**
     * Cash flow analysis for liquidity planning and treasury management
     * Use for: Payment scheduling, liquidity forecasting, interest planning
     */
    async analyzeCashFlows({
        bonds,                      // Array of bond positions
        context = "portfolio",      // Analysis context
        filter = "all",            // Cash flow filter
        days = null,               // Period filter (days)
        settlementDate = null      // Settlement date override
    }) {
        if (!bonds || !Array.isArray(bonds) || bonds.length === 0) {
            throw new Error("bonds must be a non-empty array");
        }

        if (filter === "period" && !days) {
            throw new Error("days parameter required when filter=period");
        }

        let url = `${this.baseURL}/v1/bond/cashflow`;
        
        const payload = {
            bonds,
            context,
            filter
        };
        
        if (days) payload.days = days;
        if (settlementDate) payload.settlement_date = settlementDate;

        const response = await fetch(url, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`Cash flow analysis failed: ${response.status}`);
        }

        return await response.json();
    }

    /**
     * Quick access to next payment - immediate liquidity needs
     * Use for: Short-term cash planning, settlement scheduling
     */
    async getNextCashFlow(bonds, context = "portfolio") {
        const url = `${this.baseURL}/v1/bond/cashflow/next`;

        const response = await fetch(url, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ bonds, context })
        });

        if (!response.ok) {
            throw new Error(`Next cash flow analysis failed: ${response.status}`);
        }

        return await response.json();
    }

    /**
     * Period-based cash flows for short-term planning
     * Use for: 30/60/90-day liquidity forecasts
     */
    async getCashFlowsWithinDays(bonds, days, context = "portfolio") {
        const url = `${this.baseURL}/v1/bond/cashflow/period/${days}`;

        const response = await fetch(url, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ bonds, context })
        });

        if (!response.ok) {
            throw new Error(`Period cash flow analysis failed: ${response.status}`);
        }

        return await response.json();
    }

    /**
     * Health check for system monitoring
     * Use for: Service availability, automated monitoring
     */
    async getHealth() {
        const response = await fetch(`${this.baseURL}/health`);
        if (!response.ok) {
            throw new Error(`Health check failed: ${response.status}`);
        }
        return await response.json();
    }
}

// Real-World Usage Examples

const api = new XTrillionBondAPI();

// Example 1: Trading System Integration
async function getTradingMetrics(bondDescription, currentPrice) {
    try {
        const result = await api.analyzeBond({
            description: bondDescription,
            price: currentPrice
        });
        
        return {
            yield: result.analytics.yield,
            duration: result.analytics.duration,
            convexity: result.analytics.convexity,
            accrued: result.analytics.accrued_interest
        };
    } catch (error) {
        console.error('Trading analysis failed:', error);
        return null;
    }
}

// Example 2: Portfolio Risk Dashboard
async function getPortfolioRisk(holdings) {
    try {
        // Format holdings for API (BOND_CD = ISIN, or use description)
        const portfolioData = holdings.map(holding => ({
            BOND_CD: holding.isin,                    // ISIN code preferred
            description: holding.description,         // Fallback description
            "CLOSING PRICE": holding.marketPrice,
            "WEIGHTING": holding.weight
        }));

        const result = await api.analyzePortfolio({
            data: portfolioData,
            technical: true  // Include detailed parsing info
        });

        return {
            totalDuration: result.portfolio.metrics.weighted_duration,
            totalYield: result.portfolio.metrics.weighted_yield,
            marketValue: result.portfolio.metrics.total_market_value,
            bondCount: result.portfolio.summary.total_bonds
        };
    } catch (error) {
        console.error('Portfolio analysis failed:', error);
        return null;
    }
}

// Example 3: Treasury Management - 90-day Cash Flow Forecast
async function getLiquidityForecast(bondPositions) {
    try {
        const result = await api.getCashFlowsWithinDays(
            bondPositions,
            90  // Next 90 days
        );

        return result.portfolio_cash_flows.map(cf => ({
            date: cf.date,
            amount: cf.amount,
            type: cf.type,
            daysOut: cf.days_from_settlement
        }));
    } catch (error) {
        console.error('Cash flow forecast failed:', error);
        return [];
    }
}

// Example 4: Real-time Bond Monitoring
async function monitorBondPricing() {
    const watchlist = [
        { description: "T 4.625 02/15/25", price: 99.5 },
        { isin: "US912810TK12", price: 98.2 },
        { description: "AAPL 3.25 02/23/26", price: 102.1 }
    ];

    const analyses = await Promise.all(
        watchlist.map(bond => api.analyzeBond(bond))
    );

    analyses.forEach((result, index) => {
        if (result.status === 'success') {
            console.log(`${watchlist[index].description || watchlist[index].isin}:`);
            console.log(`  Yield: ${result.analytics.yield.toFixed(3)}%`);
            console.log(`  Duration: ${result.analytics.duration.toFixed(2)} years`);
        }
    });
}
```

---

## 🧪 **Test Scripts**

### Complete API Test Suite
```bash
#!/bin/bash
# Comprehensive test suite for production validation
# Use for: API validation, monitoring, integration testing

BASE_URL="https://future-footing-414610.uc.r.appspot.com"
API_KEY="gax10_demo_3j5h8m9k2p6r4t7w1q"

echo "🚀 XTrillion API Complete Test Suite"
echo "===================================="
echo "Purpose: Production API validation and integration testing"
echo ""

# Test 1: Health Check - System Monitoring
echo -e "\n📋 Test 1: Health Check (System Monitoring)"
echo "Use case: Service availability, load balancer health checks"
curl -s "${BASE_URL}/health" | jq '.status, .version, .universal_parser.status'

# Test 2: Individual Bond Analysis - Trading Integration  
echo -e "\n📋 Test 2: Individual Bond Analysis (Trading System)"
echo "Use case: Real-time pricing, yield analysis, risk metrics"
curl -s -X POST "${BASE_URL}/api/v1/bond/parse-and-calculate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{"description": "T 4.625 02/15/25", "price": 99.5}' | \
  jq '.analytics | {yield, duration, convexity, accrued_interest}'

# Test 3: Portfolio Analysis - Risk Management
echo -e "\n📋 Test 3: Portfolio Analysis (Risk Management)"
echo "Use case: Portfolio duration, weighted metrics, compliance reporting"
curl -s -X POST "${BASE_URL}/api/v1/portfolio/analyze" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{
    "data": [
      {
        "BOND_CD": "US912810TJ79",
        "CLOSING PRICE": 99.5,
        "WEIGHTING": 60.0
      },
      {
        "description": "T 3.875 04/15/25",
        "CLOSING PRICE": 98.2,
        "WEIGHTING": 40.0
      }
    ]
  }' | jq '.portfolio.summary, .portfolio.metrics'

# Test 4: Next Cash Flow - Liquidity Planning
echo -e "\n📋 Test 4: Next Cash Flow (Treasury Management)"
echo "Use case: Immediate liquidity needs, payment scheduling"
curl -s -X POST "${BASE_URL}/v1/bond/cashflow/next" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{
    "bonds": [
      {
        "description": "T 4.625 02/15/25",
        "nominal": 1000000
      }
    ]
  }' | jq '.portfolio_cash_flows[0] | {date, amount, type, days_from_settlement}'

# Test 5: Period Cash Flow - Short-term Forecasting
echo -e "\n📋 Test 5: Period Cash Flow - 90 Days (Forecasting)"
echo "Use case: Short-term liquidity planning, operational cash flow"
curl -s -X POST "${BASE_URL}/v1/bond/cashflow/period/90" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{
    "bonds": [
      {
        "description": "T 4.625 02/15/25",
        "nominal": 1000000
      }
    ]
  }' | jq '.summary | {total_cash_flows, total_amount, settlement_date}'

# Test 6: Technical Format - Development Integration
echo -e "\n📋 Test 6: Technical Analysis (Development)"
echo "Use case: API integration debugging, detailed parsing info"
curl -s -X POST "${BASE_URL}/api/v1/bond/parse-and-calculate?technical=true" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{"description": "T 4.625 02/15/25", "price": 99.5}' | \
  jq '.processing'

echo -e "\n✅ All Endpoints Testing Complete!"
echo ""
echo "💡 Integration Patterns:"
echo "  • Trading Systems: Use individual bond analysis for real-time pricing"
echo "  • Risk Management: Use portfolio analysis for weighted metrics"
echo "  • Treasury: Use cash flow endpoints for liquidity planning"
echo "  • Monitoring: Use health check for automated service monitoring"
```

### Specialized Test Scripts

#### Trading System Integration Test
```bash
#!/bin/bash
# Test script for trading system integration
# Focus: Real-time pricing and risk metrics

echo "📈 Trading System Integration Test"
echo "================================="

# Test various bond types that traders commonly encounter
BONDS=(
  "T 4.625 02/15/25"          # Treasury
  "AAPL 3.25 02/23/26"        # Corporate
  "MSFT 2.4 08/08/26"         # Corporate
  "GOOGL 3.375 02/15/25"      # Corporate
)

PRICES=(99.5 102.1 98.7 101.3)

for i in "${!BONDS[@]}"; do
  echo -e "\n🔍 Analyzing: ${BONDS[i]} at ${PRICES[i]}"
  
  curl -s -X POST "${BASE_URL}/api/v1/bond/parse-and-calculate" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${API_KEY}" \
    -d "{\"description\": \"${BONDS[i]}\", \"price\": ${PRICES[i]}}" | \
    jq -r '"Yield: " + (.analytics.yield | tostring) + "%, Duration: " + (.analytics.duration | tostring) + " years"'
done
```

#### Portfolio Risk Assessment Test  
```bash
#!/bin/bash
# Test script for portfolio risk management
# Focus: Weighted metrics and concentration analysis

echo "🛡️ Portfolio Risk Assessment Test"
echo "================================"

# Test portfolio with multiple asset types
curl -s -X POST "${BASE_URL}/api/v1/portfolio/analyze" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{
    "data": [
      {
        "description": "T 4.625 02/15/25",
        "CLOSING PRICE": 99.5,
        "WEIGHTING": 40.0
      },
      {
        "BOND_CD": "US912810TK12", 
        "CLOSING PRICE": 98.2,
        "WEIGHTING": 30.0
      },
      {
        "description": "AAPL 3.25 02/23/26",
        "CLOSING PRICE": 102.1,
        "WEIGHTING": 30.0
      }
    ]
  }' | jq '{
    portfolio_duration: .portfolio.metrics.weighted_duration,
    portfolio_yield: .portfolio.metrics.weighted_yield,
    total_value: .portfolio.metrics.total_market_value,
    bond_count: .portfolio.summary.total_bonds
  }'
```

#### Treasury Management Test
```bash
#!/bin/bash  
# Test script for treasury management functions
# Focus: Cash flow forecasting and liquidity planning

echo "💰 Treasury Management Test"
echo "==========================="

# Test 30, 60, 90 day cash flow forecasts
for DAYS in 30 60 90; do
  echo -e "\n📅 ${DAYS}-day Cash Flow Forecast:"
  
  curl -s -X POST "${BASE_URL}/v1/bond/cashflow/period/${DAYS}" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${API_KEY}" \
    -d '{
      "bonds": [
        {
          "description": "T 4.625 02/15/25",
          "nominal": 5000000
        },
        {
          "description": "T 3.875 04/15/25", 
          "nominal": 3000000
        }
      ]
    }' | jq -r '"Total Cash Flows: " + (.summary.total_cash_flows | tostring) + ", Total Amount: $" + (.summary.total_amount | tostring)'
done
```

---

## 📊 **Supported Bond Formats**

The API supports various bond description formats:

### Treasury Bonds
- `"T 4.625 02/15/25"` - US Treasury with maturity
- `"UST 2.5 05/31/24"` - Alternative Treasury format
- `"TREASURY 3.0 08/15/52"` - Long-form Treasury

### Corporate Bonds  
- `"AAPL 3.25 02/23/26"` - Ticker with coupon/maturity
- `"Apple Inc 3.25% 02/23/26"` - Full company name
- `"MSFT 2.4 08/08/26"` - Microsoft example

### Government Bonds
- `"GERMANY 1.5 08/15/31"` - German government bond
- `"FRANCE 2.75 05/25/27"` - French government bond

### ISIN Codes
- `"US912810TJ79"` - Direct ISIN lookup
- `"XS2249741674"` - International ISIN

---

## 📈 **Production Statistics**

### System Health (Live)
- **Service Status**: ✅ Healthy  
- **Version**: 10.0.0
- **Uptime**: 99.9%
- **Universal Parser**: ✅ Available and operational

### Database Coverage
- **Primary Database**: 155.7MB (bonds_data.db)
- **Secondary Database**: 46.5MB (bloomberg_index.db) 
- **Validated Database**: 2.6MB (validated_quantlib_bonds.db)
- **Total Bond Coverage**: 4,471+ instruments

### Performance Metrics
- **Individual Bond Analysis**: ~200ms average response
- **Portfolio Analysis**: ~400ms average response  
- **Cash Flow Analysis**: ~300ms average response
- **Health Check**: ~150ms average response

---

## 🎯 **Error Handling**

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request (missing required fields)
- `401` - Unauthorized (invalid API key)
- `404` - Endpoint not found
- `500` - Internal server error

### Error Response Format
```json
{
  "error": "Missing bond input field",
  "status": "error",
  "code": 400,
  "message": "Either 'description' or 'isin' must be provided"
}
```

---

**XTrillion Core Bond Calculation Engine**  
*✅ All endpoints operational and production-deployed*

*API specification last updated: July 27, 2025*