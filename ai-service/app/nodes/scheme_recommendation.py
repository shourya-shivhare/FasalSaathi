"""
Scheme Recommendation Node — wraps existing scheme_recommendation_agent.
Depends on crop output (crop → scheme dependency).
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from app.agents.scheme_recommendation_agent import run_scheme_recommendation_agent
from app.schemas.agent_schemas import SchemeRecommendationRequest
from app.graph.state import FasalSaathiState
from langchain_core.runnables import RunnableConfig

logger = logging.getLogger(__name__)


async def scheme_recommendation_node(state: FasalSaathiState, config: RunnableConfig) -> dict:
    """
    Run scheme recommendation agent.
    Reads crop recommendations from state (crop → scheme dependency).
    """
    start = time.time()
    profile = state.get("farmer_profile", {})

    # Build context from upstream agents
    context_from_agents: dict = {}

    crop_result = state.get("crop_recommendations")
    if crop_result:
        crops = crop_result.get("recommended_crops", [])
        crop_names = [c.get("crop_name", "") for c in crops[:5]]
        context_from_agents["crop_recommendations"] = ", ".join(crop_names)

    pest_result = state.get("pest_detection_result")
    if pest_result:
        detections = pest_result.get("detections", [])
        if detections:
            pest_names = [d.get("class", "") for d in detections[:3]]
            context_from_agents["pest_detection"] = ", ".join(pest_names)

    # Merge crop types from profile + recommendations
    crop_types = list(profile.get("crop_types", []))
    if crop_result:
        for c in crop_result.get("recommended_crops", [])[:3]:
            name = c.get("crop_name", "")
            if name and name not in crop_types:
                crop_types.append(name)

    try:
        request = SchemeRecommendationRequest(
            user_id=profile.get("user_id"),
            state=profile.get("state", ""),
            district=profile.get("district"),
            farmer_category=profile.get("farmer_category", "marginal"),
            crop_types=crop_types,
            annual_income=profile.get("annual_income"),
            gender=profile.get("gender"),
            age=profile.get("age"),
            language_preference=profile.get("language_preference", "en"),
            context_from_agents=context_from_agents,
        )

        response = await run_scheme_recommendation_agent(request)
        result = response.model_dump()

        schemes = result.get("matched_schemes", [])
        avg_conf = (
            sum(s.get("eligibility_score", 0.5) for s in schemes) / len(schemes)
            if schemes else 0.5
        )

        logger.info("🏛️ Scheme node: %d matches, avg_score=%.2f", len(schemes), avg_conf)

        return {
            "scheme_recommendations": result,
            "confidence_scores": {"scheme": avg_conf},
            "reasoning_steps": [{
                "agent": "scheme_recommendation",
                "reasoning": (
                    f"Matched {len(schemes)} schemes for "
                    f"{profile.get('farmer_category', 'marginal')} farmer in {profile.get('state', '?')}"
                ),
                "confidence": avg_conf,
            }],
            "graph_path": ["scheme_recommendation"],
            "timestamps": {"scheme_completed": _now_iso()},
            "execution_trace": [{
                "node": "scheme_recommendation", "status": "success",
                "duration_ms": round((time.time() - start) * 1000, 2),
                "tools_used": ["scheme_db", "gemini_llm"],
                "reasoning": f"{len(schemes)} schemes matched",
                "confidence": avg_conf, "timestamp": _now_iso(),
            }],
        }

    except Exception as e:
        logger.error("Scheme recommendation failed: %s", e)
        return {
            "graph_path": ["scheme_recommendation"],
            "errors": [{"node": "scheme_recommendation", "error": str(e)}],
            "confidence_scores": {"scheme": 0.0},
            "execution_trace": [{
                "node": "scheme_recommendation", "status": "failed",
                "duration_ms": round((time.time() - start) * 1000, 2),
                "reasoning": f"Error: {e}", "confidence": 0.0,
                "timestamp": _now_iso(),
            }],
        }


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
