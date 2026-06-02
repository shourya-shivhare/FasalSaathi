"""
Scored Validation Layer — validates planner output and builds execution groups.

Graph scoring formula (corrected weights):
  score = 0.45 * relevance + 0.30 * dependency + 0.10 * planner_confidence + 0.15 * tool_availability
  Threshold: 0.4 (below → route to conversational)

Dependency rules:
  - market = INDEPENDENT
  - crop → scheme
  - pest → crop (conditional: if both planned)
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from app.graph.state import FasalSaathiState, PlannerOutput
from langchain_core.runnables import RunnableConfig

logger = logging.getLogger(__name__)

# ── Dependency Rules ─────────────────────────────────────────────────────────
# agent: [must_run_before_it]
DEPENDENCY_RULES: dict[str, list[str]] = {
    "crop": [],         # no required upstream (pest is conditional)
    "market": [],       # INDEPENDENT
    "scheme": ["crop"], # requires crop results
    "pest": [],         # no required upstream
}

# Conditional deps: if both are planned, first must run before second
CONDITIONAL_DEPS: dict[tuple[str, str], bool] = {
    ("pest", "crop"): True,     # pest → crop (if both planned)
    ("pest", "scheme"): True,   # pest → scheme (if both planned, via crop)
}

GRAPH_SCORE_THRESHOLD = 0.4

# ── Tools required per agent ─────────────────────────────────────────────────
AGENT_TOOLS: dict[str, list[str]] = {
    "pest": ["yolo", "pest_map"],
    "crop": ["weather_client", "memory_tools"],
    "market": ["market_client", "weather_client", "trend_analyzer", "forecaster"],
    "scheme": ["scheme_db"],
}


def _count_dependency_violations(plan: PlannerOutput) -> int:
    """Count how many dependency rules are violated in the plan."""
    agents = set(plan.get("agents", []))
    violations = 0

    for agent in agents:
        required = DEPENDENCY_RULES.get(agent, [])
        for dep in required:
            if dep not in agents:
                violations += 1

    # Check conditional deps
    for (first, second), required in CONDITIONAL_DEPS.items():
        if first in agents and second in agents:
            # Both planned — check if ordering hints respect this
            hints = plan.get("execution_hints", {})
            priority = hints.get("priority", {})
            if priority.get(first, 0) > priority.get(second, 0):
                violations += 1

    return violations


def _tools_available(agent: str) -> bool:
    """Check if tools for an agent are importable (basic availability check)."""
    # Phase 1: assume all tools available. In production, ping health endpoints.
    return True


def compute_graph_score(
    plan: PlannerOutput,
    state: FasalSaathiState,
) -> float:
    """
    Compute graph validation score.

    Weights:
      relevance          = 0.45  (primary: do planned agents match sub_intents?)
      dependency          = 0.30  (are dependencies satisfiable?)
      planner_confidence  = 0.10  (LOW weight: LLMs overestimate confidence)
      tool_availability   = 0.15  (are required APIs available?)

    Threshold: 0.4
    """
    planned = set(plan.get("agents", []))
    requested = set(state.get("sub_intents", []))

    if not planned:
        return 0.0

    # Relevance (0.45)
    if planned:
        relevance = len(planned & requested) / max(len(planned), 1)
    else:
        relevance = 0.0

    # Dependency (0.30)
    violations = _count_dependency_violations(plan)
    dependency = max(0.0, 1.0 - (violations * 0.25))

    # Planner confidence (0.10) — deliberately low weight
    confidence = plan.get("confidence", 0.5)

    # Tool availability (0.15)
    available = sum(1 for a in planned if _tools_available(a))
    tool_score = available / max(len(planned), 1) if planned else 0.0

    score = (
        0.45 * relevance
        + 0.30 * dependency
        + 0.10 * confidence
        + 0.15 * tool_score
    )
    return round(max(0.0, min(1.0, score)), 2)


def _build_execution_groups(agents: list[str]) -> list[list[str]]:
    """
    Build ordered execution groups respecting dependencies.
    Agents in the same group run in parallel via Send().

    Corrected: market is INDEPENDENT, crop and market are parallel.
    """
    groups: list[list[str]] = []

    # Phase 1: pest (if present — must run before crop)
    phase1 = [a for a in agents if a == "pest"]
    # Phase 2: crop + market in parallel (market is independent)
    phase2 = [a for a in agents if a in ("crop", "market")]
    # Phase 3: scheme (depends on crop)
    phase3 = [a for a in agents if a == "scheme"]

    if phase1:
        groups.append(phase1)
    if phase2:
        groups.append(phase2)
    if phase3:
        groups.append(phase3)

    return groups


async def validator_node(state: FasalSaathiState, config: RunnableConfig) -> dict:
    """
    Validate planner output, compute graph score, and build execution groups.
    If score < 0.4, route to conversational.
    """
    start = time.time()
    plan = state.get("planner_output")

    if not plan:
        return {
            "validation_result": {
                "validated_agents": [],
                "execution_graph": {"groups": []},
                "graph_score": 0.0,
                "warnings": ["No planner output to validate"],
                "pending_action": None,
                "reasoning": "Missing planner output.",
            },
            "graph_path": ["validator"],
            "execution_trace": [{
                "node": "validator", "status": "failed",
                "duration_ms": round((time.time() - start) * 1000, 2),
                "reasoning": "No planner output", "confidence": 0.0,
                "timestamp": _now_iso(),
            }],
        }

    agents = plan.get("agents", [])
    score = compute_graph_score(plan, state)
    warnings: list[str] = []

    # Check for missing dependencies
    for agent in agents:
        for dep in DEPENDENCY_RULES.get(agent, []):
            if dep not in agents:
                warnings.append(f"'{agent}' requires '{dep}' but it's not planned")

    # Determine pending action
    pending_action = None
    if plan.get("requires_image") and not state.get("uploaded_image_id"):
        pending_action = "waiting_for_image"

    # Build execution groups
    groups = _build_execution_groups(agents)

    validation = {
        "validated_agents": agents,
        "execution_graph": {"groups": groups},
        "graph_score": score,
        "warnings": warnings,
        "pending_action": pending_action,
        "reasoning": (
            f"Score: {score} (threshold: {GRAPH_SCORE_THRESHOLD}). "
            f"{len(agents)} agents in {len(groups)} execution groups. "
            f"{len(warnings)} warnings."
        ),
    }

    logger.info(
        "✅ Validator: score=%.2f, agents=%s, groups=%s, pending=%s",
        score, agents, groups, pending_action,
    )

    return {
        "validation_result": validation,
        "graph_path": ["validator"],
        "timestamps": {"validation_completed": _now_iso()},
        "execution_trace": [{
            "node": "validator", "status": "success",
            "duration_ms": round((time.time() - start) * 1000, 2),
            "reasoning": validation["reasoning"],
            "confidence": score,
            "timestamp": _now_iso(),
        }],
    }


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
