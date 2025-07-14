from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import List
import json

from ..core.database import Base

class Application(Base):
    __tablename__ = "applications"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, server_default=text("gen_random_uuid()"))
    
    # Basic application information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # OAuth 2.0 credentials
    client_id = Column(String(255), unique=True, index=True, nullable=False)
    client_secret = Column(String(255), nullable=False)
    
    # OAuth 2.0 configuration (stored as JSON strings)
    redirect_uris = Column(Text, nullable=False, default='[]')  # JSON string of allowed redirect URIs
    allowed_scopes = Column(Text, nullable=False, default='["openid", "profile", "email"]')  # JSON string of allowed scopes
    grant_types = Column(Text, nullable=False, default='["authorization_code", "refresh_token"]')  # JSON string of supported grant types
    response_types = Column(Text, nullable=False, default='["code"]')  # JSON string of supported response types
    
    # Application settings
    is_active = Column(Boolean, default=True, nullable=False)
    is_confidential = Column(Boolean, default=True, nullable=False)  # Public vs Confidential client
    require_consent = Column(Boolean, default=True, nullable=False)  # Require user consent
    
    # Branding and information
    logo_url = Column(String(500), nullable=True)
    website_url = Column(String(500), nullable=True)
    privacy_policy_url = Column(String(500), nullable=True)
    terms_of_service_url = Column(String(500), nullable=True)
    
    # Security settings
    token_endpoint_auth_method = Column(String(50), default="client_secret_basic", nullable=False)
    access_token_lifetime = Column(Integer, default=3600, nullable=False)  # seconds
    refresh_token_lifetime = Column(Integer, default=2592000, nullable=False)  # 30 days
    authorization_code_lifetime = Column(Integer, default=600, nullable=False)  # 10 minutes
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Foreign key to the user who created the application
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    creator = relationship("User", back_populates="oauth_applications")
    
    def __repr__(self):
        return f"<OAuthApplication(id={self.id}, name={self.name}, client_id={self.client_id})>"
    
    def to_dict(self):
        """Convert application object to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "client_id": self.client_id,
            "redirect_uris": self.get_redirect_uris(),
            "allowed_scopes": self.get_allowed_scopes(),
            "grant_types": self.get_grant_types(),
            "response_types": self.get_response_types(),
            "is_active": self.is_active,
            "is_confidential": self.is_confidential,
            "require_consent": self.require_consent,
            "logo_url": self.logo_url,
            "website_url": self.website_url,
            "privacy_policy_url": self.privacy_policy_url,
            "terms_of_service_url": self.terms_of_service_url,
            "token_endpoint_auth_method": self.token_endpoint_auth_method,
            "access_token_lifetime": self.access_token_lifetime,
            "refresh_token_lifetime": self.refresh_token_lifetime,
            "authorization_code_lifetime": self.authorization_code_lifetime,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": str(self.created_by) if self.created_by else None
        }
    
    def get_redirect_uris(self) -> List[str]:
        """Get redirect URIs as a list"""
        try:
            return json.loads(str(self.redirect_uris)) if self.redirect_uris else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    def get_allowed_scopes(self) -> List[str]:
        """Get allowed scopes as a list"""
        try:
            return json.loads(self.allowed_scopes) if self.allowed_scopes else []
        except (json.JSONDecodeError, TypeError):
            return ["openid", "profile", "email"]
    
    def get_grant_types(self) -> List[str]:
        """Get grant types as a list"""
        try:
            return json.loads(str(self.grant_types)) if self.grant_types else []
        except (json.JSONDecodeError, TypeError):
            return ["authorization_code", "refresh_token"]
    
    def get_response_types(self) -> List[str]:
        """Get response types as a list"""
        try:
            return json.loads(str(self.response_types)) if self.response_types else []
        except (json.JSONDecodeError, TypeError):
            return ["code"]
    
    def is_redirect_uri_allowed(self, redirect_uri: str) -> bool:
        """Check if redirect URI is allowed for this application"""
        return redirect_uri in self.get_redirect_uris()
    
    def is_scope_allowed(self, scope: str) -> bool:
        """Check if scope is allowed for this application"""
        requested_scopes = scope.split() if scope else []
        allowed_scopes = self.get_allowed_scopes()
        return all(s in allowed_scopes for s in requested_scopes)
    
    def supports_grant_type(self, grant_type: str) -> bool:
        """Check if grant type is supported by this application"""
        return grant_type in self.get_grant_types()
    
    def supports_response_type(self, response_type: str) -> bool:
        """Check if response type is supported by this application"""
        return response_type in self.get_response_types()
    
    def get_access_token_lifetime(self) -> int:
        """Get access token lifetime in seconds"""
        return self.access_token_lifetime
    
    def get_refresh_token_lifetime(self) -> int:
        """Get refresh token lifetime in seconds"""
        return self.refresh_token_lifetime
    
    def get_authorization_code_lifetime(self) -> int:
        """Get authorization code lifetime in seconds"""
        return self.authorization_code_lifetime