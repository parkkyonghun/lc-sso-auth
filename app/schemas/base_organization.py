from pydantic import BaseModel, model_validator, ConfigDict
from uuid import UUID
from typing import Any, Dict

class BaseOrganizationResponse(BaseModel):
    """
    Base response schema for organization entities like Branch, Department, Position
    Provides common fields and functionality
    """
    model_config = ConfigDict(from_attributes=True)

    id: str

    @model_validator(mode='before')
    @classmethod
    def convert_uuid_to_str(cls, data: Any) -> Any:
        """
        Convert UUID objects to strings before validation.
        This handles the case where SQLAlchemy models have UUID fields
        but the Pydantic schema expects string fields.
        """
        if hasattr(data, '__dict__'):
            # Handle SQLAlchemy model objects
            data_dict = {}
            for key, value in data.__dict__.items():
                if isinstance(value, UUID):
                    data_dict[key] = str(value)
                else:
                    data_dict[key] = value
            return data_dict
        elif isinstance(data, dict):
            # Handle dictionary input
            converted_data = {}
            for key, value in data.items():
                if isinstance(value, UUID):
                    converted_data[key] = str(value)
                else:
                    converted_data[key] = value
            return converted_data
        return data