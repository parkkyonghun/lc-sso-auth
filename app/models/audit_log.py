from sqlalchemy import Column, String, text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from ..core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), nullable=False)
    event_type = Column(String, nullable=False)
    ip_address = Column(String, nullable=True)
    details = Column(JSONB, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)