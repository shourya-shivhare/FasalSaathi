from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict
from backend.app.models.enums import CropStage, CropCycleStatus, CropSeason


class CropCycleCreate(BaseModel):
    farm_id: int
    crop_name: str
    crop_variety: Optional[str] = None
    season: CropSeason
    year: Optional[int] = None
    sowing_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None
    current_stage: CropStage = CropStage.SEEDING
    area_under_crop: Optional[float] = None
    status: CropCycleStatus = CropCycleStatus.ACTIVE
    notes: Optional[str] = None


class CropCycleUpdate(BaseModel):
    crop_name: Optional[str] = None
    crop_variety: Optional[str] = None
    season: Optional[CropSeason] = None
    year: Optional[int] = None
    sowing_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None
    current_stage: Optional[CropStage] = None
    area_under_crop: Optional[float] = None
    status: Optional[CropCycleStatus] = None
    notes: Optional[str] = None


class StageUpdate(BaseModel):
    current_stage: CropStage


class CropCycleOut(CropCycleCreate):
    id: int
    farm_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
