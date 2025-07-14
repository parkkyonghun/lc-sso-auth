from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models.user import User
from ..models.application import Application
from ..schemas.application import AuthorizeRequest, TokenRequest, TokenResponse
from ..core.security import (
    create_auth_code, consume_auth_code, create_access_token, 
    create_id_token, decode_jwt
)
from .user_service import UserService
from .application_service import ApplicationService

class OAuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)
        self.app_service = ApplicationService(db)
    
    def handle_authorization_request(self, auth_request: AuthorizeRequest, user_id: str = None) -> Dict[str, Any]:
        """Handle OAuth 2.0 authorization request"""
        # Validate client
        app = self.app_service.get_application_by_client_id(auth_request.client_id)
        if not app or not app.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid client_id"
            )
        
        # Validate response type
        if not app.supports_response_type(auth_request.response_type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported response_type"
            )
        
        # Validate redirect URI
        if not app.is_redirect_uri_allowed(auth_request.redirect_uri):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid redirect_uri"
            )
        
        # Validate scope
        if auth_request.scope and not app.is_scope_allowed(auth_request.scope):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid scope"
            )
        
        # Check if user is authenticated
        if not user_id:
            return {
                "action": "login_required",
                "login_url": f"/login?next=/authorize",
                "client_name": app.name
            }
        
        # Get user information
        user = self.user_service.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is not active"
            )
        
        # Check if consent is required
        if app.require_consent:
            return {
                "action": "consent_required",
                "consent_url": "/consent",
                "client_name": app.name,
                "client_description": app.description,
                "requested_scopes": auth_request.scope.split() if auth_request.scope else [],
                "client_logo": app.logo_url,
                "privacy_policy_url": app.privacy_policy_url,
                "terms_of_service_url": app.terms_of_service_url
            }
        
        # Generate authorization code
        auth_code = create_auth_code(
            user_id=str(user.id),
            client_id=auth_request.client_id,
            redirect_uri=auth_request.redirect_uri,
            scope=auth_request.scope or "openid profile email"
        )
        
        return {
            "action": "redirect",
            "redirect_uri": auth_request.redirect_uri,
            "code": auth_code,
            "state": auth_request.state
        }
    
    def handle_consent(self, client_id: str, scope: str, user_id: str, consent: bool, redirect_uri: str, state: str = None) -> Dict[str, Any]:
        """Handle user consent for OAuth authorization"""
        if not consent:
            return {
                "action": "redirect",
                "redirect_uri": redirect_uri,
                "error": "access_denied",
                "error_description": "User denied the request",
                "state": state
            }
        
        # Validate client and user
        app = self.app_service.get_application_by_client_id(client_id)
        if not app or not app.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid client_id"
            )
        
        user = self.user_service.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is not active"
            )
        
        # Generate authorization code
        auth_code = create_auth_code(
            user_id=str(user.id),
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope=scope
        )
        
        return {
            "action": "redirect",
            "redirect_uri": redirect_uri,
            "code": auth_code,
            "state": state
        }
    
    def handle_token_request(self, token_request: TokenRequest) -> TokenResponse:
        """Handle OAuth 2.0 token request"""
        # Validate client credentials
        app = self.app_service.validate_client_credentials(
            token_request.client_id, 
            token_request.client_secret
        )
        if not app:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid client credentials",
                headers={"WWW-Authenticate": "Basic"}
            )
        
        # Handle different grant types
        if token_request.grant_type == "authorization_code":
            return self._handle_authorization_code_grant(token_request, app)
        elif token_request.grant_type == "refresh_token":
            return self._handle_refresh_token_grant(token_request, app)
        elif token_request.grant_type == "client_credentials":
            return self._handle_client_credentials_grant(token_request, app)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported grant_type"
            )
    
    def _handle_authorization_code_grant(self, token_request: TokenRequest, app: Application) -> TokenResponse:
        """Handle authorization code grant"""
        if not token_request.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing authorization code"
            )
        
        # Consume authorization code
        code_data = consume_auth_code(token_request.code)
        if not code_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired authorization code"
            )
        
        # Validate client and redirect URI
        if code_data["client_id"] != token_request.client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client ID mismatch"
            )
        
        if token_request.redirect_uri and code_data["redirect_uri"] != token_request.redirect_uri:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Redirect URI mismatch"
            )
        
        # Get user information
        user = self.user_service.get_user_by_id(code_data["user_id"])
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is not active"
            )
        
        # Generate tokens
        scope = code_data.get("scope", "openid profile email")
        access_token = create_access_token(str(user.id), scope)
        
        # Create ID token if openid scope is requested
        id_token = None
        if "openid" in scope:
            id_token = create_id_token(user.to_dict())
        
        # Generate refresh token if offline_access scope is requested
        refresh_token = None
        if "offline_access" in scope:
            refresh_token = create_access_token(str(user.id), "refresh_token")
        
        return TokenResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=app.get_access_token_lifetime(),
            refresh_token=refresh_token,
            id_token=id_token,
            scope=scope
        )
    
    def _handle_refresh_token_grant(self, token_request: TokenRequest, app: Application) -> TokenResponse:
        """Handle refresh token grant"""
        if not token_request.refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing refresh token"
            )
        
        try:
            # Decode refresh token
            payload = decode_jwt(token_request.refresh_token)
            if payload.get("scope") != "refresh_token":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid refresh token"
                )
            
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid refresh token"
                )
            
            # Get user information
            user = self.user_service.get_user_by_id(user_id)
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is not active"
                )
            
            # Generate new access token
            scope = token_request.scope or "openid profile email"
            access_token = create_access_token(user_id, scope)
            
            # Create new ID token if openid scope is requested
            id_token = None
            if "openid" in scope:
                id_token = create_id_token(user.to_dict())
            
            return TokenResponse(
                access_token=access_token,
                token_type="Bearer",
                expires_in=app.get_access_token_lifetime(),
                id_token=id_token,
                scope=scope
            )
        
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid refresh token"
            )
    
    def _handle_client_credentials_grant(self, token_request: TokenRequest, app: Application) -> TokenResponse:
        """Handle client credentials grant"""
        # Client credentials grant doesn't involve a user
        scope = token_request.scope or "client"
        access_token = create_access_token(app.client_id, scope)
        
        return TokenResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=app.get_access_token_lifetime(),
            scope=scope
        )
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from access token"""
        try:
            payload = decode_jwt(access_token)
            if payload.get("token_type") != "access_token":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            # Get user information
            user = self.user_service.get_user_by_id(user_id)
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is not active"
                )
            
            # Return user info based on requested scope
            scope = payload.get("scope", "")
            user_info = {"sub": str(user.id)}
            
            if "profile" in scope:
                user_info.update({
                    "name": user.full_name,
                    "username": user.username,
                    "picture": user.profile_picture
                })
            
            if "email" in scope:
                user_info.update({
                    "email": user.email,
                    "email_verified": user.is_verified
                })
            
            if "phone" in scope and user.phone_number:
                user_info["phone_number"] = user.phone_number
            
            return user_info
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token"
            )
    
    def get_openid_configuration(self, base_url: str) -> Dict[str, Any]:
        """Get OpenID Connect discovery configuration"""
        return {
            "issuer": base_url,
            "authorization_endpoint": f"{base_url}/authorize",
            "token_endpoint": f"{base_url}/token",
            "userinfo_endpoint": f"{base_url}/userinfo",
            "jwks_uri": f"{base_url}/.well-known/jwks.json",
            "scopes_supported": ["openid", "profile", "email", "phone", "offline_access"],
            "response_types_supported": ["code", "token", "id_token", "code token", "code id_token", "token id_token", "code token id_token"],
            "grant_types_supported": ["authorization_code", "client_credentials", "refresh_token"],
            "subject_types_supported": ["public"],
            "id_token_signing_alg_values_supported": ["RS256"],
            "token_endpoint_auth_methods_supported": ["client_secret_basic", "client_secret_post", "none"],
            "claims_supported": ["sub", "name", "username", "email", "email_verified", "phone_number", "picture"]
        }