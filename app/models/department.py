from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from ..core.database import Base
from .base_organization import BaseOrganizationEntity

class Department(Base, BaseOrganizationEntity):
    __tablename__ = "departments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    department_name = Column(String, nullable=False)
    description = Column(Text)

    positions = relationship("Position", back_populates="department")