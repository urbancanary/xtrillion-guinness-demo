#!/usr/bin/env python3
"""
Authentication utilities for XTrillion API
Provides environment-aware API key enforcement
"""

import os
import logging
from functools import wraps
from flask import request, jsonify

logger = logging.getLogger(__name__)

def require_api_key_environment_aware(valid_keys):
    """
    Environment-aware API key authentication
    
    - Production & Maia-dev: STRICT - requires valid API key
    - Development (RMB): NO AUTH - your personal environment
    - Configurable per environment
    
    Args:
        valid_keys: Dictionary of valid API keys for this environment
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get current service
            service_name = os.environ.get('GAE_SERVICE', 'unknown')
            
            # RMB Development environment - NO authentication required
            if service_name == 'development':
                logger.debug("🧪 RMB Development environment - bypassing API key check")
                return f(*args, **kwargs)
            
            # Production and Maia-dev - STRICT authentication
            api_key = request.headers.get('X-API-Key')
            
            if not api_key:
                logger.warning(f"❌ No API key provided for {request.endpoint} in {service_name}")
                return jsonify({
                    "status": "error",
                    "code": 401,
                    "message": "API key required in X-API-Key header",
                    "environment": service_name
                }), 401
            
            if api_key not in valid_keys:
                logger.warning(f"❌ Invalid API key '{api_key[:10]}...' for {request.endpoint} in {service_name}")
                return jsonify({
                    "status": "error",
                    "code": 401,
                    "message": "Invalid API key",
                    "environment": service_name
                }), 401
            
            # Valid key - log usage
            key_info = valid_keys.get(api_key, {})
            if isinstance(key_info, dict):
                key_name = key_info.get('name', 'Unknown')
                key_user = key_info.get('user', 'unknown')
            else:
                key_name = key_info
                key_user = 'unknown'
                
            logger.info(f"✅ API key '{key_name}' used by {key_user} for {request.endpoint} in {service_name}")
            
            # Add key info to request context for potential usage tracking
            request.api_key_info = {
                'key': api_key,
                'name': key_name,
                'user': key_user,
                'environment': service_name
            }
            
            return f(*args, **kwargs)
            
        return decorated_function
    return decorator

def require_maia_api_key(f):
    """
    Specific decorator for Maia's API key
    Single key works in both production and maia-dev
    """
    # Define Maia's single API key
    MAIA_KEYS = {
        'gax10_maia_7k9d2m5p8w1e6r4t3y2x': {'name': 'Maia API Key', 'user': 'maia', 'permissions': 'full'}
    }
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        service_name = os.environ.get('GAE_SERVICE', 'unknown')
        
        # Your dev environment - no auth needed
        if service_name == 'development':
            return f(*args, **kwargs)
        
        # Check for Maia's specific keys
        api_key = request.headers.get('X-API-Key')
        
        if not api_key or api_key not in MAIA_KEYS:
            return jsonify({
                "status": "error",
                "code": 401,
                "message": "Valid Maia API key required",
                "contact": "Contact RMB for API access"
            }), 401
            
        # Log Maia's usage for billing/tracking
        key_info = MAIA_KEYS[api_key]
        logger.info(f"💰 Maia API usage: {key_info['name']} accessing {request.endpoint}")
        
        return f(*args, **kwargs)
        
    return decorated_function

def get_auth_decorator_for_environment():
    """
    Returns the appropriate auth decorator based on environment
    This allows dynamic auth requirements
    """
    service_name = os.environ.get('GAE_SERVICE', 'unknown')
    
    if service_name == 'development':
        # No auth for your dev environment
        def no_auth(f):
            return f
        return no_auth
    else:
        # Strict auth for production/maia-dev
        from google_analysis10_api import VALID_API_KEYS
        return require_api_key_environment_aware(VALID_API_KEYS)