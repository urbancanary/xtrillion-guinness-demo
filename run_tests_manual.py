#!/usr/bin/env python3
"""
Manual test runner for XTrillion API
Run this script anytime to test the API and see results
"""

import subprocess
import sys
import os
import json
from datetime import datetime

def main():
    print("🧪 XTrillion API Manual Test Runner")
    print("=" * 50)
    
    # Check if daily_test_suite.py exists
    if not os.path.exists("daily_test_suite.py"):
        print("❌ Error: daily_test_suite.py not found!")
        print("Please run this script from the google_analysis10 directory")
        sys.exit(1)
    
    # Ask user for options
    print("\nTest Options:")
    print("1. Run tests only (no email)")
    print("2. Run tests and send email (only if failures)")
    print("3. Run tests and always send email")
    print("4. Configure email settings")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "4":
        configure_email()
        return
    
    # Set environment variables based on choice
    env = os.environ.copy()
    
    if choice == "3":
        env["ALWAYS_SEND_EMAIL"] = "true"
    
    if choice in ["2", "3"]:
        # Load email config if exists
        if os.path.exists(".email_config.json"):
            with open(".email_config.json", "r") as f:
                email_config = json.load(f)
                env.update(email_config)
        else:
            print("\n⚠️  No email configuration found!")
            print("Run option 4 to configure email settings")
            if input("Continue without email? (y/n): ").lower() != "y":
                return
    
    # Run tests
    print(f"\n🚀 Running tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            [sys.executable, "daily_test_suite.py"],
            env=env,
            capture_output=False
        )
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed!")
            
        # Show results file location
        results_file = f"test_results_production_{datetime.now().strftime('%Y-%m-%d')}.json"
        if os.path.exists(results_file):
            print(f"\n📊 Detailed results saved to: {results_file}")
            
            # Show summary
            with open(results_file, "r") as f:
                results = json.load(f)
                print(f"\nSummary:")
                print(f"  Total Tests: {results['total_tests']}")
                print(f"  Passed: {results['passed']}")
                print(f"  Failed: {results['failed']}")
                print(f"  Success Rate: {results['success_rate']:.1f}%")
                
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")

def configure_email():
    """Configure email settings"""
    print("\n📧 Email Configuration")
    print("-" * 50)
    print("For Gmail, you need an App Password (not your regular password)")
    print("1. Enable 2-factor authentication")
    print("2. Generate app password at: https://myaccount.google.com/apppasswords")
    print()
    
    config = {}
    config["SENDER_EMAIL"] = input("Sender email address: ").strip()
    config["SENDER_PASSWORD"] = input("Sender password/app password: ").strip()
    config["RECIPIENT_EMAIL"] = input("Recipient email address: ").strip()
    config["SMTP_SERVER"] = input("SMTP server (default: smtp.gmail.com): ").strip() or "smtp.gmail.com"
    config["SMTP_PORT"] = input("SMTP port (default: 587): ").strip() or "587"
    
    # Save config
    with open(".email_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("\n✅ Email configuration saved!")
    print("Note: .email_config.json is git-ignored for security")
    
    # Test email
    if input("\nSend test email? (y/n): ").lower() == "y":
        env = os.environ.copy()
        env.update(config)
        env["ALWAYS_SEND_EMAIL"] = "true"
        
        print("\n📤 Sending test email...")
        subprocess.run([sys.executable, "daily_test_suite.py"], env=env)

if __name__ == "__main__":
    main()