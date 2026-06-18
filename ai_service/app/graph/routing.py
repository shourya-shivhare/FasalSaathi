"""
Dynamic routing — conditional edges + Send() for parallel agent dispatch.
NO executor node. LangGraph orchestrates via edges.

Key routing functions:
  - route_after_intent → greeting | data_retrieval | data_analysis | conversational | planner | context_retrieval
  - route_after_validation → dispatch agents or conversational
  - route_after_agent → next group, human_intervention, manual_review, or summary
  - route_after_intervention → re-route based on state
"""
from __future__ import annotations

import logging
from typing import Union

from langgraph.types import Send
from ai_service.app.graph.state import FasalSaathiState
from ai_service.app.graph.validator import GRAPH_SCORE_THRESHOLD

logger = logging.getLogger(__name__)

# ── Node name mapping ────────────────────────────────────────────────────────
NODE_MAP: dict[str, str] = {
    "pest": "pest_detection",
    "crop": "crop_recommendation",
    "market": "market_intelligence",
    "scheme": "scheme_recommendation",
}

REVERSE_NODE_MAP: dict[str, str] = {v: k for k, v in NODE_MAP.items()}

# Confidence thresholds per agent for intervention triggers
CONFIDENCE_THRESHOLDS: dict[str, float] = {
    "pest": 0.5,
    "crop": 0.5,
    "market": 0.6,
    "scheme": 0.5,
}

MAX_INTERVENTION_ATTEMPTS = 2


# ── After intent router ─────────────────────────────────────────────────────

def route_after_intent(state: FasalSaathiState) -> str:
    """Route based on classified intent."""
    intent = state.get("intent", "conversational")
    route_map = {
        "greeting": "greeting",
        "data_retrieval": "data_retrieval",
        "data_analysis": "data_analysis",
        "workflow": "planner",
        "follow_up": "context_retrieval",
        "conversational": "conversational",
    }
    result = route_map.get(intent, "conversational")
    logger.info("🔀 Intent route: %s → %s", intent, result)
    return result


# ── After validator ──────────────────────────────────────────────────────────

def route_after_validation(state: FasalSaathiState) -> Union[str, list[Send]]:
    """
    After validation, dispatch to agents or conversational.
    Returns a single node name or a list of Send() for parallel dispatch.
    """
    vr = state.get("validation_result")
    if not vr or vr.get("graph_score", 0) < GRAPH_SCORE_THRESHOLD:
        logger.info("🔀 Validation score too low → conversational")
        return "conversational"

    # If waiting for image, go to image upload interrupt
    if vr.get("pending_action") == "waiting_for_image":
        logger.info("🔀 Validation: waiting_for_image → image_upload")
        return "image_upload"

    groups = vr.get("execution_graph", {}).get("groups", [])
    if not groups:
        return "conversational"

    # Dispatch first group
    first = groups[0]
    if len(first) == 1:
        node = NODE_MAP.get(first[0], "conversational")
        logger.info("🔀 Dispatching single agent: %s", node)
        return node
    else:
        sends = [Send(NODE_MAP[a], state) for a in first if a in NODE_MAP]
        logger.info("🔀 Dispatching parallel: %s", [NODE_MAP[a] for a in first])
        return sends


# ── After each agent node ───────────────────────────────────────────────────

def route_after_agent(state: FasalSaathiState) -> Union[str, list[Send]]:
    """
    After an agent completes:
    1. Check confidence → maybe trigger intervention (loop-protected)
    2. Dispatch next group if remaining
    3. Otherwise → summary
    """
    conf = state.get("confidence_scores", {})
    attempts = state.get("intervention_attempts", {})
    last = _last_completed_agent(state)

    # ── Confidence gating ────────────────────────────────────────────────
    if last:
        threshold = CONFIDENCE_THRESHOLDS.get(last, 0.5)
        agent_conf = conf.get(last, 1.0)

        if agent_conf < threshold:
            current_attempts = attempts.get(last, 0)
            if current_attempts >= MAX_INTERVENTION_ATTEMPTS:
                logger.info("🔀 %s: conf=%.2f, attempts=%d ≥ max → manual_review",
                            last, agent_conf, current_attempts)
                return "manual_review"
            else:
                logger.info("🔀 %s: conf=%.2f < %.2f, attempt %d → human_intervention",
                            last, agent_conf, threshold, current_attempts + 1)
                return "human_intervention"

    # ── Next group dispatch ──────────────────────────────────────────────
    vr = state.get("validation_result", {})
    groups = vr.get("execution_graph", {}).get("groups", [])
    completed = _completed_agents(state)

    for group in groups:
        remaining = [a for a in group if a not in completed]
        if remaining:
            if len(remaining) == 1:
                node = NODE_MAP.get(remaining[0], "summary")
                logger.info("🔀 Next agent: %s", node)
                return node
            else:
                sends = [Send(NODE_MAP[a], state) for a in remaining if a in NODE_MAP]
                logger.info("🔀 Next parallel: %s", remaining)
                return sends

    logger.info("🔀 All agents complete → summary")
    return "summary"


# ── After human intervention ────────────────────────────────────────────────

def route_after_intervention(state: FasalSaathiState) -> str:
    """After human intervention, re-route to appropriate node."""
    pending = state.get("pending_action")
    if pending == "waiting_for_image":
        return "image_upload"

    # Determine which agent needs re-entry
    return _determine_reentry(state)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _completed_agents(state: FasalSaathiState) -> set[str]:
    """Determine which agents have completed (success or failed)."""
    completed = set()
    trace = state.get("execution_trace", [])

    for entry in trace:
        node = entry.get("node", "")
        status = entry.get("status", "")
        if status in ("success", "failed"):
            agent_id = REVERSE_NODE_MAP.get(node)
            if agent_id:
                completed.add(agent_id)

    return completed


def _last_completed_agent(state: FasalSaathiState) -> str | None:
    """Get the most recently completed agent ID."""
    trace = state.get("execution_trace", [])
    for entry in reversed(trace):
        node = entry.get("node", "")
        status = entry.get("status", "")
        if status in ("success", "failed"):
            agent_id = REVERSE_NODE_MAP.get(node)
            if agent_id:
                return agent_id
    return None


def _determine_reentry(state: FasalSaathiState) -> str:
    """Determine which node to re-enter after intervention."""
    # Look at what was last attempted
    trace = state.get("execution_trace", [])
    for entry in reversed(trace):
        node = entry.get("node", "")
        if node in REVERSE_NODE_MAP:
            return node  # Re-enter the same agent node

    # Fallback: continue to next group or summary
    return "summary"
