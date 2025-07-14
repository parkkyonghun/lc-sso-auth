from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Optional, List
from datetime import datetime
import uuid

class ApplicationBase(BaseModel):
    name: str = Field(..., description="Application name", min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000, description="Application description")
    redirect_uris: List[str] = Field(..., min_items=1, description="Allowed redirect URIs")
    website_url: Optional[HttpUrl] = Field(None, description="Application website URL")
    privacy_policy_url: Optional[HttpUrl] = Field(None, description="Privacy policy URL")
    terms_of_service_url: Optional[HttpUrl] = Field(None, description="Terms of service URL")
    logo_url: Optional[HttpUrl] = Field(None, description="Application logo URL")
    
    @validator('redirect_uris')
    def validate_redirect_uris(cls, v):
        for uri in v:
            if not uri.startswith(('http://', 'https://')):
                raise ValueError(f'Invalid redirect URI: {uri}. Must start with http:// or https://')
        return v

class ApplicationCreate(ApplicationBase):
    allowed_scopes: List[str] = Field(default=["openid", "profile", "email"], description="Allowed OAuth scopes")
    grant_types: List[str] = Field(default=["authorization_code"], description="Supported grant types")
    response_types: List[str] = Field(default=["code"], description="Supported response types")
    is_confidential: bool = Field(default=True, description="Whether this is a confidential client")
    require_consent: bool = Field(default=True, description="Whether to require user consent")
    token_endpoint_auth_method: str = Field(default="client_secret_basic", description="Token endpoint authentication method")
    access_token_lifetime: int = Field(default=3600, ge=300, le=86400, description="Access token lifetime in seconds")
    refresh_token_lifetime: int = Field(default=86400, ge=3600, le=2592000, description="Refresh token lifetime in seconds")
    
    @validator('allowed_scopes')
    def validate_scopes(cls, v):
        valid_scopes = ["openid", "profile", "email", "phone", "address", "offline_access"]
        for scope in v:
            if scope not in valid_scopes:
                raise ValueError(f'Invalid scope: {scope}. Valid scopes are: {", ".join(valid_scopes)}')
        return v
    
    @validator('grant_types')
    def validate_grant_types(cls, v):
        valid_grant_types = ["authorization_code", "client_credentials", "refresh_token"]
        for grant_type in v:
            if grant_type not in valid_grant_types:
                raise ValueError(f'Invalid grant type: {grant_type}. Valid types are: {", ".join(valid_grant_types)}')
        return v
    
    @validator('response_types')
    def validate_response_types(cls, v):
        valid_response_types = ["code", "token", "id_token", "code token", "code id_token", "token id_token", "code token id_token"]
        for response_type in v:
            if response_type not in valid_response_types:
                raise ValueError(f'Invalid response type: {response_type}. Valid types are: {", ".join(valid_response_types)}')
        return v
    
    @validator('token_endpoint_auth_method')
    def validate_auth_method(cls, v):
        valid_methods = ["client_secret_basic", "client_secret_post", "none"]
        if v not in valid_methods:
            raise ValueError(f'Invalid auth method: {v}. Valid methods are: {", ".join(valid_methods)}')
        return v

class ApplicationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    redirect_uris: Optional[List[str]] = Field(None, min_items=1)
    allowed_scopes: Optional[List[str]] = Field(None)
    website_url: Optional[HttpUrl] = Field(None)
    privacy_policy_url: Optional[HttpUrl] = Field(None)
    terms_of_service_url: Optional[HttpUrl] = Field(None)
    logo_url: Optional[HttpUrl] = Field(None)
    require_consent: Optional[bool] = Field(None)
    access_token_lifetime: Optional[int] = Field(default=None, ge=300, le=86400)
    refresh_token_lifetime: Optional[int] = Field(default=None, ge=3600, le=2592000)
    is_active: Optional[bool] = Field(None)

class ApplicationResponse(ApplicationBase):
    id: uuid.UUID
    client_id: str
    allowed_scopes: List[str]
    grant_types: List[str]
    response_types: List[str]
    is_active: bool
    is_confidential: bool
    require_consent: bool
    token_endpoint_auth_method: str
    access_token_lifetime: int
    refresh_token_lifetime: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[uuid.UUID] = None
    
    class Config:
        from_attributes = True

class ApplicationWithSecret(ApplicationResponse):
    client_secret: str

class ApplicationList(BaseModel):
    applications: List[ApplicationResponse]
    total: int
    page: int
    size: int
    pages: int

# OAuth 2.0 specific schemas
class AuthorizeRequest(BaseModel):
    response_type: str = Field(..., description="OAuth response type")
    client_id: str = Field(..., description="Client ID")
    redirect_uri: str = Field(..., description="Redirect URI")
    scope: Optional[str] = Field("openid profile email", description="Requested scopes")
    state: Optional[str] = Field(None, description="State parameter")
    nonce: Optional[str] = Field(None, description="Nonce for OIDC")
    code_challenge: Optional[str] = Field(None, description="PKCE code challenge")
    code_challenge_method: Optional[str] = Field(None, description="PKCE code challenge method")

class TokenRequest(BaseModel):
    grant_type: str = Field(..., description="Grant type")
    code: Optional[str] = Field(None, description="Authorization code")
    redirect_uri: Optional[str] = Field(None, description="Redirect URI")
    client_id: str = Field(..., description="Client ID")
    client_secret: Optional[str] = Field(None, description="Client secret")
    code_verifier: Optional[str] = Field(None, description="PKCE code verifier")
    refresh_token: Optional[str] = Field(None, description="Refresh token")
    scope: Optional[str] = Field(None, description="Requested scope")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    id_token: Optional[str] = None
    scope: Optional[str] = None

class ConsentRequest(BaseModel):
    client_id: str = Field(..., description="Client ID")
    scope: str = Field(..., description="Requested scopes")
    consent: bool = Field(..., description="User consent decision")