"""
Configuration module for Flask Admin Panel
"""

import os

class Config:
    """Application configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    FASTAPI_BASE_URL = os.environ.get('FASTAPI_BASE_URL') or 'http://localhost:8000'
    WTF_CSRF_ENABLED = True

