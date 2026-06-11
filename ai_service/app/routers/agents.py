"""
Agent-specific REST endpoints — backward-compatible with the backend proxy.

Each endpoint translates the legacy per-agent request into a LangGraph
pipeline invocation, so the frontend/backend proxy continues working while
all logic flows through the unified graph.

Endpoints:
  POST /crop-recommendation   → graph with sub_intents=["crop"]
  POST /scheme-recommendation → graph with sub_intents=["scheme"]
  POST /full-analysis         → graph with sub_intents derived from payload
"""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ai_service.app.core.runtime_context import GraphRuntimeContext
from ai_service.app.core.tool_registry import create_production_registry
from ai_service.app.graph.orchestrator import get_orchestrator
from ai_service.app.graph.state_migration import CURRENT_SCHEMA_VERSION

router = APIRouter()
logger = logging.getLogger(__name__)

# Re-use the same registry singleton as chat router
_registry = None


def _get_registry():
    global _registry
    if _registry is None:
        _registry = create_production_registry()
    return _registry


# ── Shared graph invocation helper ───────────────────────────────────────────


async def _run_pipeline(
    state_input: dict,
    session_id: str,
) -> dict:
    """Invoke the LangGraph pipeline and return the full result state."""
    registry = _get_registry()
    runtime = GraphRuntimeContext(tool_registry=registry)

    config = {
        "configurable": {
            "thread_id": session_id,
            "runtime": runtime,
        }
    }

    try:
        graph = await get_orchestrator()
        result = await graph.ainvoke(state_input, config=config)
        return result
    except Exception as e:
        err_str = str(e).lower()
        is_quota = any(kw in err_str for kw in [
            "429", "resource_exhausted", "quota", "rate limit", "resourceexhausted",
        ])
        if is_quota:
            logger.warning("Quota exhausted in agent pipeline: %s", e)
            raise HTTPException(
                status_code=429,
                detail="AI service is experiencing high traffic. Please retry shortly.",
            )
        logger.error("Agent pipeline error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Pipeline error: {e}")


def _build_base_state(
    user_query: str,
    sub_intents: list[str],
    profile: dict,
) -> dict:
    """Construct the initial graph state shared by all agent endpoints."""
    return {
        "state_schema_version": CURRENT_SCHEMA_VERSION,
        "user_query": user_query,
        "farmer_profile": profile,
        "intent": "workflow",
        "sub_intents": sub_intents,
        "intent_confidence": 1.0,
        "chat_history": [],
        "messages": [],
        "reasoning_steps": [],
        "confidence_scores": {},
        "execution_trace": [],
        "graph_path": [],
        "errors": [],
        "tool_outputs": {},
        "timestamps": {},
        "intervention_attempts": {},
        "memory_context": {},
    }


# ── POST /crop-recommendation ───────────────────────────────────────────────


