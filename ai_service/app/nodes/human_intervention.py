"""
Human Intervention Node — loop-protected clarification requests.

Bug Fix (was: Command(resume=...)):
  The previous version returned Command(resume={...}), which is the API a
  *caller* uses to RESUME a paused graph — not how a node triggers an interrupt.
  It silently never paused; the graph continued immediately to
  route_after_intervention which re-entered the same agent, creating an
  uncontrolled loop regardless of MAX_ATTEMPTS.

New design (state-machine / non-interrupt):
  1. Increment intervention_attempts for the failing agent.
  2. Set final_response to the clarification message.
  3. Return normally → graph flows to memory_persist → observability → END.
  4. Next invocation: the farmer provides more details; the new query is
     processed with fresh context and the agent re-runs.
  5. If count already >= MAX_ATTEMPTS (from prior turns), route_after_agent
     sends to manual_review directly (this node is not reached again).

This matches the state-machine approach used by image_upload_node and is
robust across independent API calls, which is how the chat router works.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from ai_service.app.graph.state import FasalSaathiState
from langchain_core.runnables import RunnableConfig

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 2


def _determine_intervention(state: FasalSaathiState) -> dict:
    """Determine what kind of intervention is needed."""
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
                        "message": (
                            "Detection confidence is low. "
                            "Could you upload a closer, clearer image of the affected area?"
                        ),
                    }
                else:
                    return {
                        "type": "low_confidence",
                        "agent": _node_to_agent(node),
                        "message": (
                            f"I'm not very confident about the {_node_to_agent(node)} analysis. "
                            "Could you provide more details about your situation, "
                            "such as your location, soil type, or specific concerns?"
                        ),
                    }

    return {
        "type": "low_confidence",
        "agent": "unknown",
        "message": (
            "I need a bit more information to give you accurate advice. "
            "Could you describe your situation in more detail?"
        ),
    }


async def human_intervention_node(state: FasalSaathiState, config: RunnableConfig) -> dict:
    """
    Loop-protected clarification request.

    Increments intervention_attempts and returns the clarification message
    as final_response so the farmer sees it.  The graph then ends this turn
    (→ memory_persist → observability → END).

    On the next invocation route_after_agent checks attempts:
      - < MAX_ATTEMPTS  → this node fires again with the farmer's answer
      - >= MAX_ATTEMPTS → routes to manual_review (bypasses this node)
    """
    start = time.time()
    attempts = state.get("intervention_attempts", {})
    intervention = _determine_intervention(state)
    agent = intervention.get("agent", "unknown")
    count = attempts.get(agent, 0)

    new_count = count + 1

    logger.info(
        "⏸️  Intervention for %s (attempt %d/%d): %s",
        agent, new_count, MAX_ATTEMPTS, intervention["type"],
    )

    return {
        "final_response": intervention["message"],
        "intervention_attempts": {agent: new_count},
        "pending_action": None,
        "graph_path": ["human_intervention"],
        "execution_trace": [{
            "node": "human_intervention", "status": "success",
            "duration_ms": round((time.time() - start) * 1000, 2),
            "reasoning": (
                f"Clarification requested for {agent} "
                f"(attempt {new_count}/{MAX_ATTEMPTS}): {intervention['type']}"
            ),
            "confidence": 0.3, "timestamp": _now_iso(),
        }],
    }


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
