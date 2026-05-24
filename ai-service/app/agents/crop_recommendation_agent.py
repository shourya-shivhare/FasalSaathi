"""
Crop Recommendation Agent
─────────────────────────
Accepts location, soil, season, water, and pest context.
Uses Gemini LLM to reason over the best 3–5 crops for the farmer.

Independently callable via its own router OR via the orchestrator pipeline.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict

from app.core.llm import get_llm, safe_llm_invoke_async
from app.schemas.agent_schemas import (
    CropRecommendationRequest,
    CropRecommendationResponse,
    RecommendedCrop,
)

logger = logging.getLogger(__name__)

# ── Prompt ────────────────────────────────────────────────────────────────────

CROP_RECOMMENDATION_PROMPT = """\
You are an expert Indian agronomist. Based on the farmer's profile below, \
recommend the top 3-5 best crops to grow this season.

FARMER PROFILE:
- State: {state}
- District: {district}
- Soil type: {soil_type}
- Season: {season}
- Water availability: {water_availability}
- Land size: {land_size_acres} acres
- Past crops grown: {past_crops}
- Pest/disease context: {pest_context}

{extra_context}

Return your response as a JSON array with exactly this structure:
[
  {{
    "crop_name": "Wheat",
    "confidence": 0.92,
    "season": "Rabi",
    "reasoning": "Why this crop is ideal for the farmer",
    "estimated_yield_per_acre": "18-22 quintals",
    "water_requirement": "moderate"
  }}
]

Rules:
- Recommend 3-5 crops max
- Consider crop rotation from past_crops
- If pest_context mentions a specific pest, avoid crops highly susceptible to it
- confidence must be 0.0-1.0
- Keep reasoning under 2 sentences
- Return ONLY the JSON array, no other text
"""


async def run_crop_recommendation_agent(
    request: CropRecommendationRequest,
) -> CropRecommendationResponse:
    """
    Execute the crop recommendation agent.

    Args:
        request: Farmer's profile and land details.

    Returns:
        CropRecommendationResponse with ranked crop suggestions.
    """
    logger.info(
        "🌱 Crop Recommendation Agent invoked — state=%s, season=%s, soil=%s",
        request.state, request.season, request.soil_type,
    )

    # Build extra context from upstream agents (orchestrator injects this)
    extra_lines = []
    if request.context_from_agents:
        if "pest_detection" in request.context_from_agents:
            extra_lines.append(
                f"Pest detection results: {request.context_from_agents['pest_detection']}"
            )
    extra_context = "\n".join(extra_lines) if extra_lines else "No additional agent context."

    prompt_text = CROP_RECOMMENDATION_PROMPT.format(
        state=request.state,
        district=request.district or "N/A",
        soil_type=request.soil_type,
        season=request.season,
        water_availability=request.water_availability,
        land_size_acres=request.land_size_acres or "Unknown",
        past_crops=", ".join(request.past_crops) if request.past_crops else "None",
        pest_context=request.pest_context or "None reported",
        extra_context=extra_context,
    )

    llm = get_llm(temperature=0.3)
    raw = await safe_llm_invoke_async(
        llm,
        prompt_text,
        fallback=_fallback_crops(request.season),
    )

    # Parse LLM JSON response
    crops = _parse_crop_response(raw, request.season)

    pest_note = None
    if request.pest_context:
        pest_note = f"Crops were filtered considering: {request.pest_context}"

    logger.info("🌱 Crop Agent returning %d recommendations", len(crops))

    return CropRecommendationResponse(
        recommended_crops=crops,
        reasoning_summary=f"Top {len(crops)} crops for {request.season} season in {request.state} ({request.soil_type} soil, {request.water_availability} water).",
        pest_considerations=pest_note,
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_crop_response(raw: str, season: str) -> list[RecommendedCrop]:
    """Try to parse LLM JSON; fall back to defaults on failure."""
    try:
        # Strip markdown fences if present
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
        data = json.loads(text)
        return [
            RecommendedCrop(
                crop_name=c.get("crop_name", "Unknown"),
                confidence=min(max(float(c.get("confidence", 0.5)), 0.0), 1.0),
                season=c.get("season", season),
                reasoning=c.get("reasoning", "Suitable for your region and conditions."),
                estimated_yield_per_acre=c.get("estimated_yield_per_acre"),
                water_requirement=c.get("water_requirement"),
            )
            for c in data[:5]
        ]
    except Exception as e:
        logger.warning("Failed to parse crop LLM response: %s", e)
        return _default_crops(season)


def _default_crops(season: str) -> list[RecommendedCrop]:
    """Hardcoded fallback crops per season."""
    defaults = {
        "Kharif": [
            RecommendedCrop(crop_name="Rice", confidence=0.85, season="Kharif", reasoning="Staple Kharif crop suited to monsoon conditions."),
            RecommendedCrop(crop_name="Maize", confidence=0.80, season="Kharif", reasoning="Good yield potential with moderate water."),
            RecommendedCrop(crop_name="Soybean", confidence=0.75, season="Kharif", reasoning="Excellent nitrogen fixer, good rotation crop."),
        ],
        "Rabi": [
            RecommendedCrop(crop_name="Wheat", confidence=0.88, season="Rabi", reasoning="Primary Rabi crop across North India."),
            RecommendedCrop(crop_name="Mustard", confidence=0.82, season="Rabi", reasoning="Low water requirement, good oil crop."),
            RecommendedCrop(crop_name="Gram (Chana)", confidence=0.78, season="Rabi", reasoning="Pulse crop with strong MSP support."),
        ],
        "Zaid": [
            RecommendedCrop(crop_name="Moong", confidence=0.82, season="Zaid", reasoning="Short-duration pulse ideal for summer."),
            RecommendedCrop(crop_name="Watermelon", confidence=0.78, season="Zaid", reasoning="High market demand in summer months."),
            RecommendedCrop(crop_name="Cucumber", confidence=0.75, season="Zaid", reasoning="Quick returns with moderate input cost."),
        ],
    }
    return defaults.get(season, defaults["Kharif"])


def _fallback_crops(season: str) -> str:
    """Return a JSON string fallback for safe_llm_invoke."""
    crops = _default_crops(season)
    return json.dumps([
        {"crop_name": c.crop_name, "confidence": c.confidence, "season": c.season,
         "reasoning": c.reasoning, "estimated_yield_per_acre": c.estimated_yield_per_acre,
         "water_requirement": c.water_requirement}
        for c in crops
    ])
