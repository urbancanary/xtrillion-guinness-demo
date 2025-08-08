# 🧪 Automated Testing Guide for XTrillion Bond Analytics API

This guide explains how to set up and use automated daily testing with email notifications to catch bugs before they affect your software company partner.

## 📋 Overview

The automated testing system:
- ✅ Runs comprehensive API tests daily
- ✅ Sends email notifications only when tests fail
- ✅ Monitors performance to catch degradation
- ✅ Tests both production and development environments
- ✅ Provides detailed HTML reports with test results

## 🚀 Quick Start

### 1. Manual Testing (Immediate)

Run tests right now to see current API status:

```bash
python3 run_tests_manual.py
```

This will:
- Show a menu to select test options
- Run all API tests
- Display results in the terminal
- Optionally send email notifications

### 2. Daily Automated Testing Setup

#### Option A: Google Cloud Scheduler (Recommended)

```bash
# One-time setup
./setup_daily_testing.sh
```

This will:
- Set up Google Cloud Scheduler to run tests daily at 8 AM EST
- Create a Cloud Function to execute tests
- Configure email notifications
- Store credentials securely in Google Secret Manager

#### Option B: GitHub Actions

If your code is on GitHub:
1. Add secrets to your repository:
   - `SENDER_EMAIL`: Your email address
   - `SENDER_PASSWORD`: Gmail app password
   - `RECIPIENT_EMAIL`: Where to send notifications

2. The workflow will automatically:
   - Run tests daily at 3 AM EST
   - Run tests on every push to main/develop
   - Send notifications only on failures

## 📧 Email Configuration

### Gmail Setup (Recommended)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Create a new app password for "Mail"
   - Use this password (NOT your regular Gmail password)

3. **Configure Email**:
   ```bash
   python3 run_tests_manual.py
   # Select option 4 to configure email
   ```

### What You'll Receive

When tests fail, you'll get an email like this:

```
Subject: ❌ FAILED - XTrillion API Daily Test Report - Production

Summary:
- Environment: Production
- Total Tests: 5
- Passed: 3
- Failed: 2
- Success Rate: 60.0%

Detailed Results:
┌─────────────────────┬────────┬───────────────┬──────────────────────┐
│ Test Name           │ Status │ Response Time │ Details              │
├─────────────────────┼────────┼───────────────┼──────────────────────┤
│ Health Check        │ PASSED │ 125ms         │ API is healthy       │
│ Bond Analysis       │ FAILED │ 450ms         │ Invalid YTM 25.3     │
│ Portfolio Analysis  │ PASSED │ 380ms         │ All bonds processed  │
│ Error Handling      │ PASSED │ 95ms          │ Errors handled well  │
│ Performance         │ FAILED │ N/A           │ Avg response 850ms   │
└─────────────────────┴────────┴───────────────┴──────────────────────┘
```

## 🧪 What Gets Tested

### 1. **Health Check**
- Verifies API is responding
- Checks database connections
- Validates service configuration

### 2. **Bond Analysis**
- Tests individual bond calculations
- Validates YTM, duration, and other metrics
- Checks multiple bond types (treasuries, corporates)

### 3. **Portfolio Analysis**
- Tests portfolio-level calculations
- Validates weighted averages
- Ensures all bonds process correctly

### 4. **Error Handling**
- Tests invalid inputs
- Verifies proper error messages
- Ensures graceful failure handling

### 5. **Performance Benchmarks**
- Monitors response times
- Alerts if API becomes slow (>500ms average)
- Tracks performance trends

### 6. **Baseline Calculation Comparison** ⭐ NEW
- **Detects ANY changes in calculation results**
- Uses fixed settlement date (2025-04-18) for consistency
- Compares 12 key metrics for each bond:
  - YTM, Duration, Convexity, PVBP
  - Macaulay Duration, Clean/Dirty Price
  - Accrued Interest, Annual equivalents
  - Spreads (when available)
- **Alerts on even tiny changes** (0.1 basis point for yields)
- Critical for catching unintended calculation changes

## 🎯 Baseline Calculation Management

### Understanding Baseline Testing

The baseline comparison test is **critical** for detecting unintended changes:

