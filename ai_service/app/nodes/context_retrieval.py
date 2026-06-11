"""
Context Retrieval Node — loads prior workflow context for follow-up queries.
Route: follow_up → context_retrieval → conversational

Ensures conversational node has access to prior recommendations,
reasoning steps, and memory when answering "why did you suggest soybean?"
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from ai_service.app.core.retry import retry_async, MEMORY_RETRY
from ai_service.app.graph.state import FasalSaathiState
from langchain_core.runnables import RunnableConfig

logger = logging.getLogger(__name__)


async def context_retrieval_node(state: FasalSaathiState, config: RunnableConfig) -> dict:
    """
    Load prior workflow context for follow-up queries.
    Merges current-session state + historical memory from SQLite.
    """
    start = time.time()
    runtime = config["configurable"]["runtime"]
    tools = runtime.tool_registry
    user_id = state.get("farmer_profile", {}).get("user_id", "anonymous")

    # Load historical memory from SQLite
    try:
        memory = await retry_async(
            tools.memory_store.retrieve,
            MEMORY_RETRY,
            user_id,
            operation_name="context_retrieval",
        )
    except Exception as e:
        logger.error("Context retrieval memory failed: %s", e)
        memory = {}

    # Merge with current-session results (from prior graph runs in same thread)
    session_context: dict = {}
    for key in (
        "crop_recommendations", "market_analysis",
        "scheme_recommendations", "pest_detection_result",
        "final_summary",
    ):
        if state.get(key):
            session_context[f"last_{key}"] = state[key]

    # Include reasoning from prior agents
    session_context["prior_reasoning"] = state.get("reasoning_steps", [])

    merged = {**memory, **session_context}

    logger.info(
        "📋 Context retrieval: %d memory categories + %d session keys",
        len(memory), len(session_context),
    )

    return {
        "memory_context": merged,
        "graph_path": ["context_retrieval"],
        "timestamps": {"context_retrieved": _now_iso()},
        "execution_trace": [{
            "node": "context_retrieval", "status": "success",
            "duration_ms": round((time.time() - start) * 1000, 2),
            "reasoning": f"Loaded {len(merged)} context keys for follow-up",
            "confidence": 1.0, "timestamp": _now_iso(),
        }],
    }


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
