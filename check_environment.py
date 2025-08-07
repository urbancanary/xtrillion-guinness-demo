#!/usr/bin/env python3
"""
Check which environment you're connected to
Prevents accidental deployments to wrong service
"""

import requests
import sys
import json

# Environment URLs
ENVIRONMENTS = {
    'rmb-dev': 'https://development-dot-future-footing-414610.uc.r.appspot.com',
    'maia-dev': 'https://api-dev.x-trillion.ai',
    'production': 'https://api.x-trillion.ai'
}

def check_environment(env_name=None):
    """Check one or all environments"""
    
    if env_name and env_name in ENVIRONMENTS:
        urls_to_check = {env_name: ENVIRONMENTS[env_name]}
    else:
        urls_to_check = ENVIRONMENTS
    
    print("\n🔍 Checking environments...\n")
    
    for name, url in urls_to_check.items():
        print(f"Checking {name}...")
        print(f"URL: {url}")
        
        try:
            # Try the banner endpoint for visual confirmation
            banner_response = requests.get(f"{url}/env/banner", timeout=5)
            if banner_response.status_code == 200:
                print(banner_response.text)
            
            # Get detailed info
            response = requests.get(f"{url}/env", timeout=5)
            if response.status_code == 200:
                data = response.json()
                env_info = data.get('environment', {})
                
                # Verify it's the expected service
                expected_service = {
                    'rmb-dev': 'development',
                    'maia-dev': 'maia-dev',
                    'production': 'default'
                }
                
                actual_service = env_info.get('service')
                if actual_service == expected_service.get(name):
                    print(f"✅ Correct service: {actual_service}")
                else:
                    print(f"❌ WRONG SERVICE! Expected {expected_service.get(name)}, got {actual_service}")
                
                print(f"Version: {env_info.get('version')}")
                if env_info.get('warning'):
                    print(f"⚠️  {env_info.get('warning')}")
                    
            else:
                print(f"❌ Environment endpoint not available (status: {response.status_code})")
                
        except Exception as e:
            print(f"❌ Error connecting: {e}")
        
        print("-" * 60)

def main():
    """Main function"""
    if len(sys.argv) > 1:
        env_name = sys.argv[1]
        if env_name not in ENVIRONMENTS:
            print(f"Unknown environment: {env_name}")
            print(f"Available: {', '.join(ENVIRONMENTS.keys())}")
            sys.exit(1)
        check_environment(env_name)
    else:
        check_environment()
        print("\nUsage: python check_environment.py [rmb-dev|maia-dev|production]")

if __name__ == "__main__":
    main()