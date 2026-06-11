from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.db.database import Base
from backend.app.models.enums import JournalEntryType

class CropJournalEntry(Base):
    __tablename__ = "crop_journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    crop_cycle_id = Column(Integer, ForeignKey("crop_cycles.id"), nullable=False, index=True)
    entry_type = Column(Enum(JournalEntryType), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    crop_cycle = relationship("CropCycle", back_populates="journal_entries")
