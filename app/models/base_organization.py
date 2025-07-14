from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid

from ..core.database import Base

class BaseOrganizationEntity:
    """
    Base class for organization entities like Branch, Department, Position
    Provides common fields and functionality
    """
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    @classmethod
    def get_display_name(cls, obj):
        """
        Returns the display name of the entity based on its type
        This helps standardize access to the primary name field of each entity
        """
        if hasattr(obj, 'branch_name'):
            return obj.branch_name
        elif hasattr(obj, 'department_name'):
            return obj.department_name
        elif hasattr(obj, 'title'):
            return obj.title
        return None