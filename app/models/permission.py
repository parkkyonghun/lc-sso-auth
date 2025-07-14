from sqlalchemy import Column, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..core.database import Base

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    permission_name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True)  # Group permissions by category

    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")