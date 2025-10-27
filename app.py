#!/usr/bin/env python3
"""
Flask application entry point for API mode.

Usage:
    # Development:
    python app.py
    
    # Production:
    gunicorn app:app --bind 0.0.0.0:8080
"""

import os
from routes.api import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

