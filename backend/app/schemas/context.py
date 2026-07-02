from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import date, datetime


class GPSCoordinates(BaseModel):
    latitude: float
    longitude: float


class FarmInfo(BaseModel):
    farm_id: int
    farm_name: str
    state: str
    district: str
    village: Optional[str] = None
    gps_coordinates: Optional[GPSCoordinates] = None
    total_area_acres: Optional[float] = None
    soil_type: str
    irrigation_source: str


from backend.app.services.weather_intelligence import WeatherContext


class SoilInfo(BaseModel):
    farm_id: int
    farm_name: str
    soil_type: str
    ph: Optional[float] = None
    nitrogen_ppm: Optional[float] = None
    phosphorus_ppm: Optional[float] = None
    potassium_ppm: Optional[float] = None
    organic_carbon_pct: Optional[float] = None


class IrrigationInfo(BaseModel):
    farm_id: int
    farm_name: str
    irrigation_source: str
    water_availability: str  # derived: e.g. "irrigated" if drip/sprinkler/borewell, else "moderate"/"low"


class CropCycleInfo(BaseModel):
    crop_cycle_id: int
    crop_name: str
    crop_variety: Optional[str] = None
    season: str
    year: Optional[int] = None
    sowing_date: Optional[str] = None  # ISO format date string
    expected_harvest_date: Optional[str] = None
    current_stage: str
    area_under_crop: Optional[float] = None
    status: str
    farm_name: str
    farm_id: int
    last_updated_at: Optional[str] = None


class HistoricalCropInfo(BaseModel):
    crop_name: str
    crop_variety: Optional[str] = None
    season: str
    year: Optional[int] = None
    status: str
    farm_name: str


class PestHistoryInfo(BaseModel):
    disease_name: str
    confidence: Optional[float] = None
    source: str
    created_at: Optional[str] = None
    crop_name: Optional[str] = None
    farm_name: Optional[str] = None


class JournalEntryInfo(BaseModel):
    entry_type: str
    title: str
    description: Optional[str] = None
    created_at: Optional[str] = None
    crop_name: Optional[str] = None
    farm_name: Optional[str] = None


class MarketPreferencesInfo(BaseModel):
    preferred_crops: List[str] = Field(default_factory=list)
    preferred_mandi: Optional[str] = None


class SchemeParticipationInfo(BaseModel):
    scheme_name: str
    status: str  # e.g., "Applied", "Approved", "Active", "Enrolled"
    enrolled_date: Optional[str] = None
    benefits_received: Optional[str] = None


class FarmerProfileInfo(BaseModel):
    name: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None
    category: Optional[str] = None
    annual_income: Optional[float] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    preferred_language: str = "ENGLISH"


class FarmSummaryInfo(BaseModel):
    total_farms: int = 0
    total_registered_area: float = 0.0
    active_crop_count: int = 0
    total_crop_cycles: int = 0
    completed_crop_cycles: int = 0
    recent_pest_count: int = 0
    recent_journal_count: int = 0


class SeasonContextInfo(BaseModel):
    current_season: str
    season_active_crops: int = 0


class FarmerContext(BaseModel):
    """Unified and strongly-typed farmer agricultural context payload."""
    user_id: int
    profile: FarmerProfileInfo
    farms: List[FarmInfo] = Field(default_factory=list)
    active_crops: List[CropCycleInfo] = Field(default_factory=list)
    crop_history: List[HistoricalCropInfo] = Field(default_factory=list)
    soil_profiles: List[SoilInfo] = Field(default_factory=list)
    weather_data: Optional[WeatherContext] = None
    irrigation_details: List[IrrigationInfo] = Field(default_factory=list)
    pest_history: List[PestHistoryInfo] = Field(default_factory=list)
    crop_journal_entries: List[JournalEntryInfo] = Field(default_factory=list)
    market_preferences: Optional[MarketPreferencesInfo] = None
    scheme_participation: List[SchemeParticipationInfo] = Field(default_factory=list)
    farm_summary: FarmSummaryInfo
    season_context: SeasonContextInfo
