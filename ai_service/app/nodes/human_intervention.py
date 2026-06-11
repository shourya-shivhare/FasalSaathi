"""
Human Intervention Node — loop-protected interrupts.
Uses Command (not bare interrupt) per Patch 3 for atomic state+interrupt.
Max 2 attempts per agent — exhausted → routes to manual_review.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from langgraph.types import Command
from ai_service.app.graph.state import FasalSaathiState
from langchain_core.runnables import RunnableConfig

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 2


def _determine_intervention(state: FasalSaathiState) -> dict:
    """Determine what kind of intervention is needed."""
    conf = state.get("confidence_scores", {})
    trace = state.get("execution_trace", [])

    # Find the last agent with low confidence
    for entry in reversed(trace):
        node = entry.get("node", "")
        status = entry.get("status", "")
        if status in ("success", "failed"):
            agent_conf = entry.get("confidence", 1.0)
            if agent_conf < 0.5:
                if node == "pest_detection":
                    return {
                        "type": "image_quality",
                        "agent": "pest",
                        "message": "Detection confidence is low. Could you upload a closer, clearer image?",
                    }
                else:
                    return {
                        "type": "low_confidence",
                        "agent": _node_to_agent(node),
                        "message": f"I'm not very confident about the {_node_to_agent(node)} analysis. Could you provide more details?",
                    }

    return {
        "type": "low_confidence",
        "agent": "unknown",
        "message": "Could you provide more details to improve the analysis?",
    }


async def human_intervention_node(state: FasalSaathiState, config: RunnableConfig) -> dict:
    """
    Loop-protected human intervention.
    Uses Command for atomic state+interrupt (Patch 3).
    After MAX_ATTEMPTS, returns without interrupt (routing sends to manual_review).
    """
    start = time.time()
    attempts = state.get("intervention_attempts", {})
    intervention = _determine_intervention(state)
    agent = intervention.get("agent", "unknown")
    count = attempts.get(agent, 0)

    # ── Exhausted: don't interrupt, just return ─────────────────────────
    if count >= MAX_ATTEMPTS:
        logger.info(
            "🚫 Intervention exhausted for %s (%d/%d) → manual_review",
            agent, count, MAX_ATTEMPTS,
        )
        return {
            "intervention_attempts": {agent: count},
            "graph_path": ["human_intervention"],
            "execution_trace": [{
                "node": "human_intervention", "status": "skipped",
                "duration_ms": round((time.time() - start) * 1000, 2),
                "reasoning": f"Max attempts ({MAX_ATTEMPTS}) reached for {agent}",
                "confidence": 0.3, "timestamp": _now_iso(),
            }],
        }

    # ── Interrupt with atomic state update (Patch 3) ────────────────────
    logger.info(
        "⏸️ Intervention for %s (attempt %d/%d): %s",
        agent, count + 1, MAX_ATTEMPTS, intervention["type"],
    )

    return Command(
        update={
            "intervention_attempts": {agent: count + 1},
            "pending_action": None,
            "graph_path": ["human_intervention"],
            "execution_trace": [{
                "node": "human_intervention", "status": "interrupted",
                "duration_ms": round((time.time() - start) * 1000, 2),
                "reasoning": f"Requesting {intervention['type']} for {agent} (attempt {count + 1}/{MAX_ATTEMPTS})",
                "confidence": 0.3, "timestamp": _now_iso(),
            }],
        },
        resume={
            "type": intervention["type"],
            "message": intervention["message"],
            "attempt": count + 1,
            "max_attempts": MAX_ATTEMPTS,
        },
    )


def _node_to_agent(node_name: str) -> str:
    """Convert node name to agent ID."""
    mapping = {
        "pest_detection": "pest",
        "crop_recommendation": "crop",
        "market_intelligence": "market",
        "scheme_recommendation": "scheme",
    }
    return mapping.get(node_name, "unknown")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
