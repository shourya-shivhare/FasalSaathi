from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.models.farmer_profile import FarmerProfile
from backend.app.models.farm import Farm
from backend.app.models.crop_cycle import CropCycle
from backend.app.models.enums import CropCycleStatus, PreferredLanguage

def build_farmer_context(user_id: int, db: Session) -> dict:
    """
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
        "preferred_language": "en",
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
            context["soil_type"] = profile.soil_type.value if hasattr(profile.soil_type, 'value') else str(profile.soil_type)
        if profile.irrigation_source:
            context["irrigation_source"] = profile.irrigation_source.value if hasattr(profile.irrigation_source, 'value') else str(profile.irrigation_source)
            
        # Map preferred language
        if profile.preferred_language:
            lang_val = profile.preferred_language
            if isinstance(lang_val, PreferredLanguage):
                context["preferred_language"] = "hi" if lang_val == PreferredLanguage.HINDI else "en"
            else:
                context["preferred_language"] = "hi" if str(lang_val).upper() == "HINDI" else "en"

    # Fetch farms
    farms = db.query(Farm).filter(Farm.user_id == user_id).all()
    
    active_crops_from_cycles = []
    
    if farms:
        # Prioritize Farm details if available
        # We take details from the first farm as primary context
        primary_farm = farms[0]
        if primary_farm.state:
            context["state"] = primary_farm.state
        if primary_farm.district:
            context["district"] = primary_farm.district
        if primary_farm.village:
            context["village"] = primary_farm.village
            
        # Prioritize farm's soil_type and irrigation_source
        if primary_farm.soil_type:
            context["soil_type"] = primary_farm.soil_type.value if hasattr(primary_farm.soil_type, 'value') else str(primary_farm.soil_type)
        if primary_farm.irrigation_source:
            context["irrigation_source"] = primary_farm.irrigation_source.value if hasattr(primary_farm.irrigation_source, 'value') else str(primary_farm.irrigation_source)
            
        # For farm size, we can sum the total area of all farms the user has
        total_area = sum(f.total_area or 0.0 for f in farms)
        if total_area > 0:
            context["farm_size_acres"] = total_area
            
        # Query active crop cycles for all farms of this user
        farm_ids = [f.id for f in farms]
        active_cycles = db.query(CropCycle).filter(
            CropCycle.farm_id.in_(farm_ids),
            CropCycle.status == CropCycleStatus.ACTIVE
        ).all()
        
        active_crops_from_cycles = list(set(cycle.crop_name for cycle in active_cycles if cycle.crop_name))

    # Determine active crops list
    if active_crops_from_cycles:
        context["active_crops"] = active_crops_from_cycles
    elif profile and profile.crops_grown:
        # Fallback to crops_grown from the profile only as migration-compatibility
        if isinstance(profile.crops_grown, list):
            context["active_crops"] = profile.crops_grown
        elif isinstance(profile.crops_grown, str):
            # Parse comma-separated string if it was stored that way
            context["active_crops"] = [c.strip() for c in profile.crops_grown.split(",") if c.strip()]
            
    return context

class ContextBuilder:
    """
    Backward-compatibility class wrapping build_farmer_context
    used by legacy chat and multi-agent pipeline routes.
    """
    def __init__(self, db: Session):
        self.db = db

    def build(self, user: User) -> dict:
        flat = build_farmer_context(user.id, self.db)
        
        # Build nested structure for backward compatibility with agents & chat proxies
        active_crops_nested = [{"crop_name": c} for c in flat["active_crops"]]
        
        profile_dict = {
            "state": flat["state"] or "",
            "district": flat["district"] or "",
            "village": flat["village"] or "",
            "category": "marginal",
            "annual_income": flat["annual_income"],
            "gender": None,
            "age": None,
            "land_size_acres": flat["farm_size_acres"]
        }
        
        if user.farmer_profile:
            if user.farmer_profile.category:
                profile_dict["category"] = user.farmer_profile.category
            if user.farmer_profile.gender:
                profile_dict["gender"] = user.farmer_profile.gender.value if hasattr(user.farmer_profile.gender, 'value') else str(user.farmer_profile.gender)
            if user.farmer_profile.age:
                profile_dict["age"] = user.farmer_profile.age

        return {
            **flat,
            "profile": profile_dict,
            "active_crops": active_crops_nested
        }
