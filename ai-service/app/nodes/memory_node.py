"""
Memory nodes — retrieve and persist farmer context from SQLite.
Entry point (first node) and near-exit (post-summary) nodes.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from app.core.retry import retry_async, MEMORY_RETRY
from app.graph.state import FasalSaathiState
from langchain_core.runnables import RunnableConfig

logger = logging.getLogger(__name__)


async def memory_retrieve_node(state: FasalSaathiState, config: RunnableConfig) -> dict:
    """Retrieve farmer's historical context from SQLite memory store."""
    start = time.time()
    runtime = config["configurable"]["runtime"]
    tools = runtime.tool_registry
    user_id = state.get("farmer_profile", {}).get("user_id", "anonymous")

    try:
        context = await retry_async(
            tools.memory_store.retrieve,
            MEMORY_RETRY,
            user_id,
            operation_name="memory_retrieve",
        )
    except Exception as e:
        logger.error("Memory retrieve failed: %s", e)
        context = {}

    return {
        "memory_context": context,
        "graph_path": ["memory_retrieve"],
        "timestamps": {"memory_retrieved": _now_iso()},
        "execution_trace": [{
            "node": "memory_retrieve", "status": "success",
            "duration_ms": round((time.time() - start) * 1000, 2),
            "reasoning": f"Retrieved {sum(len(v) for v in context.values() if isinstance(v, list))} memory entries",
            "confidence": 1.0, "timestamp": _now_iso(),
        }],
    }


async def memory_persist_node(state: FasalSaathiState, config: RunnableConfig) -> dict:
    """Persist current session results to SQLite memory store."""
    start = time.time()
    runtime = config["configurable"]["runtime"]
    tools = runtime.tool_registry
    user_id = state.get("farmer_profile", {}).get("user_id", "anonymous")

    session_data = {
        "user_query": state.get("user_query"),
        "crop_recommendations": state.get("crop_recommendations"),
        "pest_detection_result": state.get("pest_detection_result"),
        "scheme_recommendations": state.get("scheme_recommendations"),
        "market_analysis": state.get("market_analysis"),
        "final_summary": state.get("final_summary"),
    }

    try:
        await retry_async(
            tools.memory_store.persist,
            MEMORY_RETRY,
            user_id, session_data,
            operation_name="memory_persist",
        )
        status = "success"
    except Exception as e:
        logger.error("Memory persist failed: %s", e)
        status = "failed"

    return {
        "graph_path": ["memory_persist"],
        "timestamps": {"memory_persisted": _now_iso()},
        "execution_trace": [{
            "node": "memory_persist", "status": status,
            "duration_ms": round((time.time() - start) * 1000, 2),
            "reasoning": "Persisted session data to memory",
            "confidence": 1.0, "timestamp": _now_iso(),
        }],
    }


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
