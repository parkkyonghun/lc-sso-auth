"""
API Version 1 Module
This module contains all V1 API endpoints with backward compatibility support.
"""

from fastapi import APIRouter
from .auth import router as auth_router
from .admin import router as admin_router
from .applications import router as applications_router
from .oauth import router as oauth_router

# Create the main V1 router
v1_router = APIRouter(prefix="/v1", tags=["v1"])

# Include all V1 routers
v1_router.include_router(auth_router, prefix="/auth", tags=["v1-auth"])
v1_router.include_router(admin_router, prefix="/admin", tags=["v1-admin"])
v1_router.include_router(applications_router, prefix="/applications", tags=["v1-applications"])
v1_router.include_router(oauth_router, prefix="/oauth", tags=["v1-oauth"])

# Export routers for backward compatibility
__all__ = ["v1_router", "auth_router", "admin_router", "applications_router", "oauth_router"]
