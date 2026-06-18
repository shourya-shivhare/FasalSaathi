from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.app.db.database import Base
from backend.app.models.enums import AccountStatus, UserRole

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    status = Column(Enum(AccountStatus, name='accountstatus'), default=AccountStatus.ACTIVE, nullable=False)
    role = Column(Enum(UserRole, name='userrole'), default=UserRole.FARMER, nullable=False)

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