from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Enum, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.app.db.database import Base
from backend.app.models.enums import Gender, PreferredLanguage, SoilType, IrrigationSource

class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    full_name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(Enum(Gender), nullable=True)
    state = Column(String, nullable=True)
    district = Column(String, nullable=True)
    village = Column(String, nullable=True)
    farm_size_acres = Column(Float, nullable=True)
    annual_income = Column(Float, nullable=True)
    category = Column(String, nullable=True)
    preferred_language = Column(Enum(PreferredLanguage, name='preferredlanguage'), default=PreferredLanguage.ENGLISH, nullable=False)
    soil_type = Column(Enum(SoilType, name='soiltype_v2'), nullable=True)
    irrigation_source = Column(Enum(IrrigationSource, name='irrigationsource'), nullable=True)
    
    # crops_grown is migration-compatibility cache only.
    # Long-term crop data lives in Farm and CropCycle domain models.
    crops_grown = Column(JSON, nullable=True)
    
    # Market preferences and government schemes
    market_preferences = Column(JSON, nullable=True)
    scheme_participation = Column(JSON, nullable=True)

    profile_completed = Column(Boolean, default=False, nullable=False)
    profile_version = Column(Integer, default=1, nullable=False)
    profile_updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="farmer_profile")
