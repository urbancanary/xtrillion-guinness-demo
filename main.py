#!/usr/bin/env python3
"""
App Engine Entry Point for Google Analysis 10 Bond Analytics API
===============================================================

This is the entry point for Google App Engine deployment.
It imports the Flask app from google_analysis10_api.py.
"""

from google_analysis10_api import app

# App Engine will automatically use this 'app' variable
if __name__ == '__main__':
    # This runs when testing locally
    app.run(host='127.0.0.1', port=8080, debug=True)
