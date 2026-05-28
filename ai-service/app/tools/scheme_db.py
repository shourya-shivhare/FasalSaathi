"""
Government Scheme Database — searchable wrapper over seed_schemes.
Used by the scheme_recommendation node via ToolRegistry.
"""
from __future__ import annotations

from app.data.seed_schemes import SEED_SCHEMES


def get_all_schemes() -> list[dict]:
    """Return all available government schemes."""
    return SEED_SCHEMES


def search_schemes(
    state: str | None = None,
    tags: list[str] | None = None,
    income: int | None = None,
    gender: str | None = None,
    farmer_category: str | None = None,
) -> list[dict]:
    """
    Filter schemes by state, category tags, income, gender.
    Returns matching schemes from the seed database.
    """
    schemes = list(SEED_SCHEMES)

    if state:
        s_lower = state.lower()
        schemes = [
            s for s in schemes
            if not s.get("state_applicability")  # empty list = all-India
            or s_lower in [x.lower() for x in s.get("state_applicability", [])]
        ]

    if tags:
        t_lower = {t.lower() for t in tags}
        schemes = [
            s for s in schemes
            if t_lower & {t.lower() for t in s.get("category_tags", [])}
        ]

    if income is not None:
        schemes = [
            s for s in schemes
            if not s.get("income_limit") or s["income_limit"] >= income
        ]

    if gender:
        schemes = [
            s for s in schemes
            if not s.get("gender_specific")
            or s["gender_specific"].lower() == gender.lower()
            or s.get("gender_specific", "").lower() == "all"
        ]

    return schemes
