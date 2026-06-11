from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.app.db.database import Base
from backend.app.models.enums import AccountStatus, UserRole

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    name = Column(String, default="", nullable=False)
    is_active = Column(Boolean, default=True)

    # Identity Platform columns
    phone_number = Column(String, unique=True, index=True, nullable=True)
    is_phone_verified = Column(Boolean, default=False, nullable=False)
    phone_verified_at = Column(DateTime(timezone=True), nullable=True)
    account_status = Column(Enum(AccountStatus, name='accountstatus'), default=AccountStatus.ACTIVE, nullable=False)
    role = Column(Enum(UserRole, name='userrole'), default=UserRole.FARMER, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    farmer_profile = relationship("FarmerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    security_events = relationship("SecurityEvent", back_populates="user", cascade="all, delete-orphan")
    
    # Existing domain model relationships
    farms = relationship("Farm", back_populates="user", cascade="all, delete-orphan")
    pest_histories = relationship("PestDetectionHistory", back_populates="user")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")