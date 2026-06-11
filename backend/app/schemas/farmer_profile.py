from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from backend.app.models.enums import Gender, PreferredLanguage, SoilType, IrrigationSource

class FarmerProfileBase(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[Gender] = None
    state: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None
    farm_size_acres: Optional[float] = None
    annual_income: Optional[float] = None
    category: Optional[str] = None
    preferred_language: PreferredLanguage = PreferredLanguage.ENGLISH
    soil_type: Optional[SoilType] = None
    irrigation_source: Optional[IrrigationSource] = None
    crops_grown: Optional[List[str]] = None

class FarmerProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[Gender] = None
    state: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None
    farm_size_acres: Optional[float] = None
    annual_income: Optional[float] = None
    category: Optional[str] = None
    preferred_language: Optional[PreferredLanguage] = None
    soil_type: Optional[SoilType] = None
    irrigation_source: Optional[IrrigationSource] = None
    crops_grown: Optional[List[str]] = None

class FarmerProfileResponse(FarmerProfileBase):
    id: int
    user_id: int
    profile_completed: bool
    profile_version: int
    profile_updated_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
