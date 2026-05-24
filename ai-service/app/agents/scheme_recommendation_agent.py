"""
Government Scheme Recommendation Agent
───────────────────────────────────────
1. Pre-filters the 25-scheme seed DB by state, category, age, gender, income.
2. Computes a RULE-BASED base score per scheme (category match, income fit, etc.)
3. Sends the filtered list + farmer profile to the LLM for ranking refinement.
4. Blends rule-based + LLM scores for differentiated, robust results.

Independently callable via its own router OR via the orchestrator pipeline.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

from app.core.llm import get_llm, safe_llm_invoke_async
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
Rank the TOP 5-8 most relevant schemes for this specific farmer.

SCORING RUBRIC — use this strictly to assign eligibility_score:
  0.90–1.00 = PERFECT FIT: Farmer meets ALL criteria, scheme directly addresses their needs
  0.75–0.89 = STRONG FIT: Farmer meets most criteria, scheme is very relevant
  0.60–0.74 = MODERATE FIT: Farmer likely qualifies, but scheme is not a core need
  0.40–0.59 = WEAK FIT: Farmer may qualify on paper, but scheme is not very useful
  0.20–0.39 = POOR FIT: Farmer barely qualifies or scheme is tangentially relevant
  <0.20 = DO NOT INCLUDE

DIFFERENTIATION RULES:
- A {farmer_category} farmer should score HIGHEST on schemes with matching category tags
- Income-support schemes should rank higher for marginal/small farmers
- Crop insurance should rank higher if the farmer grows Kharif crops (higher risk season)
- Equipment/machinery schemes score LOWER for marginal farmers (less practical)
- State-specific schemes matching the farmer's state should get a BONUS
- If pest context is available, pest-related schemes should score higher
- DO NOT give all schemes the same score — spread them across the rubric

Return ONLY a JSON array (no markdown, no explanation):
[
  {{
    "scheme_name": "exact name from the list above",
    "eligibility_score": 0.93,
    "why_recommended": "1-2 sentence explanation specific to THIS farmer"
  }},
  {{
    "scheme_name": "another scheme",
    "eligibility_score": 0.71,
    "why_recommended": "Different explanation"
  }}
]

CRITICAL: Each scheme MUST have a DIFFERENT score. Spread scores across the 0.40–0.98 range.
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

    # ── Step 2.5: Compute rule-based scores ──────────────────────────────────
    rule_scores = _compute_rule_scores(candidates, request)

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
    raw = await safe_llm_invoke_async(llm, prompt_text, fallback="__LLM_FAILED__")

    # ── Step 5: Parse, blend scores, and enrich ──────────────────────────────
    if raw == "__LLM_FAILED__":
        # LLM unavailable — use rule-based scores as the sole ranking
        logger.warning("LLM unavailable, returning rule-based scored candidates as fallback")
        matched = _build_fallback_results(candidates, rule_scores)
    else:
        matched = _parse_scheme_response(raw, candidates, rule_scores)

    matched.sort(key=lambda s: s.eligibility_score, reverse=True)

    logger.info("🏛️  Scheme Agent returning %d matches", len(matched))

    return SchemeRecommendationResponse(
        matched_schemes=matched,
        total_found=len(matched),
        farmer_summary=_build_farmer_summary(request),
    )


# ── Rule-Based Scoring ───────────────────────────────────────────────────────

def _compute_rule_scores(schemes: list[dict], req: SchemeRecommendationRequest) -> dict[str, float]:
    """
    Compute a differentiated rule-based score (0.0-1.0) for each scheme.
    This ensures even without LLM, scores are varied and meaningful.
    """
    scores = {}
    category = req.farmer_category.lower() if req.farmer_category else "marginal"

    for s in schemes:
        score = 0.50  # Base score (passed all hard filters, so minimally eligible)
        tags = {t.lower() for t in s.get("category_tags", [])}

        # ── Category match (+0.15) ───────────────────────────────────────
        if category in tags or "all_farmers" in tags:
            score += 0.15
        # Extra bonus if scheme specifically targets this farmer's category
        if category in tags and "all_farmers" not in tags:
            score += 0.05  # More targeted = higher score

        # ── Income support bonus for small/marginal farmers (+0.10) ──────
        if category in ("marginal", "small") and "income_support" in tags:
            score += 0.10

        # ── Crop relevance (+0.05) ───────────────────────────────────────
        if req.crop_types:
            crop_lower = {c.lower() for c in req.crop_types}
            crop_tags = {"seeds", "pulses", "rice", "wheat", "cereals", "horticulture",
                         "fruits", "vegetables", "flowers", "spices"}
            if crop_lower & crop_tags & tags:
                score += 0.05

        # ── State-specific bonus (+0.08) ─────────────────────────────────
        if s.get("state_applicability"):  # State-specific scheme
            score += 0.08

        # ── Practical fit based on farmer category ───────────────────────
        # Machinery/infrastructure less practical for marginal farmers
        if category == "marginal" and ("machinery" in tags or "infrastructure" in tags):
            score -= 0.10
        # Credit/loan more relevant for small-medium farmers
        if category in ("small", "semi-medium", "medium") and "credit" in tags:
            score += 0.05

        # ── Insurance relevance ──────────────────────────────────────────
        if "crop_insurance" in tags:
            score += 0.05
        if "insurance" in tags and not req.age:
            score += 0.02  # No age = likely young = insurance useful

        # ── Women-specific bonus ─────────────────────────────────────────
        if req.gender and req.gender.lower() == "female" and "women" in tags:
            score += 0.10

        # ── Clamp to 0.30–0.98 range ─────────────────────────────────────
        score = min(max(score, 0.30), 0.98)
        scores[s["scheme_name"]] = round(score, 2)

    return scores


def _build_fallback_results(
    candidates: list[dict],
    rule_scores: dict[str, float],
) -> list[MatchedScheme]:
    """Build results using only rule-based scores (LLM unavailable)."""
    # Sort by rule score and take top 8
    sorted_candidates = sorted(
        candidates,
        key=lambda s: rule_scores.get(s["scheme_name"], 0.5),
        reverse=True,
    )

    return [
        MatchedScheme(
            scheme_name=s["scheme_name"],
            ministry=s["ministry"],
            eligibility_score=rule_scores.get(s["scheme_name"], 0.5),
            benefits=s["benefits"],
            why_recommended=s["eligibility_criteria"],
            apply_url=s.get("apply_url", ""),
            category_tags=s.get("category_tags", []),
        )
        for s in sorted_candidates[:8]
    ]


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


def _parse_scheme_response(
    raw: str,
    candidates: list[dict],
    rule_scores: dict[str, float],
) -> list[MatchedScheme]:
    """
    Parse LLM JSON and BLEND with rule-based scores for robust ranking.
    Final score = 0.6 * LLM_score + 0.4 * rule_score
    """
    # Build lookup by name
    scheme_lookup = {s["scheme_name"].lower(): s for s in candidates}

    try:
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
        rankings = json.loads(text)
    except Exception as e:
        logger.warning("Failed to parse scheme LLM response: %s — using rule-based fallback", e)
        return _build_fallback_results(candidates, rule_scores)

    result = []
    seen_scores = set()

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

        # Blend LLM score with rule-based score
        llm_score = min(max(float(r.get("eligibility_score", 0.5)), 0.0), 1.0)
        base_score = rule_scores.get(full["scheme_name"], 0.5)
        blended = round(0.6 * llm_score + 0.4 * base_score, 2)

        # Ensure no two schemes have the exact same score
        while blended in seen_scores:
            blended = round(blended - 0.01, 2)
        seen_scores.add(blended)

        blended = min(max(blended, 0.10), 0.98)

        result.append(MatchedScheme(
            scheme_name=full["scheme_name"],
            ministry=full["ministry"],
            eligibility_score=blended,
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
