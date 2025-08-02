# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the **Google Analysis 10** (GA10) project - a professional-grade bond analytics API powered by XTrillion Core calculation engine. It provides institutional-quality bond analysis including yield-to-maturity, duration, convexity, and other risk metrics.

### API Documentation Structure
- **`API_SPECIFICATION_PRODUCTION_REALITY.md`** - Internal documentation with actual implementation details and real URLs
- **`API_SPECIFICATION_EXTERNAL.md`** - Client-facing documentation with branded URLs for external stakeholders

## Core Architecture

### Main API Service
- **`google_analysis10_api.py`** - Primary Flask API server with Universal Parser integration
- **Base URL**: `https://future-footing-414610.uc.r.appspot.com` (production) or `http://localhost:8080` (local)
- **Authentication**: API key required via `X-API-Key` header

### Calculation Engines
- **`bond_master_hierarchy_enhanced.py`** - Master calculation function (`calculate_bond_master`) with enhanced metrics
- **`google_analysis10.py`** - Portfolio processing engine (`process_bond_portfolio`)
- **`bloomberg_accrued_calculator.py`** - Bloomberg-compatible accrued interest calculations

### Database Architecture
- **`bonds_data.db`** - Primary bond reference database (comprehensive bond data)
- **`validated_quantlib_bonds.db`** - Validated bond conventions database (7,787+ bonds)
- **`bloomberg_index.db`** - Bloomberg reference data for validation

## Development Commands

### Local Development
```bash
# Start the API server locally
./start_ga10_portfolio_api.sh

# Alternative direct start
python3 google_analysis10_api.py

# Run specific tests
python3 test_25_bond_portfolio_comprehensive.py
```

### Production Deployment
```bash
# Deploy to Google App Engine (recommended approach)
./deploy_appengine.sh
```

**Note**: The GCS-based deployment approach is preferred because it enables:
- Faster deployments (30-60 seconds)
- Independent database updates via Google Cloud Storage  
- Cloud-native architecture with proper code/data separation
- Lower storage costs with smaller container images

### Testing
```bash
# Test individual bonds
python3 test_individual_bonds_all_25.py

# Test portfolio analysis
python3 test_25_bond_portfolio_corrected.py

# Comprehensive bond testing
python3 test_all_25_bonds.py
```

## API Endpoints

### Core Endpoints
- **`POST /api/v1/bond/analysis`** - Individual bond calculation with Universal Parser
- **`POST /api/v1/portfolio/analysis`** - Portfolio-level analytics with aggregation
- **`GET /health`** - Service health check with database status
- **`GET /api/v1/version`** - API version and capabilities

### Legacy Endpoints (Deprecated)
- **`POST /api/v1/bond/parse-and-calculate`** → Use `/api/v1/bond/analysis`
- **`POST /api/v1/portfolio/analyze`** → Use `/api/v1/portfolio/analysis`

## Key Features

### Universal Parser Integration
- Supports both ISIN codes and bond descriptions in single endpoint
- Automatic input type detection (no need to specify format)
- Eliminates 3x parsing redundancy from previous versions
- Proven SmartBondParser integration fixes complex description parsing

### Enhanced Metrics (14 Total)
- **Core**: YTM, Modified Duration, Convexity, PVBP
- **Annual**: Annual YTM, Annual Duration, Annual Macaulay Duration  
- **Pricing**: Clean Price, Dirty Price, Accrued Interest, Accrued Per Million
- **Risk**: Macaulay Duration, G-Spread (spread), Z-Spread (when treasury curve available)

### Production Features
- **Authentication**: 8 different API keys for various environments
- **Multi-database**: Triple database lookup for maximum bond coverage
- **Error Handling**: Comprehensive error responses with debugging info
- **Maturity Detection**: Automatic detection and handling of matured bonds
- **Enhanced Fallback Hierarchy**: Always returns calculations even for invalid inputs
  - ISIN lookup → Parse as description → ISIN pattern analysis → Default conventions
  - Weekend/holiday treasury dates automatically use most recent available data

## Input Formats

