"""Build ownership-validated FarmerContext Pydantic objects for AI services."""

import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.services.farmer_data_service import FarmerDataService
from backend.app.services.weather_intelligence import WeatherIntelligenceService, WeatherContext
from backend.app.schemas.context import (
    FarmerContext,
    FarmerProfileInfo,
    FarmInfo,
    GPSCoordinates,
    SoilInfo,
    IrrigationInfo,
    CropCycleInfo,
    HistoricalCropInfo,
    PestHistoryInfo,
    JournalEntryInfo,
    MarketPreferencesInfo,
    SchemeParticipationInfo,
    FarmSummaryInfo,
    SeasonContextInfo,
)

logger = logging.getLogger(__name__)


def _build_legacy_context(full_context: dict) -> dict:
    """Project rich service data into the legacy flat context shape."""
    profile = full_context["profile"]
    farms = full_context["farms"]
    active_crops = full_context["active_crops"]
    primary_farm = farms[0] if farms else {}

    return {
        "state": primary_farm.get("state") or profile.get("state"),
        "district": primary_farm.get("district") or profile.get("district"),
        "village": primary_farm.get("village") or profile.get("village"),
        "soil_type": primary_farm.get("soil_type") or profile.get("soil_type"),
        "irrigation_source": (
            primary_farm.get("irrigation_source")
            or profile.get("irrigation_source")
        ),
        "preferred_language": profile.get("preferred_language", "ENGLISH"),
        "farm_size_acres": (
            full_context["farm_summary"].get("total_registered_area")
            or profile.get("farm_size_acres")
            or 0.0
        ),
        "active_crops": (
            [
                crop["crop_name"]
                for crop in active_crops
                if crop.get("crop_name")
            ]
            or profile.get("crops_grown", [])
        ),
        "annual_income": profile.get("annual_income") or 0.0,
    }


def build_farmer_context(user_id: int, db: Session) -> dict:
    """Build the legacy flat shape through the centralized data service."""
    full_context = FarmerDataService(db, user_id).get_full_context()
    return _build_legacy_context(full_context)


