import uuid
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.app.db.database import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    refresh_token_hash = Column(String(256), unique=True, index=True, nullable=False)
    token_family_id = Column(String(36), nullable=False, index=True)
    
    device_info = Column(String(256), nullable=True)
    device_name = Column(String(128), nullable=True)
    is_trusted_device = Column(Boolean, default=False, nullable=False)
    
    user_agent = Column(String(512), nullable=True)
    ip_address = Column(String(45), nullable=True) # supports IPv4 and IPv6
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_used_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="sessions")