### Bond Analysis Request
```json
{
    "description": "T 4.1 02/15/28",      // Treasury description
    "price": 99.5,
    "settlement_date": "2025-07-15"       // Optional
}
```

### Alternative Input Fields
- `"bond_input"` - Alternative to `"description"`
- `"isin"` - ISIN code input

### Portfolio Analysis Request  

**Method 1: Using descriptions (recommended):**
```json
{
    "data": [
        {
            "description": "T 3 15/08/52",    // Bond description (reliable)
            "CLOSING PRICE": 71.66,
            "WEIGHTING": 25.0,
            "Inventory Date": "2025/07/15"     // Optional
        }
    ]
}
```

**Method 2: Using ISINs (Taiwan client naming):**
```json
{
    "data": [
        {
            "BOND_CD": "US00131MAB90",        // ISIN code only
            "CLOSING PRICE": 71.66,
            "WEIGHTING": 25.0
        }
    ]
}
```

**Important**: 
- `BOND_CD` is Taiwan client's field name for ISIN codes only
- `description` field should be used for bond descriptions  
- ISIN lookup currently has reliability issues - use descriptions when possible

## Database Setup

### Local Development
Ensure these databases exist in the project root:
- `bonds_data.db` (primary bond data)
- `validated_quantlib_bonds.db` (validated conventions)  
- `bloomberg_index.db` (Bloomberg reference)

### Production
Databases are either:
1. **Embedded** in Docker container (production-optimized deployment)
2. **Downloaded** from Google Cloud Storage (standard deployment)

## Context-Aware Responses

The API supports different response contexts:

### Portfolio Context (`"context": "portfolio"`)
- Optimized for portfolio aggregation
- Includes both annual and semi-annual metrics
- Simplified response structure

### Technical Context (`"context": "technical"`)  
- Enhanced debugging information
- Parsing route details
- Metadata for troubleshooting

### Default Context
- Standard comprehensive response
- Complete field descriptions
- Self-documenting format

## Important Constants

### Settlement Dates
- **Default**: Prior month end (institutional standard)
- **Standardized Testing**: 2025-04-18 for Bloomberg validation

### Bond Conventions
- **Treasury**: ActualActual_Bond day count, Semi-annual frequency
- **Corporate**: 30/360 day count, Semi-annual frequency  
- **Auto-detection**: Based on ISIN patterns and description parsing

## File Structure Notes

### Core Calculation Files
- Main API routes are in `google_analysis10_api.py:820-1045` (bond analysis)
- Portfolio processing in `google_analysis10_api.py:1046-1188`
- Master calculation in `bond_master_hierarchy_enhanced.py`

### Testing Files
- Individual bond tests: `test_individual_bonds_all_25.py`
- Portfolio tests: `test_25_bond_portfolio_*.py`
- API integration tests: `test_enhanced_api.py`

### Deployment Files
- Production Docker: `Dockerfile.production`
- Standard Docker: `Dockerfile`
- App Engine config: `app.yaml`, `app.production.yaml`

## Common Issues & Solutions

### Matured Bonds
The API automatically detects matured bonds and returns appropriate responses with null analytics.

### Parser Fallbacks
If Universal Parser fails, the system falls back to ISIN routing fix and SmartBondParser.

### Database Connectivity
Production deployment includes health checks that verify all three databases are accessible.

### Known Limitations
- **ISINs**: Direct ISIN lookup has limited coverage - use bond descriptions when possible
- **String Prices**: Prices must be sent as numbers, not strings (e.g., 99.5 not "99.5")
- **Z-Spread**: Only calculated when full treasury curve data is available
- **Cash Flow Endpoints**: Not yet implemented (documented for future release)

## Quality Metrics

### Current Performance
- **85.5% PASS rate** on Bloomberg validation (10,548/12,343 bonds)
- **0.01 per million tolerance** for institutional accuracy
- **13 enhanced metrics** per bond calculation

### Response Times
- **Production**: <1 second (optimized deployment)
- **Cold start**: Previously 10+ seconds, now eliminated with embedded databases