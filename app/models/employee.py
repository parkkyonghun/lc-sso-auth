from sqlalchemy import Column, String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from ..core.database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    employee_code = Column(String, unique=True, nullable=False)
    full_name_khmer = Column(String, nullable=False)
    full_name_latin = Column(String, nullable=False)
    phone_number = Column(String)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False)
    position_id = Column(UUID(as_uuid=True), ForeignKey("positions.id"), nullable=False)
    hire_date = Column(Date)
    status = Column(String)

    user = relationship("User", back_populates="employee")
    branch = relationship("Branch", back_populates="employees")
    position = relationship("Position", back_populates="employees")