# API Key Migration Plan

## Current State (INCORRECT)
- **Production**: Soft auth (allows without key) ❌
- **Maia-dev**: Soft auth (allows without key) ❌
- **RMB Dev**: Strict auth (requires key) ❌

## Target State (CORRECT)
- **Production**: STRICT auth - Maia must use paid API key ✓
- **Maia-dev**: STRICT auth - Control Maia's test access ✓
- **RMB Dev**: NO auth - Your personal playground ✓

## Implementation Steps

### Step 1: Update Development Environment (IMMEDIATE)
Remove API key requirements from your dev environment:

```python
# In google_analysis10_api_dev.py
# Replace @require_api_key with:
from auth_utils import get_auth_decorator_for_environment
auth_required = get_auth_decorator_for_environment()

# Then use @auth_required instead of @require_api_key
```

### Step 2: Create Maia-Specific Keys
```python
# Maia's production keys (they pay for these)
MAIA_PRODUCTION_KEYS = {
    'gax10_maia_prod_7k9d2m5p8w1e6r4t': {
        'name': 'Maia Production Key',
        'user': 'maia',
        'tier': 'paid',
        'requests_per_month': 100000
    }
}

# Maia's test key (limited access)
MAIA_TEST_KEYS = {
    'gax10_maia_test_4n8s6k2x7p9v5m1w': {
        'name': 'Maia Testing Key', 
        'user': 'maia',
        'tier': 'test',
        'requests_per_day': 1000
    }
}
```

### Step 3: Update Production API
Change from soft to strict authentication:

```python
# In google_analysis10_api.py
# Replace @require_api_key_soft with:
from auth_utils import require_api_key_environment_aware
auth_required = require_api_key_environment_aware(VALID_API_KEYS)

# Use @auth_required on all endpoints
```

### Step 4: Add Usage Tracking
Track API usage for billing:

```python
# Log all Maia API calls
if request.api_key_info['user'] == 'maia':
    log_api_usage(
        key=request.api_key_info['key'],
        endpoint=request.endpoint,
        timestamp=datetime.now()
    )
```

### Step 5: Deployment Order
1. Deploy to RMB dev first (remove auth requirement)
2. Test thoroughly
3. Deploy to Maia-dev (add strict auth)
4. Give Maia their test key
5. Once verified, deploy to production

## Business Benefits
1. **Revenue Protection**: Maia can't use API without paying
2. **Usage Tracking**: Monitor Maia's usage for billing
3. **Development Freedom**: You can test freely in your environment
4. **Access Control**: Different keys for test vs production

## API Key Distribution
- Give Maia only their specific keys
- Don't share the general keys (demo, inst, etc.)
- Rotate keys periodically for security

## Monitoring
Add alerts for:
- Unauthorized access attempts
- Excessive usage by any key
- Failed authentication spikes