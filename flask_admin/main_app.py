#!/usr/bin/env python3
"""
Flask Admin Panel for SSO System
A comprehensive web interface for managing users, applications, and system settings.

Refactored into modular components for better maintainability.
"""

from flask import Flask
from config import Config
from api_client import api_client
from datetime import datetime



# Import route blueprints
from routes.main import main_bp
from routes.users import users_bp
from routes.applications import applications_bp
from routes.roles import roles_bp
from routes.organization import organization_bp
from routes.analytics import analytics_bp


def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(applications_bp)
    app.register_blueprint(roles_bp)
    app.register_blueprint(organization_bp)
    app.register_blueprint(analytics_bp)

    @app.template_filter('datetime')
    def format_datetime(value, format="%Y-%m-%d %H:%M:%S"):
        if isinstance(value, datetime):
            return value.strftime(format)
        return value
    
    @app.route('/health')
    def health_check():
        return 'OK', 200

    return app


# Create app instance
app = create_app()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Flask Admin Panel for SSO System')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the application on')
    args = parser.parse_args()

    app.run(debug=True, host='0.0.0.0', port=args.port)
