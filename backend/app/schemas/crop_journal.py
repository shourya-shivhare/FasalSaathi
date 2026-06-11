from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.app.models.enums import JournalEntryType


class JournalEntryCreate(BaseModel):
    crop_cycle_id: int
    entry_type: JournalEntryType
    title: str
    description: Optional[str] = None


class JournalEntryOut(JournalEntryCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
