from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
import uuid

class UserBase(BaseModel):
    username: str = Field(..., max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, max_length=255, description="Full name")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number")
    bio: Optional[str] = Field(None, max_length=500, description="User biography")
    is_superuser: bool = Field(False, description="Superuser status")
 
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128, description="Password")
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=20)
    bio: Optional[str] = Field(None, max_length=500)
    profile_picture: Optional[str] = Field(None, description="Profile picture URL")
    is_superuser: Optional[bool] = Field(None, description="Superuser status")
 
class UserLogin(BaseModel):
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")

class UserResponse(UserBase):
    id: uuid.UUID
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class PasswordChange(BaseModel):
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")
    confirm_new_password: str = Field(..., description="New password confirmation")
    
    @validator('confirm_new_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('New passwords do not match')
        return v
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class PasswordReset(BaseModel):
    email: EmailStr = Field(..., description="Email address")

class PasswordResetConfirm(BaseModel):
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")
    confirm_new_password: str = Field(..., description="New password confirmation")
    
    @validator('confirm_new_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('New passwords do not match')
        return v

class UserList(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    size: int
    pages: int