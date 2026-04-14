"""
Government Scheme Recommendation Agent
───────────────────────────────────────
1. Pre-filters the 25-scheme seed DB by state, category, age, gender, income.
2. Sends the filtered list + farmer profile to the LLM for ranking and
   plain-language explanations.
3. Returns scored, ranked results.

Independently callable via its own router OR via the orchestrator pipeline.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

from app.core.llm import get_llm, safe_llm_invoke
from app.data.seed_schemes import filter_schemes_by_state, get_all_schemes
from app.schemas.agent_schemas import (
    MatchedScheme,
    SchemeRecommendationRequest,
    SchemeRecommendationResponse,
)

logger = logging.getLogger(__name__)

# ── Prompt ────────────────────────────────────────────────────────────────────

SCHEME_RECOMMENDATION_PROMPT = """\
You are a Government Scheme Advisor for Indian farmers.

FARMER PROFILE:
- State: {state}
- District: {district}
- Category: {farmer_category} farmer
- Crops: {crop_types}
- Annual Income: ₹{annual_income}
- Gender: {gender}
- Age: {age}

{extra_context}

AVAILABLE SCHEMES (pre-filtered for this farmer's state):
{schemes_json}

TASK:
From the schemes listed above, pick the TOP 5-8 most relevant for this farmer.
For each scheme, provide:
1. An eligibility_score from 0.0 to 1.0 (how likely the farmer qualifies)
2. A brief why_recommended (1-2 sentences in simple language explaining why)

Return ONLY a JSON array:
[
  {{
    "scheme_name": "exact name from the list",
    "eligibility_score": 0.95,
    "why_recommended": "Simple explanation"
  }}
]

Rules:
- Only include schemes the farmer is realistically eligible for
- Rank by relevance (most useful first)
- If gender_specific is set, only include if farmer's gender matches
- Check age_limit constraints
- Check income_limit if applicable
- Return ONLY the JSON array, no other text
"""


async def run_scheme_recommendation_agent(
    request: SchemeRecommendationRequest,
) -> SchemeRecommendationResponse:
    """
    Execute the scheme recommendation agent.

    Args:
        request: Farmer's demographic and location profile.

    Returns:
        SchemeRecommendationResponse with ranked, scored scheme matches.
    """
    logger.info(
        "🏛️  Scheme Agent invoked — state=%s, category=%s, age=%s, gender=%s",
        request.state, request.farmer_category, request.age, request.gender,
    )

    # ── Step 1: Pre-filter by state ──────────────────────────────────────────
    candidates = filter_schemes_by_state(request.state)

    # ── Step 2: Hard-filter by age / gender / income ─────────────────────────
    candidates = _hard_filter(candidates, request)
    logger.info("Pre-filter: %d schemes remain after state/age/gender/income filter", len(candidates))

    if not candidates:
        return SchemeRecommendationResponse(
            matched_schemes=[],
            total_found=0,
            farmer_summary=_build_farmer_summary(request),
        )

    # ── Step 3: Build extra context from upstream agents ─────────────────────
    extra_lines = []
    ctx = request.context_from_agents
    if ctx.get("crop_recommendations"):
        extra_lines.append(f"Recommended crops: {ctx['crop_recommendations']}")
    if ctx.get("pest_detection"):
        extra_lines.append(f"Pest issues: {ctx['pest_detection']}")
    extra_context = "\n".join(extra_lines) if extra_lines else "No additional context."

    # ── Step 4: LLM ranking ──────────────────────────────────────────────────
    schemes_for_llm = [
        {
            "scheme_name": s["scheme_name"],
            "ministry": s["ministry"],
            "benefits": s["benefits"],
            "eligibility_criteria": s["eligibility_criteria"],
            "category_tags": s["category_tags"],
        }
        for s in candidates
    ]

    prompt_text = SCHEME_RECOMMENDATION_PROMPT.format(
        state=request.state,
        district=request.district or "N/A",
        farmer_category=request.farmer_category,
        crop_types=", ".join(request.crop_types) if request.crop_types else "General",
        annual_income=request.annual_income or "Not specified",
        gender=request.gender or "Not specified",
        age=request.age or "Not specified",
        extra_context=extra_context,
        schemes_json=json.dumps(schemes_for_llm, indent=2),
    )

    llm = get_llm(temperature=0.2)
    raw = safe_llm_invoke(llm, prompt_text, fallback="__LLM_FAILED__")

    # ── Step 5: Parse and enrich ─────────────────────────────────────────────
    if raw == "__LLM_FAILED__":
        # LLM unavailable — return top candidates with default scores
        logger.warning("LLM unavailable, returning pre-filtered candidates as fallback")
        matched = [
            MatchedScheme(
                scheme_name=s["scheme_name"],
                ministry=s["ministry"],
                eligibility_score=0.7,
                benefits=s["benefits"],
                why_recommended=s["eligibility_criteria"],
                apply_url=s.get("apply_url", ""),
                category_tags=s.get("category_tags", []),
            )
            for s in candidates[:8]
        ]
    else:
        matched = _parse_scheme_response(raw, candidates)
    matched.sort(key=lambda s: s.eligibility_score, reverse=True)

    logger.info("🏛️  Scheme Agent returning %d matches", len(matched))

    return SchemeRecommendationResponse(
        matched_schemes=matched,
        total_found=len(matched),
        farmer_summary=_build_farmer_summary(request),
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _hard_filter(schemes: list[dict], req: SchemeRecommendationRequest) -> list[dict]:
    """Remove schemes the farmer definitely can't qualify for."""
    result = []
    for s in schemes:
        # Gender check
        if s.get("gender_specific") and req.gender:
            if s["gender_specific"].lower() != req.gender.lower():
                continue

        # Age check
        age_limit = s.get("age_limit")
        if age_limit and req.age:
            if req.age < age_limit.get("min", 0):
                continue
            if req.age > age_limit.get("max", 200):
                continue

        # Income check
        if s.get("income_limit") and req.annual_income:
            if req.annual_income > s["income_limit"]:
                continue

        result.append(s)
    return result


def _parse_scheme_response(raw: str, candidates: list[dict]) -> list[MatchedScheme]:
    """Parse LLM JSON and enrich with full scheme data."""
    # Build lookup by name
    scheme_lookup = {s["scheme_name"].lower(): s for s in candidates}

    try:
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
        rankings = json.loads(text)
    except Exception as e:
        logger.warning("Failed to parse scheme LLM response: %s — using fallback", e)
        # Fallback: return top 5 candidates with default scores
        return [
            MatchedScheme(
                scheme_name=s["scheme_name"],
                ministry=s["ministry"],
                eligibility_score=0.7,
                benefits=s["benefits"],
                why_recommended=s["eligibility_criteria"],
                apply_url=s.get("apply_url", ""),
                category_tags=s.get("category_tags", []),
            )
            for s in candidates[:5]
        ]

    result = []
    for r in rankings[:8]:
        name = r.get("scheme_name", "")
        full = scheme_lookup.get(name.lower())
        if not full:
            # Fuzzy match by substring
            for key, val in scheme_lookup.items():
                if name.lower() in key or key in name.lower():
                    full = val
                    break
        if not full:
            continue

        result.append(MatchedScheme(
            scheme_name=full["scheme_name"],
            ministry=full["ministry"],
            eligibility_score=min(max(float(r.get("eligibility_score", 0.5)), 0.0), 1.0),
            benefits=full["benefits"],
            why_recommended=r.get("why_recommended", full["eligibility_criteria"]),
            apply_url=full.get("apply_url", ""),
            category_tags=full.get("category_tags", []),
        ))

    return result


def _build_farmer_summary(req: SchemeRecommendationRequest) -> str:
    """Build a brief profile recap."""
    parts = [f"{req.farmer_category.title()} farmer in {req.state}"]
    if req.district:
        parts[0] += f" ({req.district})"
    if req.crop_types:
        parts.append(f"grows {', '.join(req.crop_types)}")
    if req.age:
        parts.append(f"age {req.age}")
    if req.gender:
        parts.append(req.gender)
    if req.annual_income:
        parts.append(f"income ₹{req.annual_income:,}")
    return ". ".join(parts) + "."