class ContextBuilder:
    """Build rich and strongly-typed farmer context."""

    def __init__(self, db: Session):
        self.db = db

    def build(self, user: User) -> FarmerContext:
        """
        Build the FarmerContext Pydantic object.
        Retrieves database snapshots and enriches with current weather.
        """
        full_context = FarmerDataService(self.db, user.id).get_full_context()
        profile_data = full_context["profile"]
        farms_data = full_context["farms"]
        active_crops_data = full_context["active_crops"]
        crop_history_data = full_context["crop_history"]
        pest_history_data = full_context["pest_history"]
        recent_journal_data = full_context["recent_journal_entries"]
        summary_data = full_context["farm_summary"]
        season_data = full_context["season_context"]

        # 1. Profile
        profile = FarmerProfileInfo(
            name=profile_data.get("name"),
            state=profile_data.get("state"),
            district=profile_data.get("district"),
            village=profile_data.get("village"),
            category=profile_data.get("category"),
            annual_income=profile_data.get("annual_income"),
            gender=profile_data.get("gender"),
            age=profile_data.get("age"),
            preferred_language=profile_data.get("preferred_language", "ENGLISH"),
        )

        # 2. Farms and Soil/Irrigation splits
        farms: List[FarmInfo] = []
        soil_profiles: List[SoilInfo] = []
        irrigation_details: List[IrrigationInfo] = []
        
        weather_data: Optional[WeatherContext] = None

        for f in farms_data:
            lat = f.get("latitude")
            lon = f.get("longitude")
            gps = None
            if lat is not None and lon is not None:
                gps = GPSCoordinates(latitude=lat, longitude=lon)
                # Fetch weather using the first farm that has GPS coordinates
                if not weather_data:
                    weather_data = WeatherIntelligenceService().get_weather_intelligence(lat, lon)

            # Farm Info
            farms.append(
                FarmInfo(
                    farm_id=f["farm_id"],
                    farm_name=f["farm_name"],
                    state=f.get("state") or "",
                    district=f.get("district") or "",
                    village=f.get("village"),
                    gps_coordinates=gps,
                    total_area_acres=f.get("total_area"),
                    soil_type=f.get("soil_type") or "Loamy",
                    irrigation_source=f.get("irrigation_source") or "RAINFED",
                )
            )

            # Soil Profile
            soil_profiles.append(
                SoilInfo(
                    farm_id=f["farm_id"],
                    farm_name=f["farm_name"],
                    soil_type=f.get("soil_type") or "Loamy",
                    ph=f.get("ph"),
                    nitrogen_ppm=f.get("nitrogen"),
                    phosphorus_ppm=f.get("phosphorus"),
                    potassium_ppm=f.get("potassium"),
                    organic_carbon_pct=f.get("organic_carbon"),
                )
            )

            # Irrigation Details
            # Map water availability rating deterministically based on source
            source = (f.get("irrigation_source") or "RAINFED").upper()
            if source in ("DRIP", "SPRINKLER"):
                avail = "irrigated"
            elif source == "BOREWELL":
                avail = "high"
            elif source == "CANAL":
                avail = "moderate"
            else:
                avail = "low"

            irrigation_details.append(
                IrrigationInfo(
                    farm_id=f["farm_id"],
                    farm_name=f["farm_name"],
                    irrigation_source=f.get("irrigation_source") or "RAINFED",
                    water_availability=avail,
                )
            )

        # 3. Active Crop Cycles
        active_crops = [
            CropCycleInfo(
                crop_cycle_id=c["crop_cycle_id"],
                crop_name=c["crop_name"],
                crop_variety=c.get("crop_variety"),
                season=c["season"],
                year=c.get("year"),
                sowing_date=c.get("sowing_date"),
                expected_harvest_date=c.get("expected_harvest_date"),
                current_stage=c["current_stage"],
                area_under_crop=c.get("area_under_crop"),
                status=c["status"],
                farm_name=c["farm_name"],
                farm_id=c["farm_id"],
                last_updated_at=c.get("last_updated_at"),
            )
            for c in active_crops_data
        ]

        # 4. Crop History
        crop_history = [
            HistoricalCropInfo(
                crop_name=h["crop_name"],
                crop_variety=h.get("crop_variety"),
                season=h["season"],
                year=h.get("year"),
                status=h["status"],
                farm_name=h["farm_name"],
            )
            for h in crop_history_data
        ]

        # 5. Pest/Disease History
        pest_history = [
            PestHistoryInfo(
                disease_name=p["disease_name"],
                confidence=p.get("confidence"),
                source=p.get("source") or "YOLO",
                created_at=p.get("created_at"),
                crop_name=p.get("crop_name"),
                farm_name=p.get("farm_name"),
            )
            for p in pest_history_data
        ]

        # 6. Journal Entries
        crop_journal_entries = [
            JournalEntryInfo(
                entry_type=j["entry_type"],
                title=j["title"],
                description=j.get("description"),
                created_at=j.get("created_at"),
                crop_name=j.get("crop_name"),
                farm_name=j.get("farm_name"),
            )
            for j in recent_journal_data
        ]

        # 7. Market Preferences
        mp_data = profile_data.get("market_preferences") or {}
        market_preferences = MarketPreferencesInfo(
            preferred_crops=mp_data.get("preferred_crops", []),
            preferred_mandi=mp_data.get("preferred_mandi"),
        )

        # 8. Scheme Participation
        sp_data = profile_data.get("scheme_participation") or []
        scheme_participation = [
            SchemeParticipationInfo(
                scheme_name=s.get("scheme_name", ""),
                status=s.get("status", "Active"),
                enrolled_date=s.get("enrolled_date"),
                benefits_received=s.get("benefits_received"),
            )
            for s in sp_data
        ]

        # 9. Summary and Season context
        farm_summary = FarmSummaryInfo(
            total_farms=summary_data.get("total_farms", 0),
            total_registered_area=float(summary_data.get("total_registered_area", 0.0)),
            active_crop_count=summary_data.get("active_crop_count", 0),
            total_crop_cycles=summary_data.get("total_crop_cycles", 0),
            completed_crop_cycles=summary_data.get("completed_crop_cycles", 0),
            recent_pest_count=summary_data.get("recent_pest_count", 0),
            recent_journal_count=summary_data.get("recent_journal_count", 0),
        )

        season_context = SeasonContextInfo(
            current_season=season_data.get("current_season", "Kharif"),
            season_active_crops=season_data.get("season_active_crops", 0),
        )

        return FarmerContext(
            user_id=user.id,
            profile=profile,
            farms=farms,
            active_crops=active_crops,
            crop_history=crop_history,
            soil_profiles=soil_profiles,
            weather_data=weather_data,
            irrigation_details=irrigation_details,
            pest_history=pest_history,
            crop_journal_entries=crop_journal_entries,
            market_preferences=market_preferences,
            scheme_participation=scheme_participation,
            farm_summary=farm_summary,
            season_context=season_context,
        )


def build_crop_context(api_key: str, resource_id: str) -> dict:
    """
    Fetch additional crop/market context from data.gov.in.
    """
    import requests
    if not api_key or not resource_id:
        logger.warning("DATA_GOV_API_KEY or DATA_GOV_RESOURCE_ID not set. Skipping API call.")
        return {}
    
    url = f"https://api.data.gov.in/resource/{resource_id}?api-key={api_key}&format=json&limit=10"
    try:
        response = requests.get(url, timeout=10.0)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch data.gov.in crop context: {e}")
        return {}

