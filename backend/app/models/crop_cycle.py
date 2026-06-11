from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Date, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.db.database import Base
from backend.app.models.enums import CropStage, CropCycleStatus, CropSeason

class CropCycle(Base):
    __tablename__ = "crop_cycles"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False, index=True)
    crop_name = Column(String, nullable=False)
    crop_variety = Column(String, nullable=True)
    season = Column(Enum(CropSeason), nullable=False)
    year = Column(Integer, nullable=True)
    sowing_date = Column(Date, nullable=True)
    expected_harvest_date = Column(Date, nullable=True)
    current_stage = Column(Enum(CropStage), default=CropStage.SEEDING, nullable=False)
    area_under_crop = Column(Float, nullable=True)
    status = Column(Enum(CropCycleStatus), default=CropCycleStatus.ACTIVE, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    farm = relationship("Farm", back_populates="crop_cycles")
    journal_entries = relationship("CropJournalEntry", back_populates="crop_cycle", cascade="all, delete-orphan")
    pest_detections = relationship("PestDetectionHistory", back_populates="crop_cycle")
