"""Build ownership-validated farmer context for downstream AI services."""

from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.services.farmer_data_service import FarmerDataService


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
    """Build rich and legacy-compatible context from a single data snapshot."""

    def __init__(self, db: Session):
        self.db = db

    def build(self, user: User) -> dict:
        full_context = FarmerDataService(self.db, user.id).get_full_context()
        flat = _build_legacy_context(full_context)
        profile = dict(full_context["profile"])

        # These aliases remain for older AI agents while rich data stays nested.
        profile["state"] = profile.get("state") or flat["state"]
        profile["district"] = profile.get("district") or flat["district"]
        profile["village"] = profile.get("village") or flat["village"]
        profile["land_size_acres"] = (
            profile.get("farm_size_acres") or flat["farm_size_acres"]
        )

        return {
            **flat,
            "profile": profile,
            "active_crops": full_context["active_crops"],
            "farms": full_context["farms"],
            "crop_history": full_context["crop_history"],
            "pest_history": full_context["pest_history"],
            "recent_journal_entries": full_context["recent_journal_entries"],
            "farm_summary": full_context["farm_summary"],
            "season_context": full_context["season_context"],
        }
