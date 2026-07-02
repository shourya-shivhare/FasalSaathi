from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.db.database import Base
from backend.app.models.enums import SoilType, IrrigationSource

class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    farm_name = Column(String, nullable=False)
    state = Column(String, nullable=True)
    district = Column(String, nullable=True)
    village = Column(String, nullable=True)
    total_area = Column(Float, nullable=True)
    soil_type = Column(Enum(SoilType), default=SoilType.LOAMY, nullable=False)
    irrigation_source = Column(Enum(IrrigationSource), default=IrrigationSource.RAINFED, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # GPS and Soil Health parameters
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    ph = Column(Float, nullable=True)
    nitrogen = Column(Float, nullable=True)
    phosphorus = Column(Float, nullable=True)
    potassium = Column(Float, nullable=True)
    organic_carbon = Column(Float, nullable=True)

    user = relationship("User", back_populates="farms")
    crop_cycles = relationship("CropCycle", back_populates="farm", cascade="all, delete-orphan")
