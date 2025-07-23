# 6-Way Method Benchmark vs Bloomberg
Generated: 2025-07-22 00:46:36
Settlement Date: 2025-06-30

## Executive Summary

**Treasury Fix Validation**: Method 1 vs Method 2 comparison for Treasury bonds
**Total Bonds Tested**: 25
**Bloomberg Baseline**: Professional QuantLib calculations with ActualActual(ISDA)

## 📊 Accuracy Summary Table

| Method | Success Rate | Yield MAE (%) | Duration MAE (yrs) | Within 1bp | Within 0.1yr |
|--------|--------------|---------------|-------------------|------------|--------------|
| Method_1_Direct_Local_ISIN | 0/25 | 0.0000 | 0.0000 | 0 | 0 |
| Method_2_Direct_Local_Parser | 25/25 | 0.0232 | 0.0974 | 7 | 17 |
| Method_3_Local_API_ISIN_NotImplemented | 0/25 | 0.0000 | 0.0000 | 0 | 0 |
| Method_4_Local_API_Parser_NotImplemented | 0/25 | 0.0000 | 0.0000 | 0 | 0 |
| Method_5_Cloud_API_ISIN_NotImplemented | 0/25 | 0.0000 | 0.0000 | 0 | 0 |
| Method_6_Cloud_API_Parser_NotImplemented | 0/25 | 0.0000 | 0.0000 | 0 | 0 |

## 🎯 Treasury Bond Focus (Validation of Fix)

**Key Bond**: US912810TJ79 (US TREASURY N/B, 3%, 15-Aug-2052)
- **Bloomberg**: 4.89916% yield, 16.35658 years duration
- **Expected**: Both Method 1 and Method 2 should match closely after Treasury fix


### Treasury Bond Results:
- **Bloomberg**: 4.89916% yield, 16.35658 years
- **Method 1**: 0.00000% yield, 0.00000 years
- **Method 2**: 4.89976% yield, 16.59994 years

### Method 1 vs Method 2 Differences:
- **Yield Difference**: 4.89976% (489.98 bps)
- **Duration Difference**: 16.59994 years


## 📋 Complete Results Table

| # | ISIN | Name | Bloomberg Yield | M1 Yield | M2 Yield | Bloomberg Duration | M1 Duration | M2 Duration |
|---|------|------|----------------|----------|----------|-------------------|-------------|-------------|
| 1 | US912810TJ79 | US TREASURY N/B, 3%, 15-Aug-2052 | 4.899 | 0.000 | 4.900 | 16.357 | 0.000 | 16.600 |
| 2 | XS2249741674 | GALAXY PIPELINE, 3.25%, 30-Sep-2040 | 5.396 | 0.000 | 5.420 | 11.223 | 0.000 | 11.176 |
| 3 | XS1709535097 | ABU DHABI CRUDE, 4.6%, 02-Nov-2047 | 5.424 | 0.000 | 5.433 | 13.211 | 0.000 | 13.196 |
| 4 | XS1982113463 | SAUDI ARAB OIL, 4.25%, 16-Apr-2039 | 5.599 | 0.000 | 5.616 | 9.931 | 0.000 | 9.900 |
| 5 | USP37466AS18 | EMPRESA METRO, 4.7%, 07-May-2050 | 6.266 | 0.000 | 6.280 | 13.182 | 0.000 | 13.169 |
| 6 | USP3143NAH72 | CODELCO INC, 6.15%, 24-Oct-2036 | 5.949 | 0.000 | 5.953 | 8.017 | 0.000 | 8.013 |
| 7 | USP30179BR86 | COMISION FEDERAL, 6.264%, 15-Feb-2052 | 7.442 | 0.000 | 7.456 | 11.587 | 0.000 | 11.784 |
| 8 | US195325DX04 | COLOMBIA REP OF, 3.875%, 15-Feb-2061 | 7.836 | 0.000 | 7.867 | 12.980 | 0.000 | 13.213 |
| 9 | US279158AJ82 | ECOPETROL SA, 5.875%, 28-May-2045 | 9.282 | 0.000 | 9.321 | 9.804 | 0.000 | 9.747 |
| 10 | USP37110AM89 | EMPRESA NACIONAL, 4.5%, 14-Sep-2047 | 6.543 | 0.000 | 6.564 | 12.382 | 0.000 | 12.451 |
| 11 | XS2542166231 | GREENSAIF PIPELI, 6.129%, 23-Feb-2038 | 5.787 | 0.000 | 5.789 | 8.614 | 0.000 | 8.697 |
| 12 | XS2167193015 | STATE OF ISRAEL, 3.8%, 13-May-2060 | 6.338 | 0.000 | 6.355 | 15.268 | 0.000 | 15.267 |
| 13 | XS1508675508 | SAUDI INT BOND, 4.5%, 26-Oct-2046 | 5.967 | 0.000 | 5.983 | 12.602 | 0.000 | 12.580 |
| 14 | XS1807299331 | KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048 | 7.060 | 0.000 | 7.070 | 11.448 | 0.000 | 11.484 |
| 15 | US91086QAZ19 | UNITED MEXICAN, 5.75%, 12-Oct-2110 | 7.375 | 0.000 | 7.381 | 13.368 | 0.000 | 13.547 |
| 16 | USP6629MAD40 | MEXICO CITY ARPT, 5.5%, 31-Jul-2047 | 7.070 | 0.000 | 7.085 | 11.379 | 0.000 | 11.575 |
| 17 | US698299BL70 | PANAMA, 3.87%, 23-Jul-2060 | 7.327 | 0.000 | 7.350 | 13.576 | 0.000 | 13.875 |
| 18 | US71654QDF63 | PETROLEOS MEXICA, 6.95%, 28-Jan-2060 | 9.876 | 0.000 | 9.900 | 9.715 | 0.000 | 10.042 |
| 19 | US71654QDE98 | PETROLEOS MEXICA, 5.95%, 28-Jan-2031 | 8.327 | 0.000 | 8.386 | 4.465 | 0.000 | 4.476 |
| 20 | XS2585988145 | GACI FIRST INVST, 5.125%, 14-Feb-2053 | 6.228 | 0.000 | 6.239 | 13.333 | 0.000 | 13.514 |
| 21 | XS1959337749 | QATAR STATE OF, 4.817%, 14-Mar-2049 | 5.585 | 0.000 | 5.593 | 13.261 | 0.000 | 13.352 |
| 22 | XS2233188353 | QNB FINANCE LTD, 1.625%, 22-Sep-2025 | 5.021 | 0.000 | 5.188 | 0.225 | 0.000 | 0.214 |
| 23 | XS2359548935 | QATAR ENERGY, 3.125%, 12-Jul-2041 | 5.628 | 0.000 | 5.655 | 11.515 | 0.000 | 11.569 |
| 24 | XS0911024635 | SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043 | 5.663 | 0.000 | 5.671 | 11.238 | 0.000 | 11.261 |
| 25 | USP0R80BAG79 | SITIOS, 5.375%, 04-Apr-2032 | 5.870 | 0.000 | 5.883 | 5.510 | 0.000 | 5.500 |

