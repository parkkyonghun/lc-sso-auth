"""
Common dependencies for API versioning
"""

from fastapi import Request, HTTPException, status
from typing import Optional

def get_api_version(request: Request) -> str:
    """
    Extract API version from request path or headers
    """
    # Try to get version from path
    path_segments = request.url.path.strip("/").split("/")
    if len(path_segments) >= 3 and path_segments[0] == "api":
        version = path_segments[1]
        if version.startswith("v") and version[1:].isdigit():
            return version
    
    # Try to get version from Accept header
    accept_header = request.headers.get("Accept", "")
    if "application/vnd.api+json" in accept_header:
        # Extract version from Accept header like: application/vnd.api+json; version=1
        for part in accept_header.split(";"):
            if "version=" in part:
                version = part.split("=")[1].strip()
                return f"v{version}"
    
    # Try to get version from custom header
    api_version = request.headers.get("API-Version", "")
    if api_version:
        if not api_version.startswith("v"):
            api_version = f"v{api_version}"
        return api_version
    
    # Default to v1
    return "v1"

def validate_api_version(version: str) -> str:
    """
    Validate API version and return standardized format
    """
    supported_versions = ["v1"]  # Add more versions as needed
    
    if version not in supported_versions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"API version '{version}' is not supported. Supported versions: {', '.join(supported_versions)}"
        )
    
    return version

def get_api_version_middleware():
    """
    Middleware to extract and validate API version
    """
    async def middleware(request: Request, call_next):
        # Extract version
        version = get_api_version(request)
        
        # Validate version
        try:
            validated_version = validate_api_version(version)
            request.state.api_version = validated_version
        except HTTPException:
            # If version is invalid, default to v1 for backward compatibility
            request.state.api_version = "v1"
        
        response = await call_next(request)
        
        # Add version header to response
        response.headers["API-Version"] = request.state.api_version
        
        return response
    
    return middleware
