from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.app.models.enums import PestDetectionSource


class PestHistoryCreate(BaseModel):
    crop_cycle_id: Optional[int] = None
    disease_name: str
    confidence: Optional[float] = None
    image_url: Optional[str] = None
    source: PestDetectionSource = PestDetectionSource.YOLO


class PestHistoryOut(PestHistoryCreate):
    id: int
    user_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
