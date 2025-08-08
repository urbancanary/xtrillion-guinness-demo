#!/usr/bin/env python3
"""
Environment Info Endpoint
Add this to your API to identify which environment is responding
"""

import os
from datetime import datetime
import socket

def add_environment_endpoints(app):
    """Add environment identification endpoints to Flask app"""
    
    @app.route('/env', methods=['GET'])
    @app.route('/environment', methods=['GET'])
    def environment_info():
        """
        Environment identification endpoint
        Shows clearly which service is responding
        """
        from flask import request
        
        # Get environment variables
        service_name = os.environ.get('GAE_SERVICE', 'unknown')
        version = os.environ.get('GAE_VERSION', 'unknown')
        env_name = os.environ.get('ENVIRONMENT', 'unknown')
        instance_id = os.environ.get('GAE_INSTANCE', 'local')
        
        # Get the host being accessed
        accessed_host = request.host
        
        # Enhanced mapping that considers the domain being accessed
        if 'api.x-trillion.ai' in accessed_host:
            if service_name == 'default':
                friendly_name = '🌍 PRODUCTION (via api.x-trillion.ai)'
            else:
                friendly_name = f'⚠️ WRONG ROUTING! {service_name} service on production domain!'
        elif 'api-dev.x-trillion.ai' in accessed_host:
            if service_name == 'maia-dev':
                friendly_name = '👥 MAIA DEVELOPMENT (via api-dev.x-trillion.ai)'
            else:
                friendly_name = f'⚠️ WRONG ROUTING! {service_name} service on maia-dev domain!'
        else:
            # Fallback to service-based naming
            service_map = {
                'default': '🌍 PRODUCTION',
                'maia-dev': '👥 MAIA DEVELOPMENT',
                'development': '🧪 RMB DEVELOPMENT',
                'hotfix': '🚨 HOTFIX ENVIRONMENT'
            }
            friendly_name = service_map.get(service_name, service_name.upper())
        
        # Color coding for terminal/logs
        color_map = {
            'default': '\033[91m',      # Red for production
            'maia-dev': '\033[93m',     # Yellow for Maia
            'development': '\033[92m',   # Green for your dev
            'hotfix': '\033[95m'        # Magenta for hotfix
        }
        color = color_map.get(service_name, '\033[0m')
        reset = '\033[0m'
        
        # Warning for production
        warning = ""
        if service_name == 'default':
            warning = "⚠️  WARNING: This is PRODUCTION! Be careful with deployments!"
        
        # Build response
        response = {
            'environment': {
                'service': service_name,
                'friendly_name': friendly_name,
                'version': version,
                'environment_var': env_name,
                'instance': instance_id,
                'warning': warning
            },
            'urls': {
                'expected_url': get_expected_url(service_name),
                'actual_host': request.host
            },
            'deployment': {
                'deployed_at': get_deployment_time(version),
                'deploy_command': get_deploy_command(service_name)
            },
            'visual': {
                'banner': f"{color}{friendly_name}{reset}",
                'emoji': get_service_emoji(service_name)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Log for visibility
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"{color}Environment Check: {friendly_name}{reset}")
        
        from flask import jsonify, request
        return jsonify(response)
    
    @app.route('/env/banner', methods=['GET'])
    def environment_banner():
        """Simple text banner for quick identification"""
        from flask import request
        
        service_name = os.environ.get('GAE_SERVICE', 'unknown')
        version = os.environ.get('GAE_VERSION', 'unknown')
        accessed_host = request.host
        
        # Enhanced banners that show the accessed domain
        if 'api.x-trillion.ai' in accessed_host:
            if service_name == 'default':
                banner = """
╔══════════════════════════════════════════╗
║        🌍 PRODUCTION ENVIRONMENT 🌍       ║
║         api.x-trillion.ai                ║
║         DO NOT DEPLOY DIRECTLY!          ║
║         Service: default                 ║
║         Version: {:<24}║
╚══════════════════════════════════════════╝
"""
            else:
                banner = """
╔══════════════════════════════════════════╗
║          ⚠️  ROUTING ERROR! ⚠️            ║
║     {} service on api.x-trillion.ai      ║
║         CHECK DISPATCH RULES!            ║
╚══════════════════════════════════════════╝
""".format(service_name)
        elif 'api-dev.x-trillion.ai' in accessed_host:
            if service_name == 'maia-dev':
                banner = """
╔══════════════════════════════════════════╗
║      👥 MAIA DEVELOPMENT ENVIRONMENT     ║
║         api-dev.x-trillion.ai            ║
║         Safe for Maia testing            ║
║         Service: maia-dev                ║
║         Version: {:<24}║
╚══════════════════════════════════════════╝
"""
            else:
                banner = """
╔══════════════════════════════════════════╗
║          ⚠️  ROUTING ERROR! ⚠️            ║
║   {} service on api-dev.x-trillion.ai   ║
║         CHECK DISPATCH RULES!            ║
╚══════════════════════════════════════════╝
""".format(service_name)
        else:
            # Use original banners for direct App Engine URLs
            banners = {
            'default': """
╔══════════════════════════════════════════╗
║        🌍 PRODUCTION ENVIRONMENT 🌍       ║
║         DO NOT DEPLOY DIRECTLY!          ║
║         Service: default                 ║
║         Version: {:<24}║
╚══════════════════════════════════════════╝
""",
            'maia-dev': """
╔══════════════════════════════════════════╗
║      👥 MAIA DEVELOPMENT ENVIRONMENT     ║
║         Safe for Maia testing            ║
║         Service: maia-dev                ║
║         Version: {:<24}║
╚══════════════════════════════════════════╝
""",
            'development': """
╔══════════════════════════════════════════╗
║      🧪 RMB DEVELOPMENT ENVIRONMENT      ║
║         Your personal playground         ║
║         Service: development             ║
║         Version: {:<24}║
╚══════════════════════════════════════════╝
""",
            'hotfix': """
╔══════════════════════════════════════════╗
║       🚨 HOTFIX ENVIRONMENT 🚨           ║
║         Emergency fixes only!            ║
║         Service: hotfix                  ║
║         Version: {:<24}║
╚══════════════════════════════════════════╝
"""
        }
            
            banner = banners.get(service_name, f"Unknown Service: {service_name}")
        
        # Format the banner with version if it has a placeholder
        if '{}' in banner or '{:' in banner:
            truncated_version = version[:24]
            banner = banner.format(truncated_version)
            
        from flask import Response
        return Response(banner, mimetype='text/plain')

def get_expected_url(service_name):
    """Get the expected URL for each service"""
    urls = {
        'default': 'https://api.x-trillion.ai',
        'maia-dev': 'https://api-dev.x-trillion.ai',
        'development': 'https://development-dot-future-footing-414610.uc.r.appspot.com',
        'hotfix': 'https://hotfix-dot-future-footing-414610.uc.r.appspot.com'
    }
    return urls.get(service_name, 'unknown')

def get_deployment_time(version):
    """Extract deployment time from version string"""
    # Versions usually have format like "maia-20250807-123456"
    try:
        if '-' in version and len(version) > 15:
            date_part = version.split('-')[-2]
            time_part = version.split('-')[-1]
            if len(date_part) == 8 and len(time_part) == 6:
                year = date_part[:4]
                month = date_part[4:6]
                day = date_part[6:8]
                hour = time_part[:2]
                minute = time_part[2:4]
                second = time_part[4:6]
                return f"{year}-{month}-{day} {hour}:{minute}:{second}"
    except:
        pass
    return version

def get_deploy_command(service_name):
    """Get the deployment command for each service"""
    commands = {
        'default': 'gcloud app deploy app.yaml (⚠️  REQUIRES APPROVAL!)',
        'maia-dev': './deploy.sh maia-dev',
        'development': 'gcloud app deploy app.development.yaml',
        'hotfix': './deploy.sh hotfix'
    }
    return commands.get(service_name, 'unknown')

def get_service_emoji(service_name):
    """Get emoji for each service"""
    emojis = {
        'default': '🌍',
        'maia-dev': '👥',
        'development': '🧪',
        'hotfix': '🚨'
    }
    return emojis.get(service_name, '❓')

# Usage in your API files:
# from environment_info import add_environment_endpoints
# add_environment_endpoints(app)