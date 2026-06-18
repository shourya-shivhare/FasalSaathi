"""
Farmer Data Tools — extraction utilities for the data_retrieval and
data_analysis nodes.

These tools work with the farmer context already injected into graph state
by the backend ContextBuilder.  They do NOT make direct database calls.

The backend enforces ownership validation (user_id checks) before the
data ever reaches the AI service. These tools are a structured interface
over the injected context.

Security note: All data in farmer_profile was already filtered by user_id
in the backend's FarmerDataService before being sent to the AI service.
"""
from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class FarmerDataTools:
    """
    Provides structured access to farmer data from the graph state's
    farmer_profile dict.  Each method returns a dict with:
      - "found": bool
      - "data": the records (or empty)
      - "count": number of records
      - "summary": human-readable one-liner
    """

    def __init__(self, farmer_profile: dict):
        self._profile = farmer_profile or {}

    # ── Profile ──────────────────────────────────────────────────────────

    def get_farmer_profile(self) -> dict:
        """Return the farmer's profile information."""
        # Profile data can be at top level or in nested "profile" key
        profile = self._profile.get("profile") or {}

        # Merge top-level fields if profile dict is sparse
        merged = {
            "name": profile.get("name") or self._profile.get("name"),
            "state": profile.get("state") or self._profile.get("state"),
            "district": profile.get("district") or self._profile.get("district"),
            "village": profile.get("village") or self._profile.get("village"),
            "category": profile.get("category") or self._profile.get("farmer_category"),
            "annual_income": profile.get("annual_income") or self._profile.get("annual_income"),
            "gender": profile.get("gender") or self._profile.get("gender"),
            "age": profile.get("age") or self._profile.get("age"),
            "land_size_acres": (
                profile.get("land_size_acres")
                or profile.get("farm_size_acres")
                or self._profile.get("land_size_acres")
            ),
            "preferred_language": (
                profile.get("preferred_language")
                or self._profile.get("preferred_language", "ENGLISH")
            ),
            "soil_type": profile.get("soil_type") or self._profile.get("soil_type"),
            "irrigation_source": (
                profile.get("irrigation_source")
                or self._profile.get("irrigation_source")
            ),
        }

        # Preferred language has a default even when no profile exists.
        identity_fields = (
            "name", "state", "district", "village", "category",
            "annual_income", "gender", "age", "land_size_acres",
            "soil_type", "irrigation_source",
        )
        has_data = any(merged.get(field) is not None for field in identity_fields)
        return {
            "found": has_data,
            "data": merged,
            "count": 1 if has_data else 0,
            "summary": (
                f"Profile: {merged.get('name') or 'unnamed'}, "
                f"{merged.get('state') or 'unknown state'}, "
                f"{merged.get('district') or 'unknown district'}"
                if has_data
                else "No farmer profile found."
            ),
        }

    # ── Farms ────────────────────────────────────────────────────────────

    def list_farms(self) -> dict:
        """List all farms from the injected context."""
        farms = self._profile.get("farms", [])
        return {
            "found": len(farms) > 0,
            "data": farms,
            "count": len(farms),
            "summary": (
                f"{len(farms)} farm(s) registered."
                if farms
                else "No farms registered in your account."
            ),
        }

    # ── Active Crops ─────────────────────────────────────────────────────

    def list_active_crops(self) -> dict:
        """List active crop cycles from the injected context."""
        active_crops = self._profile.get("active_crops", [])

        # Filter to only ACTIVE status if status field exists
        active = [
            c for c in active_crops
            if c.get("status", "ACTIVE") == "ACTIVE"
        ]

        return {
            "found": len(active) > 0,
            "data": active,
            "count": len(active),
            "summary": (
                f"{len(active)} active crop cycle(s)."
                if active
                else "No active crop cycles found."
            ),
        }

    # ── Crop History ─────────────────────────────────────────────────────

    def list_crop_history(self) -> dict:
        """List completed/historical crop cycles."""
        history = self._profile.get("crop_history", [])
        return {
            "found": len(history) > 0,
            "data": history,
            "count": len(history),
            "summary": (
                f"{len(history)} historical crop cycle(s)."
                if history
                else "No crop history available."
            ),
        }

    # ── Pest History ─────────────────────────────────────────────────────

    def get_pest_history(self) -> dict:
        """Retrieve pest detection history from context."""
        # Check both "pest_history" and "recent_pests" keys
        pest_data = (
            self._profile.get("pest_history")
            or self._profile.get("recent_pests")
            or []
        )
        return {
            "found": len(pest_data) > 0,
            "data": pest_data,
            "count": len(pest_data),
            "summary": (
                f"{len(pest_data)} pest detection(s) on record."
                if pest_data
                else "No pest detections found in your history."
            ),
        }

    # ── Journal Entries ──────────────────────────────────────────────────

    def get_journal_entries(self) -> dict:
        """Retrieve recent journal entries."""
        entries = self._profile.get("recent_journal_entries", [])
        return {
            "found": len(entries) > 0,
            "data": entries,
            "count": len(entries),
            "summary": (
                f"{len(entries)} recent journal entry/entries."
                if entries
                else "No journal entries found."
            ),
        }

    # ── Farm Summary ─────────────────────────────────────────────────────

    def get_farm_summary(self) -> dict:
        """Return aggregate farm summary statistics."""
        summary = self._profile.get("farm_summary", {})
        has_data = summary.get("total_farms", 0) > 0
        return {
            "found": has_data,
            "data": summary,
            "count": 1 if has_data else 0,
            "summary": (
                f"{summary.get('total_farms', 0)} farms, "
                f"{summary.get('total_registered_area', 0):.1f} acres, "
                f"{summary.get('active_crop_count', 0)} active crops, "
                f"{summary.get('recent_pest_count', 0)} recent pest detections"
                if has_data
                else "No farm data available."
            ),
        }

    # ── Season Context ───────────────────────────────────────────────────

    def get_season_context(self) -> dict:
        """Return current season information."""
        ctx = self._profile.get("season_context", {})
        return {
            "found": bool(ctx.get("current_season")),
            "data": ctx,
            "count": 1 if ctx else 0,
            "summary": (
                f"Current season: {ctx.get('current_season', 'Unknown')}, "
                f"{ctx.get('season_active_crops', 0)} active crops this season."
                if ctx
                else "Season information not available."
            ),
        }

    # ── Convenience: determine what data sections to include ─────────────

    def determine_relevant_sections(self, query: str) -> list[str]:
        """
        Given a user query, determine which data sections are relevant.
        Returns a list of section names to include in the response.
        """
        query_lower = query.lower()
        sections = []

        # Farm-related keywords
        if any(kw in query_lower for kw in [
            "farm", "land", "area", "acre", "soil", "irrigation",
            "kheti", "khet", "zameen",
        ]):
            sections.append("farms")

        # Crop-related keywords
        if any(kw in query_lower for kw in [
            "crop", "plant", "grow", "sow", "harvest", "cycle",
            "fasal", "ugana",
        ]):
            sections.append("active_crops")
            sections.append("crop_history")

        # Pest-related keywords
        if any(kw in query_lower for kw in [
            "pest", "disease", "detect", "scan", "bug", "insect",
            "keeda", "rog", "bimari",
        ]):
            sections.append("pest_history")

        # Profile-related keywords
        if any(kw in query_lower for kw in [
            "profile", "my info", "my information", "my details",
            "who am i", "my account",
        ]):
            sections.append("profile")

        # Journal-related keywords
        if any(kw in query_lower for kw in [
            "journal", "log", "entry", "entries", "record", "activity",
        ]):
            sections.append("journal_entries")

        # Generic "show everything" queries
        if any(kw in query_lower for kw in [
            "everything", "all data", "all my", "summary", "overview",
            "dashboard",
        ]):
            sections.extend(["farms", "active_crops", "pest_history", "profile"])

        # If no specific sections matched but it's a data query, include farms + crops
        if not sections:
            sections = ["farms", "active_crops"]

        return list(dict.fromkeys(sections))  # deduplicate preserving order

    def get_sections_data(self, sections: list[str]) -> dict[str, dict]:
        """Retrieve data for the specified sections."""
        section_methods = {
            "profile": self.get_farmer_profile,
            "farms": self.list_farms,
            "active_crops": self.list_active_crops,
            "crop_history": self.list_crop_history,
            "pest_history": self.get_pest_history,
            "journal_entries": self.get_journal_entries,
            "farm_summary": self.get_farm_summary,
            "season_context": self.get_season_context,
        }

        result = {}
        for section in sections:
            method = section_methods.get(section)
            if method:
                result[section] = method()

        return result
