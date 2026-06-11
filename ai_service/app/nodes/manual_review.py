"""
Manual Review Node — activated when intervention attempts are exhausted (≥ 2).
Adds disclaimer and routes to summary with available data.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from ai_service.app.graph.state import FasalSaathiState
from langchain_core.runnables import RunnableConfig

logger = logging.getLogger(__name__)


async def manual_review_node(state: FasalSaathiState, config: RunnableConfig) -> dict:
    """
    Activated when intervention attempts are exhausted.
    Adds a disclaimer and proceeds to summary with available data.
    """
    start = time.time()
    attempts = state.get("intervention_attempts", {})

    exhausted = [
        agent for agent, count in attempts.items() if count >= 2
    ]

    disclaimer = (
        f"⚠️ Note: Results for {', '.join(exhausted)} could not be fully verified "
        f"after multiple attempts. The advisory below uses the best available data. "
        f"Please consult a local agricultural expert for confirmation."
    )

    logger.info("📋 Manual review: exhausted agents = %s", exhausted)

    return {
        "reasoning_steps": [{
            "agent": "manual_review",
            "reasoning": (
                f"Intervention exhausted for: {', '.join(exhausted)}. "
                f"Proceeding with available data and disclaimer."
            ),
            "confidence": 0.3,
        }],
        "graph_path": ["manual_review"],
        "errors": [{"node": "manual_review", "warning": disclaimer}],
        "execution_trace": [{
            "node": "manual_review", "status": "success",
            "duration_ms": round((time.time() - start) * 1000, 2),
            "reasoning": f"Added disclaimer for {', '.join(exhausted)}",
            "confidence": 0.3, "timestamp": _now_iso(),
        }],
    }


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
