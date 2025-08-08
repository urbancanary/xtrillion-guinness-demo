# Simplified API Key Setup

## The Simple Approach

### 1. **Maia Gets ONE Key**
```
gax10_maia_7k9d2m5p8w1e6r4t3y2x
```
- Works in both production (api.x-trillion.ai) and maia-dev (api-dev.x-trillion.ai)
- They use the same key everywhere
- Easy to remember and manage

### 2. **Your Dev Environment**
- NO API key required
- Complete freedom to test and develop

### 3. **Authentication Rules**

| Environment | Service | Requires API Key? | Which Keys Work? |
|------------|---------|------------------|------------------|
| Production | default | YES ✓ | Maia's key + others |
| Maia Dev | maia-dev | YES ✓ | Maia's key + others |
| Your Dev | development | NO ✗ | None needed |

### 4. **Why This Works Better**
- **Simpler for Maia**: One key to manage
- **Easier Support**: You don't have to remember which key is for what
- **Same Security**: You still control access and can revoke if needed
- **Cleaner Code**: Less key management complexity

### 5. **Usage Tracking**
Track usage by environment:
```python
# In your logs
"Maia API Key used at api.x-trillion.ai" → Production usage
"Maia API Key used at api-dev.x-trillion.ai" → Test usage
```

### 6. **Billing**
- Bill based on total usage across both environments
- Or give them X requests/month that work anywhere
- Much simpler than managing separate quotas

### 7. **Implementation**
Just add Maia's key to the VALID_API_KEYS in production:
```python
VALID_API_KEYS = {
    'gax10_maia_7k9d2m5p8w1e6r4t3y2x': {
        'name': 'Maia Software API Access',
        'user': 'maia',
        'permissions': 'full',
        'tier': 'paid'
    },
    # ... other keys
}
```