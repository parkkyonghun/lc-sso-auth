from typing import Optional, List
from pydantic import BaseModel
from .base_organization import BaseOrganizationResponse

class BranchResponse(BaseOrganizationResponse):
    """
    Branch response schema
    """
    branch_name: str
    branch_code: str
    address: Optional[str] = None
    province: Optional[str] = None
    
    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=str(obj.id),
            branch_name=obj.branch_name,
            branch_code=obj.branch_code,
            address=obj.address,
            province=obj.province
        )

class DepartmentResponse(BaseOrganizationResponse):
    """
    Department response schema
    """
    department_name: str
    description: Optional[str] = None
    
    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=str(obj.id),
            department_name=obj.department_name,
            description=obj.description
        )

class PositionResponse(BaseOrganizationResponse):
    """
    Position response schema
    """
    title: str
    department_id: str
    department_name: Optional[str] = None
    
    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=str(obj.id),
            title=obj.title,
            department_id=str(obj.department_id),
            department_name=obj.department.department_name if obj.department else None
        )