#!/usr/bin/env python3
"""
Simple startup script for Flask Admin Panel
"""

import argparse
from flask_admin.main_app import app

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Flask Admin Panel for SSO System')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the application on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    app.run(debug=args.debug, host='0.0.0.0', port=args.port)
