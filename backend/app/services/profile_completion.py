from backend.app.models.farmer_profile import FarmerProfile

def evaluate_profile_completion(profile: FarmerProfile) -> bool:
    """
    Checks if required fields are present and valid.
    Required: full_name, state, district, village, farm_size_acres, preferred_language.
    """
    required_fields = [
        profile.full_name,
        profile.state,
        profile.district,
        profile.village,
        profile.farm_size_acres,
        profile.preferred_language
    ]
    return all(field is not None and str(field).strip() != "" for field in required_fields)
