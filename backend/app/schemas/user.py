from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, model_validator
from backend.app.models.enums import AccountStatus, UserRole, Gender, PreferredLanguage, SoilType, IrrigationSource
from backend.app.schemas.farmer_profile import FarmerProfileResponse

class UserBase(BaseModel):
    username: str
    phone_number: str
    status: AccountStatus = AccountStatus.ACTIVE
    role: UserRole = UserRole.FARMER

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    phone_number: Optional[str] = None
    status: Optional[AccountStatus] = None
    role: Optional[UserRole] = None

    # Farmer profile fields
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

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    farmer_profile: Optional[FarmerProfileResponse] = None

    # Computed from farmer_profile for frontend backward compatibility
    name: Optional[str] = None
    phone: Optional[str] = None
    is_onboarded: Optional[bool] = None

    class Config:
        from_attributes = True

    @model_validator(mode="after")
    def populate_legacy_fields(self):
        """Derive name/phone/is_onboarded from farmer_profile for frontend compat."""
        if self.farmer_profile:
            if self.name is None:
                self.name = self.farmer_profile.full_name or ""
            if self.is_onboarded is None:
                self.is_onboarded = self.farmer_profile.profile_completed
        if self.phone is None:
            self.phone = self.phone_number or ""
        if self.is_onboarded is None:
            self.is_onboarded = False
        return self

