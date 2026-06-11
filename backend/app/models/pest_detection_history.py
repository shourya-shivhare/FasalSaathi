from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.db.database import Base
from backend.app.models.enums import PestDetectionSource

class PestDetectionHistory(Base):
    __tablename__ = "pest_detection_histories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    crop_cycle_id = Column(Integer, ForeignKey("crop_cycles.id"), nullable=True, index=True)
    disease_name = Column(String, nullable=False)
    confidence = Column(Float, nullable=True)
    image_url = Column(String, nullable=True)
    source = Column(Enum(PestDetectionSource), default=PestDetectionSource.YOLO, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="pest_histories")
    crop_cycle = relationship("CropCycle", back_populates="pest_detections")
