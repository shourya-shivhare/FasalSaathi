"""
Hybrid Planner — decides which agents to invoke and in what order.
Uses LLM to select agents based on the query and farmer profile.

Dependency rules (FINAL):
  - pest → crop (if both planned)
  - crop → scheme (if both planned)
  - market = INDEPENDENT (uses commodity/location from farmer profile directly)
"""
from __future__ import annotations

import json
import re
import logging
import time
from datetime import datetime, timezone

from app.core.llm import get_llm, safe_llm_invoke_async
from app.graph.state import FasalSaathiState
from langchain_core.runnables import RunnableConfig

logger = logging.getLogger(__name__)

# ── Planner Prompt ───────────────────────────────────────────────────────────
PLANNER_PROMPT = """\
You are FasalSaathi's agent planner. Decide which specialist agents to invoke \
for the farmer's query.

AVAILABLE AGENTS:
- "pest": Pest/disease identification (requires image upload)
- "crop": Crop recommendations based on location, soil, season, water
- "market": Market prices, mandi rates, price trends, selling advice
- "scheme": Government schemes, subsidies, loans, insurance

DEPENDENCY RULES:
- pest → crop: Crop agent uses pest results to avoid susceptible varieties
- crop → scheme: Scheme matching depends on recommended crops
- market: INDEPENDENT — uses commodity/location/season from farmer profile directly.
  Market does NOT require crop recommendation output.

SAFE PARALLEL GROUPS:
- [crop, market] — always safe when both are planned (market is independent)
- [pest] — always runs before crop (if both planned)
- [scheme] — always runs after crop (if both planned)

FARMER PROFILE:
{farmer_profile}

MEMORY CONTEXT (previous interactions):
{memory_context}

USER QUERY: {query}
SUB INTENTS: {sub_intents}

Return ONLY valid JSON:
{{
  "agents": ["crop", "market"],
  "execution_hints": {{
    "parallel": [["crop", "market"]],
    "priority": {{"crop": 1, "market": 1}}
  }},
  "requires_image": false,
  "reasoning": "Farmer needs crop advice and market prices. Market is independent.",
  "confidence": 0.88
}}

Rules:
- Only include agents that are needed
- requires_image = true only if pest identification is needed
- confidence 0.0-1.0 reflecting how sure you are about the plan
- Return ONLY the JSON, no other text
"""


def _parse_planner_response(raw: str) -> dict:
    """Parse LLM JSON response for planner output."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        text = text.rsplit("```", 1)[0]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return {
        "agents": ["crop"],
        "execution_hints": {"parallel": [], "priority": {"crop": 1}},
        "requires_image": False,
        "reasoning": "Fallback: defaulting to crop recommendation.",
        "confidence": 0.4,
    }


async def planner_node(state: FasalSaathiState, config: RunnableConfig) -> dict:
    """
    Hybrid planner — LLM selects agents, hardcoded rules enforce dependencies.
    Low confidence (< 0.6) triggers a clarification interrupt.
    """
    start = time.time()
    query = state.get("user_query", "")
    sub_intents = state.get("sub_intents", [])
    farmer_profile = state.get("farmer_profile", {})
    memory_context = state.get("memory_context", {})

    try:
        prompt = PLANNER_PROMPT.format(
            query=query,
            sub_intents=json.dumps(sub_intents),
            farmer_profile=json.dumps(farmer_profile, default=str),
            memory_context=json.dumps(
                {k: v[:2] if isinstance(v, list) else v
                 for k, v in memory_context.items()},
                default=str,
            ),
        )

        llm = get_llm(temperature=0.1)
        raw = await safe_llm_invoke_async(llm, prompt, fallback="__PLANNER_FALLBACK__")

        if raw == "__PLANNER_FALLBACK__":
            plan = _fallback_plan(sub_intents)
        else:
            plan = _parse_planner_response(raw)

        # Validate agents list
        valid_agents = {"pest", "crop", "market", "scheme"}
        plan["agents"] = [a for a in plan.get("agents", []) if a in valid_agents]
        if not plan["agents"]:
            plan["agents"] = ["crop"]
            plan["confidence"] = 0.4

        # Low confidence → interrupt for clarification
        if plan.get("confidence", 0.5) < 0.6:
            from langgraph.types import Command
            return Command(
                update={
                    "planner_output": plan,
                    "graph_path": ["planner"],
                    "timestamps": {"planner_completed": _now_iso()},
                    "execution_trace": [{
                        "node": "planner", "status": "interrupted",
                        "duration_ms": round((time.time() - start) * 1000, 2),
                        "reasoning": f"Low confidence ({plan['confidence']}), requesting clarification",
                        "confidence": plan["confidence"],
                        "timestamp": _now_iso(),
                    }],
                },
                goto="planner",  # Return to planner after user responds
                resume={
                    "type": "clarification",
                    "message": (
                        "I want to make sure I understand correctly. "
                        "Could you provide more details about what you need help with?"
                    ),
                },
            )

        return {
            "planner_output": plan,
            "graph_path": ["planner"],
            "timestamps": {"planner_completed": _now_iso()},
            "execution_trace": [{
                "node": "planner", "status": "success",
                "duration_ms": round((time.time() - start) * 1000, 2),
                "reasoning": plan.get("reasoning", ""),
                "confidence": plan.get("confidence", 0.7),
                "timestamp": _now_iso(),
            }],
        }

    except Exception as e:
        logger.error("Planner error: %s", e)
        plan = _fallback_plan(sub_intents)
        return {
            "planner_output": plan,
            "graph_path": ["planner"],
            "errors": [{"node": "planner", "error": str(e)}],
            "execution_trace": [{
                "node": "planner", "status": "failed",
                "duration_ms": round((time.time() - start) * 1000, 2),
                "reasoning": f"Error: {e}. Using fallback plan.",
                "confidence": 0.4, "timestamp": _now_iso(),
            }],
        }


def _fallback_plan(sub_intents: list[str]) -> dict:
    """Build a safe fallback plan from sub_intents."""
    agents = sub_intents if sub_intents else ["crop"]
    valid = {"pest", "crop", "market", "scheme"}
    agents = [a for a in agents if a in valid] or ["crop"]
    return {
        "agents": agents,
        "execution_hints": {"parallel": [], "priority": {a: i + 1 for i, a in enumerate(agents)}},
        "requires_image": "pest" in agents,
        "reasoning": "Fallback plan from sub_intents.",
        "confidence": 0.5,
    }


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
