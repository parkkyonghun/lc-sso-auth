from sqlalchemy import Column, String, text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from ..core.database import Base
from datetime import datetime

class Application(Base):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String, nullable=False)
    client_id = Column(String, unique=True, nullable=False)
    client_secret_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)