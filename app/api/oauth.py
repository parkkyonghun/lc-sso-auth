from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from urllib.parse import urlencode

from ..core.database import get_db
from ..core.security import check_rate_limit
from ..schemas.application import AuthorizeRequest, TokenRequest, TokenResponse, ConsentRequest
from ..services.oauth_service import OAuthService
from .auth import get_current_user

router = APIRouter(tags=["OAuth 2.0"])
import os
from pathlib import Path

# Get the absolute path to the templates directory
templates_dir = os.path.join(Path(__file__).parent.parent, "templates")
templates = Jinja2Templates(directory=templates_dir)

@router.get("/authorize")
async def authorize(
    request: Request,
    response_type: str,
    client_id: str,
    redirect_uri: str,
    scope: Optional[str] = "openid profile email",
    state: Optional[str] = None,
    nonce: Optional[str] = None,
    code_challenge: Optional[str] = None,
    code_challenge_method: Optional[str] = None,
    user_id: Optional[str] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """OAuth 2.0 Authorization endpoint"""
    # Rate limiting
    client_ip = request.client.host
    if not check_rate_limit(client_ip, "authorize", limit=20, window=300):  # 20 requests per 5 minutes
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many authorization requests. Please try again later."
        )
    
    # Create authorization request
    auth_request = AuthorizeRequest(
        response_type=response_type,
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=scope,
        state=state,
        nonce=nonce,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method
    )
    
    oauth_service = OAuthService(db)
    
    try:
        result = oauth_service.handle_authorization_request(auth_request, user_id)
        
        if result["action"] == "login_required":
            # Redirect to login with current URL as next parameter
            login_url = f"/auth/login?next={request.url}"
            return RedirectResponse(url=login_url, status_code=302)
        
        elif result["action"] == "consent_required":
            # Show consent page
            return templates.TemplateResponse(
                "consent.html",
                {
                    "request": request,
                    "client_name": result["client_name"],
                    "client_description": result.get("client_description"),
                    "requested_scopes": result["requested_scopes"],
                    "client_logo": result.get("client_logo"),
                    "privacy_policy_url": result.get("privacy_policy_url"),
                    "terms_of_service_url": result.get("terms_of_service_url"),
                    "client_id": client_id,
                    "scope": scope,
                    "redirect_uri": redirect_uri,
                    "state": state
                }
            )
        
        elif result["action"] == "redirect":
            # Build redirect URL with authorization code
            params = {"code": result["code"]}
            if result.get("state"):
                params["state"] = result["state"]
            
            redirect_url = f"{result['redirect_uri']}?{urlencode(params)}"
            return RedirectResponse(url=redirect_url, status_code=302)
    
    except HTTPException as e:
        # Redirect to client with error
        error_params = {
            "error": "server_error",
            "error_description": e.detail
        }
        if state:
            error_params["state"] = state
        
        error_url = f"{redirect_uri}?{urlencode(error_params)}"
        return RedirectResponse(url=error_url, status_code=302)

@router.post("/consent")
async def consent(
    request: Request,
    client_id: str = Form(...),
    scope: str = Form(...),
    redirect_uri: str = Form(...),
    state: Optional[str] = Form(None),
    consent: bool = Form(...),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Handle user consent for OAuth authorization"""
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "not_authenticated", "detail": "Authentication required"}
        )
    
    oauth_service = OAuthService(db)
    
    try:
        result = oauth_service.handle_consent(
            client_id=client_id,
            scope=scope,
            user_id=user_id,
            consent=consent,
            redirect_uri=redirect_uri,
            state=state
        )
        
        # Build redirect URL
        params = {}
        if result.get("code"):
            params["code"] = result["code"]
        if result.get("error"):
            params["error"] = result["error"]
            params["error_description"] = result["error_description"]
        if result.get("state"):
            params["state"] = result["state"]
        
        redirect_url = f"{result['redirect_uri']}?{urlencode(params)}"
        return RedirectResponse(url=redirect_url, status_code=302)
    
    except HTTPException as e:
        # Redirect to client with error
        error_params = {
            "error": "server_error",
            "error_description": e.detail
        }
        if state:
            error_params["state"] = state
        
        error_url = f"{redirect_uri}?{urlencode(error_params)}"
        return RedirectResponse(url=error_url, status_code=302)

@router.post("/token", response_model=TokenResponse)
async def token(
    request: Request,
    grant_type: str = Form(...),
    code: Optional[str] = Form(None),
    redirect_uri: Optional[str] = Form(None),
    client_id: str = Form(...),
    client_secret: Optional[str] = Form(None),
    code_verifier: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None),
    scope: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """OAuth 2.0 Token endpoint"""
    # Rate limiting
    client_ip = request.client.host
    if not check_rate_limit(client_ip, "token", limit=30, window=300):  # 30 requests per 5 minutes
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"error": "rate_limit_exceeded", "detail": "Too many token requests. Please try again later."}
        )
    
    # Create token request
    token_request = TokenRequest(
        grant_type=grant_type,
        code=code,
        redirect_uri=redirect_uri,
        client_id=client_id,
        client_secret=client_secret,
        code_verifier=code_verifier,
        refresh_token=refresh_token,
        scope=scope
    )
    
    oauth_service = OAuthService(db)
    return oauth_service.handle_token_request(token_request)

@router.get("/userinfo")
async def userinfo(
    request: Request,
    authorization: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """OAuth 2.0 UserInfo endpoint"""
    # Extract access token from Authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid_authorization_header", "detail": "Missing or invalid authorization header"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token = authorization[7:]  # Remove "Bearer " prefix
    
    oauth_service = OAuthService(db)
    return oauth_service.get_user_info(access_token)

@router.get("/.well-known/openid-configuration")
async def openid_configuration(request: Request):
    """OpenID Connect Discovery endpoint"""
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    
    oauth_service = OAuthService(None)  # No DB needed for this endpoint
    return oauth_service.get_openid_configuration(base_url)

@router.get("/.well-known/jwks.json")
async def jwks():
    """JSON Web Key Set endpoint"""
    # This would typically return the public keys used to verify JWT signatures
    # For now, return an empty key set
    return {
        "keys": []
    }

@router.get("/health")
async def health_check():
    """Health check endpoint for OAuth service"""
    return {
        "status": "healthy",
        "service": "oauth",
        "version": "1.0.0"
    }