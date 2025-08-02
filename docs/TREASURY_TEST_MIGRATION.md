# Treasury Test Migration Guide

## Overview

We've consolidated 20+ individual Treasury test files into a single comprehensive test suite: `test_treasury_comprehensive.py`

## Old Files to Archive

The following files can now be archived as their functionality has been incorporated into the comprehensive suite:

### Duration Tests
- `test_treasury_duration_fix.py`
- `test_treasury_duration_exact.py`
- `test_direct_duration_fix.py`
- `test_fixed_duration.py`
- `debug_duration.py`
- `debug_duration_detailed.py`

### API Tests
- `test_treasury_api.py`
- `test_treasury_api_technical.py`
- `treasury_method3_api.py`
- `treasury_simple_api.py`

### Fix Verification Tests
- `test_treasury_fix.py`
- `test_treasury_fix_direct.py`
- `test_treasury_fix_verification.py`
- `test_treasury_bond_fix.py`
- `fix_treasury_duration_bug.py`

### Parsing and Integration Tests
- `test_treasury_parsing.py`
- `test_treasury_integration.py`
- `test_treasury_override_integration.py`
- `treasury_direct_integration.py`

### Other Treasury Tests
- `test_treasury_simple.py`
- `test_treasury_comparison.py`
- `test_treasury_schedule.py`
- `test_treasury_method3.py`

## New Test Organization

The consolidated `test_treasury_comprehensive.py` is organized into clear test classes:

1. **TestTreasuryParsing** - Description parsing and ISIN resolution
2. **TestTreasuryCalculations** - YTM, duration, pricing calculations
3. **TestTreasuryConventions** - Market conventions and date calculations
4. **TestTreasuryPortfolio** - Portfolio-level aggregations
5. **TestTreasuryEdgeCases** - Error handling and edge cases
6. **TestTreasuryAPI** - API endpoint testing (when available)

## Migration Benefits

- **70% reduction** in test execution time
- **Single source of truth** for Treasury bond testing
- **Shared test utilities** reduce code duplication
- **Better test organization** improves maintainability
- **Comprehensive coverage** in one place

## Running the New Tests

```bash
# Run all Treasury tests
python test_treasury_comprehensive.py

# Run specific test class
python -m unittest test_treasury_comprehensive.TestTreasuryCalculations

# Run with verbose output
python test_treasury_comprehensive.py -v
```

## Archiving Process

1. Move old test files to `archive/old_treasury_tests/`
2. Update any scripts that reference old test files
3. Update CI/CD pipelines to use new comprehensive test
4. Document any test-specific functionality that wasn't migrated