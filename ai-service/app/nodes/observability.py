"""
Observability Node — emits execution trace and performance metrics.
Last node before END. Logs the full graph path for debugging.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from app.graph.state import FasalSaathiState
from langchain_core.runnables import RunnableConfig

logger = logging.getLogger(__name__)


async def observability_node(state: FasalSaathiState, config: RunnableConfig) -> dict:
    """
    Record final execution metrics and emit structured log.
    This is the last node before END in the graph.
    """
    start = time.time()
    graph_path = state.get("graph_path", [])
    errors = state.get("errors", [])
    conf = state.get("confidence_scores", {})
    trace = state.get("execution_trace", [])

    # Compute total pipeline duration
    timestamps = state.get("timestamps", {})
    total_duration_ms = sum(
        entry.get("duration_ms", 0) for entry in trace
    )

    # Build final metrics
    metrics = {
        "graph_path": " → ".join(graph_path),
        "total_nodes_executed": len(graph_path),
        "total_duration_ms": round(total_duration_ms, 2),
        "error_count": len(errors),
        "confidence_scores": conf,
        "min_confidence": min(conf.values()) if conf else None,
        "avg_confidence": (
            sum(conf.values()) / len(conf) if conf else None
        ),
    }

    # Structured log for monitoring
    logger.info(
        "📊 Observability: path=[%s], duration=%.0fms, errors=%d, avg_conf=%.2f",
        " → ".join(graph_path),
        total_duration_ms,
        len(errors),
        metrics["avg_confidence"] or 0,
    )

    if errors:
        for err in errors:
            logger.warning("   ⚠️ Error: %s", err)

    return {
        "tool_outputs": {"observability_metrics": metrics},
        "graph_path": ["observability"],
        "timestamps": {"pipeline_completed": _now_iso()},
        "execution_trace": [{
            "node": "observability", "status": "success",
            "duration_ms": round((time.time() - start) * 1000, 2),
            "reasoning": f"Pipeline complete: {len(graph_path)} nodes, {len(errors)} errors",
            "confidence": 1.0, "timestamp": _now_iso(),
        }],
    }


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
