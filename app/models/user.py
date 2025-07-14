from sqlalchemy import Column, String, Boolean, DateTime, text, Integer, Text, ForeignKey
from datetime import datetime, timedelta
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    lockout_until = Column(DateTime(timezone=True), nullable=True)
    
    # Profile fields
    bio = Column(Text, nullable=True)
    timezone = Column(String(50), nullable=True)
    language = Column(String(10), nullable=True)
    manager_name = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=True)
    
    # Organization fields
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="SET NULL"), nullable=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    position_id = Column(UUID(as_uuid=True), ForeignKey("positions.id", ondelete="SET NULL"), nullable=True)

    employee = relationship("Employee", back_populates="user", uselist=False)
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    oauth_applications = relationship("Application", back_populates="creator")
    
    # Organization relationships
    branch = relationship("Branch", foreign_keys=[branch_id])
    department = relationship("Department", foreign_keys=[department_id])
    position = relationship("Position", foreign_keys=[position_id])

    def is_locked(self):
        return self.lockout_until and self.lockout_until > datetime.utcnow()

    def increment_failed_attempts(self):
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.lockout_until = datetime.utcnow() + timedelta(minutes=15)

    def reset_failed_attempts(self):
        self.failed_login_attempts = 0
        self.lockout_until = None

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_superuser": self.is_superuser,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "failed_login_attempts": self.failed_login_attempts,
            "is_locked": self.is_locked()
        }