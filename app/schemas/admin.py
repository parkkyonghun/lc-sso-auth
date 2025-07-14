from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import datetime
from ..models.base_organization import BaseOrganizationEntity

class SystemStatsResponse(BaseModel):
    """System-wide statistics response"""
    total_users: int
    active_users: int
    verified_users: int
    recent_registrations: int  # Last 30 days
    total_applications: int
    active_applications: int
    recent_applications: int  # Last 30 days
    locked_users: int
    unverified_users: int

class UserStatsResponse(BaseModel):
    """Detailed user statistics response"""
    registration_trends: List[Dict[str, Any]]  # Monthly registration data
    top_active_users: List[Dict[str, Any]]  # Most active users

class AdminUserCreate(BaseModel):
    """Schema for admin user creation"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    password: str
    is_active: bool = True
    is_verified: bool = False
    is_superuser: bool = False

class AdminUserUpdate(BaseModel):
    """Schema for admin user updates"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_superuser: Optional[bool] = None
    bio: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    manager_name: Optional[str] = None
    
    # Organization fields
    branch_id: Optional[str] = None
    department_id: Optional[str] = None
    position_id: Optional[str] = None

class AdminApplicationUpdate(BaseModel):
    """Schema for admin application updates"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    redirect_uris: Optional[List[str]] = None
    allowed_scopes: Optional[List[str]] = None
    grant_types: Optional[List[str]] = None
    response_types: Optional[List[str]] = None
    is_confidential: Optional[bool] = None
    require_consent: Optional[bool] = None
    website_url: Optional[str] = None
    privacy_policy_url: Optional[str] = None
    terms_of_service_url: Optional[str] = None
    logo_url: Optional[str] = None
    token_endpoint_auth_method: Optional[str] = None
    access_token_lifetime: Optional[int] = None
    refresh_token_lifetime: Optional[int] = None

class UserSearchResponse(BaseModel):
    """Response for user search"""
    users: List[Dict[str, Any]]
    total: int
    page: int
    limit: int

class ApplicationSearchResponse(BaseModel):
    """Response for application search"""
    applications: List[Dict[str, Any]]
    total: int
    page: int
    limit: int

class ActivityResponse(BaseModel):
    """Response for recent activities"""
    activities: List[Dict[str, Any]]

class AdminDashboardResponse(BaseModel):
    """Complete admin dashboard data"""
    system_stats: SystemStatsResponse
    user_stats: UserStatsResponse
    recent_activities: List[Dict[str, Any]]

class UserDetailResponse(BaseModel):
    """Detailed user information for admin"""
    id: str
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    is_superuser: bool
    failed_login_attempts: int
    lockout_until: Optional[datetime]
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    # Profile fields
    bio: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    manager_name: Optional[str] = None
    
    # Organization fields
    branch_id: Optional[str] = None
    department_id: Optional[str] = None
    position_id: Optional[str] = None
    
    # Organization details
    branch_name: Optional[str] = None
    department_name: Optional[str] = None
    position_title: Optional[str] = None
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        """Custom from_orm to handle UUID to string conversion"""
        return cls(
            id=str(obj.id),
            username=obj.username,
            email=obj.email,
            full_name=obj.full_name,
            is_active=obj.is_active,
            is_verified=obj.is_verified,
            is_superuser=obj.is_superuser,
            failed_login_attempts=obj.failed_login_attempts,
            lockout_until=obj.lockout_until,
            last_login=obj.last_login,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            # Profile fields
            bio=obj.bio,
            timezone=obj.timezone,
            language=obj.language,
            manager_name=obj.manager_name,
            # Organization fields
            branch_id=str(obj.branch_id) if obj.branch_id else None,
            department_id=str(obj.department_id) if obj.department_id else None,
            position_id=str(obj.position_id) if obj.position_id else None,
            # Organization details
            branch_name=BaseOrganizationEntity.get_display_name(obj.branch) if obj.branch else None,
            department_name=BaseOrganizationEntity.get_display_name(obj.department) if obj.department else None,
            position_title=BaseOrganizationEntity.get_display_name(obj.position) if obj.position else None
        )

class ApplicationDetailResponse(BaseModel):
    """Detailed application information for admin"""
    id: str
    name: str
    description: Optional[str]
    client_id: str
    is_active: bool
    redirect_uris: List[str]
    allowed_scopes: List[str]
    grant_types: List[str]
    response_types: List[str]
    is_confidential: bool
    require_consent: bool
    website_url: Optional[str]
    privacy_policy_url: Optional[str]
    terms_of_service_url: Optional[str]
    logo_url: Optional[str]
    token_endpoint_auth_method: str
    access_token_lifetime: int
    refresh_token_lifetime: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        """Custom from_orm to handle UUID to string conversion and JSON fields"""
        return cls(
            id=str(obj.id),
            name=obj.name,
            description=obj.description,
            client_id=obj.client_id,
            is_active=obj.is_active,
            redirect_uris=obj.get_redirect_uris(),
            allowed_scopes=obj.get_allowed_scopes(),
            grant_types=obj.get_grant_types(),
            response_types=obj.get_response_types(),
            is_confidential=obj.is_confidential,
            require_consent=obj.require_consent,
            website_url=obj.website_url,
            privacy_policy_url=obj.privacy_policy_url,
            terms_of_service_url=obj.terms_of_service_url,
            logo_url=obj.logo_url,
            token_endpoint_auth_method=obj.token_endpoint_auth_method,
            access_token_lifetime=obj.access_token_lifetime,
            refresh_token_lifetime=obj.refresh_token_lifetime,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            created_by=str(obj.created_by) if obj.created_by else None
        )

class BulkUserAction(BaseModel):
    """Schema for bulk user actions"""
    user_ids: List[str]
    action: str  # 'activate', 'deactivate', 'verify', 'delete', 'unlock'

class BulkApplicationAction(BaseModel):
    """Schema for bulk application actions"""
    application_ids: List[str]
    action: str  # 'activate', 'deactivate', 'delete'

class AdminActionResponse(BaseModel):
    """Response for admin actions"""
    success: bool
    message: str
    affected_count: Optional[int] = None
    errors: Optional[List[str]] = None

# Role and Permission Schemas
class RoleResponse(BaseModel):
    """Role response schema"""
    id: str
    role_name: str
    description: Optional[str] = None
    permissions: List[str] = []
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        """Custom from_orm to handle UUID to string conversion"""
        return cls(
            id=str(obj.id),
            role_name=obj.role_name,
            description=obj.description,
            permissions=[perm.permission_name for perm in obj.permissions] if obj.permissions else []
        )

class PermissionResponse(BaseModel):
    """Permission response schema"""
    id: str
    permission_name: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        """Custom from_orm to handle UUID to string conversion"""
        return cls(
            id=str(obj.id),
            permission_name=obj.permission_name,
            description=obj.description
        )

class RoleCreateRequest(BaseModel):
    """Role creation request schema"""
    role_name: str
    description: Optional[str] = None
    permissions: List[str] = []

class RoleUpdateRequest(BaseModel):
    """Role update request schema"""
    role_name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None

class PermissionCreateRequest(BaseModel):
    """Permission creation request schema"""
    permission_name: str
    description: Optional[str] = None

class PermissionUpdateRequest(BaseModel):
    """Permission update request schema"""
    permission_name: Optional[str] = None
    description: Optional[str] = None