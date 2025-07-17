"""
Common API utilities and dependencies
"""

from .dependencies import get_api_version, validate_api_version, get_api_version_middleware

__all__ = ["get_api_version", "validate_api_version", "get_api_version_middleware"]
