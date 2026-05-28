"""
Per-node timeout wrapper for LangGraph nodes.
Prevents external services from hanging the pipeline indefinitely.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Coroutine

logger = logging.getLogger(__name__)


# ── Per-node timeout configuration (seconds) ─────────────────────────────────
GRAPH_NODE_TIMEOUTS: dict[str, int] = {
    "intent_router": 10,
    "planner": 15,
    "validator": 5,
    "conversational": 15,
    "context_retrieval": 5,
    "crop_recommendation": 20,
    "market_intelligence": 15,
    "scheme_recommendation": 10,
    "pest_detection": 30,
    "summary": 15,
    "image_upload": 5,
    "human_intervention": 5,
    "manual_review": 5,
    "memory_retrieve": 5,
    "memory_persist": 5,
    "observability": 5,
    "greeting": 2,
}


async def run_with_timeout(coro: Coroutine, node_name: str) -> Any:
    """
    Execute a coroutine with a per-node timeout.

    On timeout:
      - Logs error
      - Raises asyncio.TimeoutError (caught by node's error handler)
    """
    timeout = GRAPH_NODE_TIMEOUTS.get(node_name, 30)
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.error("⏱️ Node '%s' timed out after %ds", node_name, timeout)
        raise
