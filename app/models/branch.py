from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from ..core.database import Base
from .base_organization import BaseOrganizationEntity

class Branch(Base, BaseOrganizationEntity):
    __tablename__ = "branches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    branch_name = Column(String, nullable=False)
    branch_code = Column(String, unique=True, nullable=False)
    address = Column(Text)
    province = Column(String)

    employees = relationship("Employee", back_populates="branch")