## 🔍 Error Analysis

### Yield Differences (vs Bloomberg)

| ISIN | Bloomberg | Method 1 | Method 2 | M1 Error (bps) | M2 Error (bps) |
|------|-----------|----------|----------|----------------|----------------|
| US912810TJ79 | 4.899 | 0.000 | 4.900 | 99900.0 | 0.1 |
| XS2249741674 | 5.396 | 0.000 | 5.420 | 99900.0 | 2.4 |
| XS1709535097 | 5.424 | 0.000 | 5.433 | 99900.0 | 0.9 |
| XS1982113463 | 5.599 | 0.000 | 5.616 | 99900.0 | 1.7 |
| USP37466AS18 | 6.266 | 0.000 | 6.280 | 99900.0 | 1.4 |
| USP3143NAH72 | 5.949 | 0.000 | 5.953 | 99900.0 | 0.4 |
| USP30179BR86 | 7.442 | 0.000 | 7.456 | 99900.0 | 1.4 |
| US195325DX04 | 7.836 | 0.000 | 7.867 | 99900.0 | 3.0 |
| US279158AJ82 | 9.282 | 0.000 | 9.321 | 99900.0 | 3.9 |
| USP37110AM89 | 6.543 | 0.000 | 6.564 | 99900.0 | 2.1 |
| XS2542166231 | 5.787 | 0.000 | 5.789 | 99900.0 | 0.2 |
| XS2167193015 | 6.338 | 0.000 | 6.355 | 99900.0 | 1.7 |
| XS1508675508 | 5.967 | 0.000 | 5.983 | 99900.0 | 1.6 |
| XS1807299331 | 7.060 | 0.000 | 7.070 | 99900.0 | 1.1 |
| US91086QAZ19 | 7.375 | 0.000 | 7.381 | 99900.0 | 0.6 |
| USP6629MAD40 | 7.070 | 0.000 | 7.085 | 99900.0 | 1.5 |
| US698299BL70 | 7.327 | 0.000 | 7.350 | 99900.0 | 2.3 |
| US71654QDF63 | 9.876 | 0.000 | 9.900 | 99900.0 | 2.4 |
| US71654QDE98 | 8.327 | 0.000 | 8.386 | 99900.0 | 5.8 |
| XS2585988145 | 6.228 | 0.000 | 6.239 | 99900.0 | 1.1 |
| XS1959337749 | 5.585 | 0.000 | 5.593 | 99900.0 | 0.8 |
| XS2233188353 | 5.021 | 0.000 | 5.188 | 99900.0 | 16.7 |
| XS2359548935 | 5.628 | 0.000 | 5.655 | 99900.0 | 2.7 |
| XS0911024635 | 5.663 | 0.000 | 5.671 | 99900.0 | 0.8 |
| USP0R80BAG79 | 5.870 | 0.000 | 5.883 | 99900.0 | 1.3 |

## 💡 Key Insights

1. **Treasury Fix Validation**: Methods 1 and 2 should now show identical results for Treasury bonds
2. **Best Performing Method**: Look for lowest MAE values
3. **Production Readiness**: Methods with >90% success rate and <1bp average error
4. **Implementation Priority**: Focus on methods with proven accuracy

## ⚠️ Notes

- **Method 3-6**: May show placeholder results if API endpoints not available
- **Spread Calculations**: May vary between methods due to different Treasury curve implementations
- **Settlement Date**: All calculations use {self.settlement_date} for consistency
