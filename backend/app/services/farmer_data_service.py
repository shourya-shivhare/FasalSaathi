"""
Farmer Data Aggregation Service — centralized, ownership-validated
retrieval of all farmer data.

Every method enforces:
    record.user_id == user_id  (or farm ownership for nested records)

Consumers:
  - ContextBuilder (backend)
  - Future REST APIs
  - AI-service farmer data tools (via context injection)
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.models.farmer_profile import FarmerProfile
from backend.app.models.farm import Farm
from backend.app.models.crop_cycle import CropCycle
from backend.app.models.crop_journal import CropJournalEntry
from backend.app.models.pest_detection_history import PestDetectionHistory
from backend.app.models.enums import CropCycleStatus, PreferredLanguage


def _enum_val(v):
    """Safely extract .value from an enum, or str() it."""
    return v.value if hasattr(v, "value") else str(v) if v else None


def _determine_current_season() -> str:
    """Determine the current agricultural season based on the month."""
    month = datetime.now().month
    if month in (6, 7, 8, 9, 10):
        return "KHARIF"
    elif month in (11, 12, 1, 2, 3):
        return "RABI"
    else:
        return "ZAID"


class FarmerDataService:
    """
    Centralized farmer data aggregation with ownership validation.

    SECURITY INVARIANT: Every query filters by user_id or by farm_ids
    that belong to the user. No method ever returns another farmer's data.
    """

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        # Cache farm IDs after first load so nested queries don't re-fetch
        self._farm_ids: Optional[List[int]] = None
        self._farm_id_to_name: Optional[dict] = None
        self._all_cycles: Optional[List[CropCycle]] = None
        self._cycle_id_map: Optional[dict] = None

    # ── Ownership-validated farm IDs ─────────────────────────────────────

    def _get_farm_ids(self) -> List[int]:
        """Lazy-load and cache farm IDs for this user."""
        if self._farm_ids is None:
            farms = self.db.query(Farm).filter(Farm.user_id == self.user_id).all()
            self._farm_ids = [f.id for f in farms]
            self._farm_id_to_name = {f.id: f.farm_name for f in farms}
        return self._farm_ids

    def _get_farm_name(self, farm_id: int) -> str:
        """Get farm name by id (lazy-loads farms if needed)."""
        self._get_farm_ids()
        return self._farm_id_to_name.get(farm_id, "Unknown")

    def _get_all_cycles(self) -> List[CropCycle]:
        """Lazy-load all crop cycles for user's farms."""
        if self._all_cycles is None:
            farm_ids = self._get_farm_ids()
            if farm_ids:
                self._all_cycles = (
                    self.db.query(CropCycle)
                    .filter(CropCycle.farm_id.in_(farm_ids))
                    .order_by(CropCycle.updated_at.desc())
                    .all()
                )
            else:
                self._all_cycles = []
        return self._all_cycles

    def _get_cycle_id_map(self) -> dict:
        """Map cycle_id → {crop_name, farm_name} for pest/journal context."""
        if self._cycle_id_map is None:
            self._cycle_id_map = {}
            for c in self._get_all_cycles():
                self._cycle_id_map[c.id] = {
                    "crop_name": c.crop_name,
                    "farm_name": self._get_farm_name(c.farm_id),
                }
        return self._cycle_id_map

    # ── Profile ──────────────────────────────────────────────────────────

    def get_farmer_profile(self) -> dict:
        """
        Retrieve the full farmer profile.
        Ownership: FarmerProfile.user_id == self.user_id
        """
        profile = (
            self.db.query(FarmerProfile)
            .filter(FarmerProfile.user_id == self.user_id)
            .first()
        )
        if not profile:
            return {
                "name": None,
                "state": None,
                "district": None,
                "village": None,
                "category": None,
                "annual_income": None,
                "gender": None,
                "age": None,
                "farm_size_acres": None,
                "preferred_language": "ENGLISH",
                "soil_type": None,
                "irrigation_source": None,
                "crops_grown": [],
                "profile_completed": False,
            }

        lang = "ENGLISH"
        if profile.preferred_language:
            lang_val = profile.preferred_language
            if isinstance(lang_val, PreferredLanguage):
                lang = "HINDI" if lang_val == PreferredLanguage.HINDI else "ENGLISH"
            else:
                lang = "HINDI" if str(lang_val).upper() == "HINDI" else "ENGLISH"

        return {
            "name": profile.full_name,
            "state": profile.state,
            "district": profile.district,
            "village": profile.village,
            "category": profile.category,
            "annual_income": profile.annual_income,
            "gender": _enum_val(profile.gender),
            "age": profile.age,
            "farm_size_acres": profile.farm_size_acres,
            "preferred_language": lang,
            "soil_type": _enum_val(profile.soil_type),
            "irrigation_source": _enum_val(profile.irrigation_source),
            "crops_grown": profile.crops_grown or [],
            "profile_completed": profile.profile_completed,
        }

    # ── Farms ────────────────────────────────────────────────────────────

    def list_farms(self) -> List[dict]:
        """
        List all farms for this user with active crop counts.
        Ownership: Farm.user_id == self.user_id
        """
        farms = self.db.query(Farm).filter(Farm.user_id == self.user_id).all()
        self._farm_ids = [f.id for f in farms]
        self._farm_id_to_name = {f.id: f.farm_name for f in farms}

        result = []
        for f in farms:
            # Count active crops for this farm
            active_count = (
                self.db.query(CropCycle)
                .filter(
                    CropCycle.farm_id == f.id,
                    CropCycle.status == CropCycleStatus.ACTIVE,
                )
                .count()
            )
            result.append({
                "farm_id": f.id,
                "farm_name": f.farm_name,
                "state": f.state,
                "district": f.district,
                "village": f.village,
                "total_area": f.total_area,
                "soil_type": _enum_val(f.soil_type),
                "irrigation_source": _enum_val(f.irrigation_source),
                "created_at": str(f.created_at) if f.created_at else None,
                "active_crop_count": active_count,
            })

        return result

    # ── Crop Cycles ──────────────────────────────────────────────────────

    def list_active_crops(self) -> List[dict]:
        """
        List all active crop cycles with farm associations.
        Ownership: CropCycle.farm_id ∈ user's farm IDs
        """
        all_cycles = self._get_all_cycles()
        return [
            self._cycle_to_dict(c)
            for c in all_cycles
            if c.status == CropCycleStatus.ACTIVE
        ]

    def list_crop_history(self, limit: int = 20) -> List[dict]:
        """
        List completed/abandoned crop cycles.
        Ownership: CropCycle.farm_id ∈ user's farm IDs
        """
        all_cycles = self._get_all_cycles()
        historical = [
            {
                "crop_name": c.crop_name,
                "crop_variety": c.crop_variety,
                "season": _enum_val(c.season),
                "year": c.year,
                "status": _enum_val(c.status),
                "farm_name": self._get_farm_name(c.farm_id),
            }
            for c in all_cycles
            if c.status != CropCycleStatus.ACTIVE
        ]
        return historical[:limit]

    def _cycle_to_dict(self, c: CropCycle) -> dict:
        return {
            "crop_cycle_id": c.id,
            "crop_name": c.crop_name,
            "crop_variety": c.crop_variety,
            "season": _enum_val(c.season),
            "year": c.year,
            "sowing_date": str(c.sowing_date) if c.sowing_date else None,
            "expected_harvest_date": str(c.expected_harvest_date) if c.expected_harvest_date else None,
            "current_stage": _enum_val(c.current_stage),
            "area_under_crop": c.area_under_crop,
            "status": _enum_val(c.status),
            "farm_name": self._get_farm_name(c.farm_id),
            "farm_id": c.farm_id,
            "last_updated_at": str(c.updated_at) if c.updated_at else None,
        }

    # ── Pest Detection History ───────────────────────────────────────────

    def get_pest_history(self, limit: int = 20) -> List[dict]:
        """
        Retrieve pest detection history.
        Ownership: PestDetectionHistory.user_id == self.user_id
        """
        records = (
            self.db.query(PestDetectionHistory)
            .filter(PestDetectionHistory.user_id == self.user_id)
            .order_by(PestDetectionHistory.created_at.desc())
            .limit(limit)
            .all()
        )

        cycle_map = self._get_cycle_id_map()
        result = []
        for p in records:
            crop_info = cycle_map.get(p.crop_cycle_id, {})
            result.append({
                "disease_name": p.disease_name,
                "confidence": p.confidence,
                "source": _enum_val(p.source),
                "created_at": str(p.created_at) if p.created_at else None,
                "crop_name": crop_info.get("crop_name"),
                "farm_name": crop_info.get("farm_name"),
            })
        return result

    # ── Journal Entries ──────────────────────────────────────────────────

    def get_recent_journal_entries(self, limit: int = 15) -> List[dict]:
        """
        Retrieve recent journal entries across all user's crop cycles.
        Ownership: via CropCycle.farm_id ∈ user's farm IDs
        """
        all_cycles = self._get_all_cycles()
        cycle_ids = [c.id for c in all_cycles]
        if not cycle_ids:
            return []

        records = (
            self.db.query(CropJournalEntry)
            .filter(CropJournalEntry.crop_cycle_id.in_(cycle_ids))
            .order_by(CropJournalEntry.created_at.desc())
            .limit(limit)
            .all()
        )

        cycle_map = self._get_cycle_id_map()
        result = []
        for j in records:
            j_info = cycle_map.get(j.crop_cycle_id, {})
            result.append({
                "entry_type": _enum_val(j.entry_type),
                "title": j.title,
                "description": j.description,
                "created_at": str(j.created_at) if j.created_at else None,
                "crop_name": j_info.get("crop_name"),
                "farm_name": j_info.get("farm_name"),
            })
        return result

    # ── Farm Summary ─────────────────────────────────────────────────────

    def get_farm_summary(self) -> dict:
        """Aggregate statistics for the farmer."""
        farms = self.list_farms()
        active_crops = self.list_active_crops()
        all_cycles = self._get_all_cycles()
        pest_history = self.get_pest_history()
        journal_entries = self.get_recent_journal_entries()
        crop_history = [c for c in all_cycles if c.status != CropCycleStatus.ACTIVE]

        return {
            "total_farms": len(farms),
            "total_registered_area": sum(f.get("total_area") or 0 for f in farms),
            "active_crop_count": len(active_crops),
            "total_crop_cycles": len(all_cycles),
            "completed_crop_cycles": len(crop_history),
            "recent_pest_count": len(pest_history),
            "recent_journal_count": len(journal_entries),
        }

    # ── Season Context ───────────────────────────────────────────────────

    def get_season_context(self) -> dict:
        """Determine current season and count relevant active crops."""
        current_season = _determine_current_season()
        active_crops = self.list_active_crops()
        season_crops = [c for c in active_crops if c.get("season") == current_season]
        return {
            "current_season": current_season,
            "season_active_crops": len(season_crops),
        }

    # ── Full Context (all data) ──────────────────────────────────────────

    def get_full_context(self) -> dict:
        """
        Build the complete farmer data context.
        Used by ContextBuilder to inject into AI requests.
        """
        profile = self.get_farmer_profile()
        farms = self.list_farms()
        active_crops = self.list_active_crops()
        crop_history = self.list_crop_history()
        pest_history = self.get_pest_history()
        journal_entries = self.get_recent_journal_entries()
        farm_summary = self.get_farm_summary()
        season_context = self.get_season_context()

        return {
            "profile": profile,
            "farms": farms,
            "active_crops": active_crops,
            "crop_history": crop_history,
            "pest_history": pest_history,
            "recent_journal_entries": journal_entries,
            "farm_summary": farm_summary,
            "season_context": season_context,
        }