1. **Fixed Settlement Date**: Always uses 2025-04-18 for consistency
2. **Precision Thresholds**:
   - Yields/Spreads: 0.1 basis point (0.001%)
   - Duration: 0.01 years
   - Prices: 0.01 units

### Managing Your Baseline

```bash
# View current baseline values
python3 baseline_comparison_test.py --show-baseline

# Run comparison test (detects changes)
python3 baseline_comparison_test.py

# Update baseline after intentional changes
python3 baseline_comparison_test.py --save-baseline

# Add a new bond to baseline
python3 baseline_comparison_test.py --add-bond "AAPL 3.45 09/02/45,85.50"
```

### When to Update Baseline

Update the baseline ONLY when:
- ✅ You've intentionally fixed a calculation bug
- ✅ You've updated bond conventions/databases
- ✅ You've verified the new values are correct

Do NOT update when:
- ❌ You see unexpected changes
- ❌ You haven't verified the new values
- ❌ You're unsure why values changed

## 🔧 Customization

### Modify Test Cases

Edit `test_config.json` to add/modify test bonds:

```json
{
  "test_cases": {
    "bonds": [
      {
        "description": "AAPL 3.45 02/09/45",
        "price": 85.50,
        "name": "Apple Corporate Bond"
      }
    ]
  }
}
```

### Change Test Schedule

```bash
# Change to run at 6 AM instead of 8 AM
gcloud scheduler jobs update http xtrillion-daily-api-tests \
  --schedule="0 6 * * *" \
  --location=us-central1
```

### Performance Thresholds

Edit `daily_test_suite.py` to adjust thresholds:

```python
# Line ~300
if avg_time < 500:  # Change this to your desired threshold in ms
```

## 📊 Viewing Results

### Google Cloud Logs

```bash
# View recent test results
gcloud functions logs read xtrillion-daily-tests --limit=50

# View only errors
gcloud functions logs read xtrillion-daily-tests --filter="severity>=ERROR"
```

### Local Test Results

Test results are saved as JSON files:
- `test_results_production_2025-08-07.json`
- `test_results_development_2025-08-07.json`

## 🚨 Troubleshooting

### Tests Not Running

```bash
# Check scheduler status
gcloud scheduler jobs list --location=us-central1

# Run manually
gcloud scheduler jobs run xtrillion-daily-api-tests --location=us-central1

# Check function logs
gcloud functions logs read xtrillion-daily-tests --limit=20
```

### Email Not Sending

1. Verify credentials:
   ```bash
   python3 run_tests_manual.py
   # Choose option 4 to reconfigure
   ```

2. Check Gmail settings:
   - Ensure 2FA is enabled
   - Use app password, not regular password
   - Check spam folder

3. Test email manually:
   ```bash
   python3 -c "
   from daily_test_suite import XTrillionAPITester
   import os
   os.environ['ALWAYS_SEND_EMAIL'] = 'true'
   tester = XTrillionAPITester('production')
   summary = tester.run_all_tests()
   tester.send_email_report(summary)
   "
   ```

## 🔒 Security Best Practices

1. **Never commit credentials** - Use `.gitignore`
2. **Use Google Secret Manager** for production
3. **Rotate app passwords** periodically
4. **Limit API key permissions** to read-only

## 💡 Pro Tips

1. **Start with manual testing** to verify everything works
2. **Run tests before deployments** to catch issues early
3. **Monitor trends** - Gradual performance degradation is a warning sign
4. **Add custom tests** for your specific use cases
5. **Test both environments** if you use development for staging

## 📝 Maintenance

### Weekly
- Review test results for patterns
- Check for consistent near-failures

### Monthly
- Update test cases with new bonds
- Review and adjust performance thresholds
- Verify email notifications still work

### Quarterly
- Rotate credentials
- Review and update test coverage
- Archive old test results

## 🆘 Support

If you need help:
1. Check the logs first
2. Run manual tests to isolate issues
3. Verify API is accessible from your location
4. Check Google Cloud status page

---

**Remember**: The goal is to catch bugs before your software company partner does. Regular testing gives you confidence that the API is working correctly and performing well.