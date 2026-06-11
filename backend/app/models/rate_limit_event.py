from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from backend.app.db.database import Base

class RateLimitEvent(Base):
    __tablename__ = "rate_limit_events"

    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String(128), nullable=False, index=True)
    
    # event_type: OTP_REQUEST, OTP_VERIFY, LOGIN_ATTEMPT, CHAT_REQUEST, IMAGE_UPLOAD, PEST_ANALYSIS
    event_type = Column(String(50), nullable=False, index=True)
    
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
