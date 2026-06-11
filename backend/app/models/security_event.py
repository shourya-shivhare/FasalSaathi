from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.app.db.database import Base

class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # event_type values from audit:
    # REGISTRATION_CREATED, LOGIN_SUCCESS, LOGIN_FAILED, OTP_SENT, OTP_VERIFIED,
    # OTP_FAILED, TOKEN_REFRESH, LOGOUT, LOGOUT_ALL, TOKEN_REUSE_DETECTED,
    # ACCOUNT_BLOCKED, ACCOUNT_SUSPENDED
    event_type = Column(String(50), nullable=False, index=True)
    
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(512), nullable=True)
    metadata_json = Column(JSON, nullable=True) # Renamed to metadata_json to avoid SQLAlchemy conflict
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="security_events")
