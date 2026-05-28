"""
Market Intelligence Node — wraps existing market_intelligence_agent.
INDEPENDENT of crop output — reads commodity/location from farmer profile.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from app.agents.market_intelligence_agent import run_market_intelligence_agent
from app.schemas.agent_schemas import MarketIntelligenceRequest
from app.graph.state import FasalSaathiState
from langchain_core.runnables import RunnableConfig

logger = logging.getLogger(__name__)


async def market_intelligence_node(state: FasalSaathiState, config: RunnableConfig) -> dict:
    """
    Run market intelligence agent.
    INDEPENDENT: reads commodity/location from farmer_profile, NOT from crop output.
    """
    start = time.time()
    profile = state.get("farmer_profile", {})

    # Market is INDEPENDENT — get commodity from farmer profile crop_types
    crop_types = profile.get("crop_types", [])
    commodity = crop_types[0] if crop_types else "Wheat"

    # Also check if user_query mentions a specific commodity
    query = state.get("user_query", "").lower()
    common_crops = [
        "wheat", "rice", "maize", "soybean", "cotton", "mustard",
        "gram", "chana", "onion", "potato", "tomato", "sugarcane",
    ]
    for crop in common_crops:
        if crop in query:
            commodity = crop.title()
            break

    try:
        request = MarketIntelligenceRequest(
            commodity=commodity,
            state=profile.get("state", "Madhya Pradesh"),
            district=profile.get("district"),
            market=None,
        )

        response = await run_market_intelligence_agent(request)
        result = response.model_dump()
        conf = result.get("confidence_score", 0.5)

        logger.info(
            "🏪 Market node: %s @ %s, trend=%s, conf=%.2f",
            commodity, profile.get("state", "?"),
            result.get("current_market_analysis", {}).get("price_trend", "?"),
            conf,
        )

        return {
            "market_analysis": result,
            "confidence_scores": {"market": conf},
            "reasoning_steps": [{
                "agent": "market_intelligence",
                "reasoning": (
                    f"Analyzed {commodity} prices. "
                    f"Trend: {result.get('current_market_analysis', {}).get('price_trend', 'stable')}. "
                    f"Recommendation: {result.get('selling_recommendation', 'N/A')}"
                ),
                "confidence": conf,
            }],
            "graph_path": ["market_intelligence"],
            "timestamps": {"market_completed": _now_iso()},
            "execution_trace": [{
                "node": "market_intelligence", "status": "success",
                "duration_ms": round((time.time() - start) * 1000, 2),
                "tools_used": ["agmarknet_client", "weather_client", "trend_analysis", "forecasting"],
                "reasoning": f"{commodity} market analysis complete",
                "confidence": conf, "timestamp": _now_iso(),
            }],
        }

    except Exception as e:
        logger.error("Market intelligence failed: %s", e)
        return {
            "graph_path": ["market_intelligence"],
            "errors": [{"node": "market_intelligence", "error": str(e)}],
            "confidence_scores": {"market": 0.0},
            "execution_trace": [{
                "node": "market_intelligence", "status": "failed",
                "duration_ms": round((time.time() - start) * 1000, 2),
                "reasoning": f"Error: {e}", "confidence": 0.0,
                "timestamp": _now_iso(),
            }],
        }


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