@router.post("/crop-recommendation")
async def crop_recommendation(payload: dict):
    """
    Run crop recommendation through the LangGraph pipeline.
    Backward-compatible with the backend proxy.
    """
    session_id = payload.get("user_id") or str(uuid.uuid4())

    # If a full ContextBuilder context is present, merge it into the profile
    context = payload.get("context")
    if context and isinstance(context, dict) and "profile" in context:
        ctx_profile = context["profile"]
        profile = {
            "user_id": session_id,
            "state": ctx_profile.get("state", payload.get("state", "Madhya Pradesh")),
            "district": ctx_profile.get("district", payload.get("district", "")),
            "village": ctx_profile.get("village", ""),
            "farmer_category": ctx_profile.get("category", payload.get("farmer_category", "marginal")),
            "soil_type": payload.get("soil_type", "Loamy"),
            "season": payload.get("season", "Kharif"),
            "water_availability": payload.get("water_availability", "moderate"),
            "land_size_acres": ctx_profile.get("land_size_acres", payload.get("land_size_acres")),
            "past_crops": payload.get("past_crops", []),
            "crop_types": payload.get("crop_types", []),
            "preferred_language": ctx_profile.get("preferred_language", "ENGLISH"),
        }
        for key in ("farms", "active_crops", "recent_pests",
                    "recent_journal_entries", "farm_summary", "season_context"):
            if key in context:
                profile[key] = context[key]
        if "active_crops" in context:
            profile["crop_types"] = [c.get("crop_name", "") for c in context["active_crops"]]
    else:
        profile = {
            "user_id": session_id,
            "state": payload.get("state", "Madhya Pradesh"),
            "district": payload.get("district", ""),
            "farmer_category": payload.get("farmer_category", "marginal"),
            "soil_type": payload.get("soil_type", "Loamy"),
            "season": payload.get("season", "Kharif"),
            "water_availability": payload.get("water_availability", "moderate"),
            "land_size_acres": payload.get("land_size_acres"),
            "past_crops": payload.get("past_crops", []),
            "crop_types": payload.get("crop_types", []),
            "preferred_language": payload.get("preferred_language", "ENGLISH"),
        }

    query = (
        f"Recommend crops for {profile['season']} season in "
        f"{profile['district'] or profile['state']} with {profile['soil_type']} soil"
    )

    state_input = _build_base_state(query, ["crop"], profile)
    result = await _run_pipeline(state_input, session_id)

    crops = result.get("crop_recommendations")
    return {
        "crop_recommendations": crops,
        "summary": result.get("final_summary") or result.get("final_response", ""),
        "confidence": result.get("confidence_scores", {}).get("crop"),
        "graph_path": result.get("graph_path"),
    }


# ── POST /scheme-recommendation ─────────────────────────────────────────────


@router.post("/scheme-recommendation")
async def scheme_recommendation(payload: dict):
    """
    Run scheme recommendation through the LangGraph pipeline.
    Backward-compatible with the backend proxy.
    """
    session_id = payload.get("user_id") or str(uuid.uuid4())

    context = payload.get("context")
    if context and isinstance(context, dict) and "profile" in context:
        ctx_profile = context["profile"]
        profile = {
            "user_id": session_id,
            "state": ctx_profile.get("state", payload.get("state", "Madhya Pradesh")),
            "district": ctx_profile.get("district", payload.get("district", "")),
            "village": ctx_profile.get("village", ""),
            "farmer_category": ctx_profile.get("category", payload.get("farmer_category", "marginal")),
            "crop_types": payload.get("crop_types", []),
            "annual_income": ctx_profile.get("annual_income", payload.get("annual_income")),
            "gender": ctx_profile.get("gender", payload.get("gender")),
            "age": ctx_profile.get("age", payload.get("age")),
            "preferred_language": ctx_profile.get("preferred_language", "ENGLISH"),
        }
        for key in ("farms", "active_crops", "recent_pests",
                    "recent_journal_entries", "farm_summary", "season_context"):
            if key in context:
                profile[key] = context[key]
        if "active_crops" in context:
            profile["crop_types"] = [c.get("crop_name", "") for c in context["active_crops"]]
    else:
        profile = {
            "user_id": session_id,
            "state": payload.get("state", "Madhya Pradesh"),
            "district": payload.get("district", ""),
            "farmer_category": payload.get("farmer_category", "marginal"),
            "crop_types": payload.get("crop_types", []),
            "annual_income": payload.get("annual_income"),
            "gender": payload.get("gender"),
            "age": payload.get("age"),
            "preferred_language": payload.get("preferred_language", "ENGLISH"),
        }

    query = (
        f"Find government schemes for a {profile['farmer_category']} farmer "
        f"in {profile['district'] or profile['state']}"
    )

    state_input = _build_base_state(query, ["crop", "scheme"], profile)
    result = await _run_pipeline(state_input, session_id)

    return {
        "scheme_recommendations": result.get("scheme_recommendations"),
        "crop_recommendations": result.get("crop_recommendations"),
        "summary": result.get("final_summary") or result.get("final_response", ""),
        "confidence": result.get("confidence_scores", {}).get("scheme"),
        "graph_path": result.get("graph_path"),
    }


