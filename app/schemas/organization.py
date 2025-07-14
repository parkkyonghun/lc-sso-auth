from typing import Optional
from pydantic import BaseModel, Field
from .base_organization import BaseOrganizationResponse

# Request Schemas
class BranchCreateRequest(BaseModel):
    """
    Branch creation request schema
    """
    name: str = Field(..., min_length=1, max_length=100, description="Branch name")
    code: str = Field(..., min_length=1, max_length=20, description="Unique branch code")
    address: Optional[str] = Field(None, max_length=300, description="Branch address")
    province: Optional[str] = Field(None, max_length=50, description="Province/state")

class BranchUpdateRequest(BaseModel):
    """
    Branch update request schema
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Branch name")
    code: Optional[str] = Field(None, min_length=1, max_length=20, description="Unique branch code")
    address: Optional[str] = Field(None, max_length=300, description="Branch address")
    province: Optional[str] = Field(None, max_length=50, description="Province/state")

class DepartmentCreateRequest(BaseModel):
    """
    Department creation request schema
    """
    name: str = Field(..., min_length=1, max_length=100, description="Department name")
    description: Optional[str] = Field(None, max_length=300, description="Department description")

class DepartmentUpdateRequest(BaseModel):
    """
    Department update request schema
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Department name")
    description: Optional[str] = Field(None, max_length=300, description="Department description")

class PositionCreateRequest(BaseModel):
    """
    Position creation request schema
    """
    title: str = Field(..., min_length=1, max_length=100, description="Position title")
    department_id: str = Field(..., description="Department ID this position belongs to")

class PositionUpdateRequest(BaseModel):
    """
    Position update request schema
    """
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="Position title")
    department_id: Optional[str] = Field(None, description="Department ID this position belongs to")

# Response Schemas
class BranchResponse(BaseOrganizationResponse):
    """
    Branch response schema
    """
    branch_name: str = Field(..., description="Branch name")
    branch_code: str = Field(..., description="Unique branch code")
    address: Optional[str] = Field(None, description="Branch address")
    province: Optional[str] = Field(None, description="Province/state")

class DepartmentResponse(BaseOrganizationResponse):
    """
    Department response schema
    """
    department_name: str = Field(..., description="Department name")
    description: Optional[str] = Field(None, description="Department description")

class PositionResponse(BaseOrganizationResponse):
    """
    Position response schema
    """
    title: str = Field(..., description="Position title")
    department_id: str = Field(..., description="Department ID this position belongs to")
    department_name: Optional[str] = Field(None, description="Department name (populated from relationship)")

# Success Response Schema
class OrganizationDeleteResponse(BaseModel):
    """
    Standard response for organization entity deletion
    """
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Success message")
    