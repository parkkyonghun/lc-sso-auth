from typing import Optional
from pydantic import BaseModel

class BaseOrganizationResponse(BaseModel):
    """
    Base response schema for organization entities like Branch, Department, Position
    Provides common fields and functionality
    """
    id: str
    
    @staticmethod
    def get_entity_name(obj, entity_type):
        """
        Returns the appropriate name field based on entity type
        """
        if entity_type == 'branch':
            return obj.branch_name if hasattr(obj, 'branch_name') else None
        elif entity_type == 'department':
            return obj.department_name if hasattr(obj, 'department_name') else None
        elif entity_type == 'position':
            return obj.title if hasattr(obj, 'title') else None
        return None
    
    class Config:
        from_attributes = True