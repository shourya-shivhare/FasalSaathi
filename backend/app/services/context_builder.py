"""
Context Builder — assembles the full farmer context payload for the AI service.

Consumes FarmerDataService for all data retrieval (ownership-validated).
Maintains backward compatibility with the legacy flat context format.
"""
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.models.farmer_profile import FarmerProfile
from backend.app.models.farm import Farm
from backend.app.models.crop_cycle import CropCycle
from backend.app.models.enums import CropCycleStatus, PreferredLanguage
from backend.app.services.farmer_data_service import FarmerDataService


def _enum_val(v):
    """Safely extract .value from an enum, or str() it."""
    return v.value if hasattr(v, "value") else str(v) if v else None


def build_farmer_context(user_id: int, db: Session) -> dict:
    """
    Legacy flat context builder.
    Fetches the User, FarmerProfile, active Farm details, and current CropCycle.
    Returns a unified context dictionary for Chat, Agents, and Pest Detection.
    Treats crops_grown on FarmerProfile as a migration-compatibility field only.
    Prioritizes Farm and CropCycle data over FarmerProfile.crops_grown compatibility field.
    """
    # Fetch user and profile
    profile = db.query(FarmerProfile).filter(FarmerProfile.user_id == user_id).first()
    
    # Defaults
    context = {
        "state": None,
        "district": None,
        "village": None,
        "soil_type": None,
        "irrigation_source": None,
        "preferred_language": "ENGLISH",
        "farm_size_acres": 0.0,
        "active_crops": [],
        "annual_income": 0.0
    }
    
    if profile:
        context["state"] = profile.state
        context["district"] = profile.district
        context["village"] = profile.village
        context["farm_size_acres"] = profile.farm_size_acres or 0.0
        context["annual_income"] = profile.annual_income or 0.0
        
        if profile.soil_type:
            context["soil_type"] = _enum_val(profile.soil_type)
        if profile.irrigation_source:
            context["irrigation_source"] = _enum_val(profile.irrigation_source)
            
        # Map preferred language to AI service format (HINDI / ENGLISH)
        if profile.preferred_language:
            lang_val = profile.preferred_language
            if isinstance(lang_val, PreferredLanguage):
                context["preferred_language"] = "HINDI" if lang_val == PreferredLanguage.HINDI else "ENGLISH"
            else:
                context["preferred_language"] = "HINDI" if str(lang_val).upper() == "HINDI" else "ENGLISH"

    # Fetch farms
    farms = db.query(Farm).filter(Farm.user_id == user_id).all()
    
    active_crops_from_cycles = []
    
    if farms:
        primary_farm = farms[0]
        if primary_farm.state:
            context["state"] = primary_farm.state
        if primary_farm.district:
            context["district"] = primary_farm.district
        if primary_farm.village:
            context["village"] = primary_farm.village
        if primary_farm.soil_type:
            context["soil_type"] = _enum_val(primary_farm.soil_type)
        if primary_farm.irrigation_source:
            context["irrigation_source"] = _enum_val(primary_farm.irrigation_source)
            
        total_area = sum(f.total_area or 0.0 for f in farms)
        if total_area > 0:
            context["farm_size_acres"] = total_area
            
        farm_ids = [f.id for f in farms]
        active_cycles = db.query(CropCycle).filter(
            CropCycle.farm_id.in_(farm_ids),
            CropCycle.status == CropCycleStatus.ACTIVE
        ).all()
        
        active_crops_from_cycles = list(set(cycle.crop_name for cycle in active_cycles if cycle.crop_name))

    if active_crops_from_cycles:
        context["active_crops"] = active_crops_from_cycles
    elif profile and profile.crops_grown:
        if isinstance(profile.crops_grown, list):
            context["active_crops"] = profile.crops_grown
        elif isinstance(profile.crops_grown, str):
            context["active_crops"] = [c.strip() for c in profile.crops_grown.split(",") if c.strip()]
            
    return context


class ContextBuilder:
    """
    Builds rich farmer context for the AI assistant.

    Consumes FarmerDataService for all ownership-validated data retrieval.
    Heavy context (farms, crop cycles, pest history, journal entries) is
    always included so the AI service can decide what to inject into the
    LLM prompt based on the classified intent.
    """
    def __init__(self, db: Session):
        self.db = db

    def build(self, user: User) -> dict:
        flat = build_farmer_context(user.id, self.db)

        # ── Use FarmerDataService for ownership-validated rich data ────────
        svc = FarmerDataService(self.db, user.id)
        full_ctx = svc.get_full_context()

        # ── Merge profile fields ──────────────────────────────────────────
        profile_dict = full_ctx["profile"]
        # Ensure backward-compatible top-level fields
        profile_dict.setdefault("state", flat.get("state", ""))
        profile_dict.setdefault("district", flat.get("district", ""))
        profile_dict.setdefault("village", flat.get("village", ""))
        profile_dict.setdefault("land_size_acres", flat.get("farm_size_acres", 0))

        # ── Build backward-compatible active_crops for legacy code ────────
        active_crops_nested = full_ctx["active_crops"] if full_ctx["active_crops"] else [
            {"crop_name": c} for c in flat.get("active_crops", [])
        ]

        return {
            **flat,
            "profile": profile_dict,
            "active_crops": active_crops_nested,
            # ── Rich data sections (for data_retrieval / data_analysis) ───
            "farms": full_ctx["farms"],
            "crop_history": full_ctx["crop_history"],
            "pest_history": full_ctx["pest_history"],
            "recent_journal_entries": full_ctx["recent_journal_entries"],
            "farm_summary": full_ctx["farm_summary"],
            "season_context": full_ctx["season_context"],
        }
