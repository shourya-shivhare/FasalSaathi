"""
Crop Knowledge Base Service — ground truth agricultural database for crop recommendations.
Stores and queries detailed crop profiles.
No LLM or recommendation logic.
"""
from __future__ import annotations

import json
import os
import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

logger = logging.getLogger(__name__)


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class MinMaxRange(BaseModel):
    min: float
    max: Optional[float] = None


class MinMaxRangeInt(BaseModel):
    min: int
    max: Optional[int] = None


class CropRotationCompatibility(BaseModel):
    preferred_previous_crops: List[str] = Field(default_factory=list)
    avoid_previous_crops: List[str] = Field(default_factory=list)


class CropProfile(BaseModel):
    """Agronomic profile of a single crop covering 27 agricultural attributes."""
    model_config = ConfigDict(populate_by_name=True)

    crop_name: str = Field(..., alias="crop_name")
    scientific_name: str
    suitable_states: List[str]
    suitable_districts: List[str]
    soil_types: List[str]
    ideal_ph: MinMaxRange
    nitrogen_requirement_kg_ha: float
    phosphorus_requirement_kg_ha: float
    potassium_requirement_kg_ha: float
    organic_carbon_requirement_pct: MinMaxRange
    temperature_range_c: MinMaxRange
    rainfall_range_mm: MinMaxRange
    humidity_range_pct: MinMaxRange
    water_requirement: str  # "Low", "Moderate", "High"
    irrigation_requirement: List[str]
    growing_duration_days: MinMaxRangeInt
    season: str  # "Kharif", "Rabi", "Zaid"
    sowing_window: List[str]
    harvest_window: List[str]
    sunlight_requirement: str
    drainage_requirement: str
    expected_yield: str
    disease_risks: List[str]
    pest_risks: List[str]
    crop_rotation_compatibility: CropRotationCompatibility
    fertilizer_recommendation: List[str]
    micronutrient_requirement: List[str]


# ── Service Implementation ───────────────────────────────────────────────────

class CropKnowledgeBaseService:
    """
    Service for loading and querying crop profiles.
    Decoupled from LLM logic.
    """

    def __init__(self, json_path: Optional[str] = None):
        if not json_path:
            # Resolve default path relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.normpath(
                os.path.join(current_dir, "..", "data", "crop_profiles.json")
            )

        self.json_path = json_path
        self._profiles: Dict[str, CropProfile] = {}
        self._load_profiles()

    def _load_profiles(self) -> None:
        """Load crop profiles from the JSON data file."""
        if not os.path.exists(self.json_path):
            logger.error("Crop profiles file not found at %s", self.json_path)
            return

        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for crop_data in data:
                try:
                    profile = CropProfile(**crop_data)
                    # Key by lowercase name for easy lookup
                    self._profiles[profile.crop_name.lower()] = profile
                except Exception as ve:
                    logger.error(
                        "Validation error for crop %s: %s",
                        crop_data.get("crop_name", "Unknown"),
                        ve,
                    )
            logger.info("Successfully loaded %d crop profiles from %s", len(self._profiles), self.json_path)
        except Exception as e:
            logger.error("Failed to load crop profiles JSON: %s", e)

    def get_crop_profile(self, crop_name: str) -> Optional[CropProfile]:
        """
        Retrieve a specific crop profile by name (case-insensitive).
        Returns None if the crop is not in the knowledge base.
        """
        if not crop_name:
            return None
        return self._profiles.get(crop_name.strip().lower())

    def list_all_crops(self) -> List[CropProfile]:
        """Return all crop profiles in the knowledge base."""
        return list(self._profiles.values())

    def find_crops_by_filters(
        self,
        state: str,
        district: Optional[str] = None,
        soil_type: Optional[str] = None,
        season: Optional[str] = None,
    ) -> List[CropProfile]:
        """
        Filter crop profiles based on geographical and environmental criteria.
        
        Args:
            state: Name of the Indian state.
            district: Optional name of the district.
            soil_type: Optional soil type of the plot.
            season: Optional season (Kharif/Rabi/Zaid).

        Returns:
            List of matching CropProfile objects.
        """
        results = []
        state_lower = state.strip().lower()
        district_lower = district.strip().lower() if district else None
        soil_lower = soil_type.strip().lower() if soil_type else None
        season_lower = season.strip().lower() if season else None

        for profile in self._profiles.values():
            # 1. State check
            suitable_states = [s.lower() for s in profile.suitable_states]
            if state_lower not in suitable_states and "all" not in suitable_states:
                continue

            # 2. District check
            if district_lower:
                suitable_districts = [d.lower() for d in profile.suitable_districts]
                if (
                    district_lower not in suitable_districts
                    and "*" not in suitable_districts
                    and "all" not in suitable_districts
                ):
                    continue

            # 3. Soil type check
            if soil_lower:
                profile_soils = [s.lower() for s in profile.soil_types]
                if soil_lower not in profile_soils:
                    continue

            # 4. Season check
            if season_lower:
                if profile.season.lower() != season_lower:
                    continue

            results.append(profile)

        return results