# ── POST /full-analysis ─────────────────────────────────────────────────────


@router.post("/full-analysis")
async def full_analysis(payload: dict):
    """
    Run the full multi-agent pipeline through LangGraph.
    Backward-compatible with the backend proxy.
    """
    session_id = payload.get("user_id") or str(uuid.uuid4())

    context = payload.get("context")
    if context and isinstance(context, dict) and "profile" in context:
        ctx_profile = context["profile"]
        profile = {
            "user_id": session_id,
            "state": ctx_profile.get("state", payload.get("state", "Madhya Pradesh")),
            "district": ctx_profile.get("district", payload.get("district", "")),
            "village": ctx_profile.get("village", ""),
            "farmer_category": ctx_profile.get("category", payload.get("farmer_category", "marginal")),
            "soil_type": payload.get("soil_type", "Loamy"),
            "season": payload.get("season", "Kharif"),
            "water_availability": payload.get("water_availability", "moderate"),
            "land_size_acres": ctx_profile.get("land_size_acres", payload.get("land_size_acres")),
            "past_crops": payload.get("past_crops", []),
            "crop_types": payload.get("crop_types", []),
            "annual_income": ctx_profile.get("annual_income", payload.get("annual_income")),
            "gender": ctx_profile.get("gender", payload.get("gender")),
            "age": ctx_profile.get("age", payload.get("age")),
            "preferred_language": ctx_profile.get("preferred_language", "ENGLISH"),
        }
        for key in ("farms", "active_crops", "recent_pests",
                    "recent_journal_entries", "farm_summary", "season_context"):
            if key in context:
                profile[key] = context[key]
        if "active_crops" in context:
            profile["crop_types"] = [c.get("crop_name", "") for c in context["active_crops"]]
    else:
        profile = {
            "user_id": session_id,
            "state": payload.get("state", "Madhya Pradesh"),
            "district": payload.get("district", ""),
            "farmer_category": payload.get("farmer_category", "marginal"),
            "soil_type": payload.get("soil_type", "Loamy"),
            "season": payload.get("season", "Kharif"),
            "water_availability": payload.get("water_availability", "moderate"),
            "land_size_acres": payload.get("land_size_acres"),
            "past_crops": payload.get("past_crops", []),
            "crop_types": payload.get("crop_types", []),
            "annual_income": payload.get("annual_income"),
            "gender": payload.get("gender"),
            "age": payload.get("age"),
            "preferred_language": payload.get("preferred_language", "ENGLISH"),
        }

    # Determine sub_intents from payload or default to full suite
    user_query = payload.get("user_query", "")
    if not user_query:
        user_query = (
            f"Full agricultural analysis for {profile['season']} season in "
            f"{profile['district'] or profile['state']}"
        )

    # Full analysis includes crop + market + scheme (pest only if image provided)
    sub_intents = ["crop", "market", "scheme"]

    state_input = _build_base_state(user_query, sub_intents, profile)

    # Carry over pest context if provided
    if payload.get("pest_detection_result"):
        state_input["pest_detection_result"] = {
            "context": payload["pest_detection_result"],
        }

    result = await _run_pipeline(state_input, session_id)

    # Build backward-compatible pipeline response
    steps = []
    for trace_entry in result.get("execution_trace", []):
        steps.append({
            "agent_name": trace_entry.get("node", ""),
            "success": trace_entry.get("status") == "success",
            "data": {},
            "error": (
                trace_entry.get("reasoning")
                if trace_entry.get("status") == "failed"
                else None
            ),
        })

    return {
        "pipeline_id": session_id,
        "steps": steps,
        "crop_recommendations": result.get("crop_recommendations"),
        "market_analysis": result.get("market_analysis"),
        "scheme_recommendations": result.get("scheme_recommendations"),
        "summary": result.get("final_summary") or result.get("final_response", ""),
        "graph_path": result.get("graph_path"),
        "confidence_scores": result.get("confidence_scores"),
    }
