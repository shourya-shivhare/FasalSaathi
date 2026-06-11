from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.app.models.enums import SoilType, IrrigationSource


class FarmCreate(BaseModel):
    farm_name: str
    state: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None
    total_area: Optional[float] = None
    soil_type: SoilType = SoilType.LOAMY
    irrigation_source: IrrigationSource = IrrigationSource.RAINFED


class FarmUpdate(BaseModel):
    farm_name: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None
    total_area: Optional[float] = None
    soil_type: Optional[SoilType] = None
    irrigation_source: Optional[IrrigationSource] = None


class FarmOut(FarmCreate):
    id: int
    user_id: int
    created_at: datetime
    active_crop_count: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)
