"""
Chat Router — new unified endpoint using LangGraph orchestrator.
Supports:
  - JSON-only chat (text)
  - Multipart upload (text + image for pest detection)
  - Runtime context injection (ToolRegistry via config)
"""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from ai_service.app.core.runtime_context import GraphRuntimeContext
from ai_service.app.core.tool_registry import create_production_registry
from ai_service.app.graph.orchestrator import get_orchestrator
from ai_service.app.graph.state_migration import CURRENT_SCHEMA_VERSION

router = APIRouter()
logger = logging.getLogger(__name__)

# ── Create production ToolRegistry (once at module level) ────────────────────
_registry = None


def _get_registry():
    global _registry
    if _registry is None:
        _registry = create_production_registry()
    return _registry


# ── Request / Response schemas ───────────────────────────────────────────────


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    analysis_context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    graph_path: Optional[List[str]] = None
    confidence_scores: Optional[Dict[str, float]] = None


# ── JSON chat endpoint ───────────────────────────────────────────────────────


@router.post("/", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    """Handle text-only chat through the LangGraph pipeline."""
    session_id = payload.session_id or str(uuid.uuid4())
    user_input = payload.messages[-1].content if payload.messages else ""

    # Build farmer profile from context
    profile = _build_farmer_profile(payload.context, session_id)

    # Build chat history
    chat_history = [
        {"role": m.role, "content": m.content}
        for m in payload.messages[:-1]
    ]

    # Build initial graph state
    initial_state = {
        "state_schema_version": CURRENT_SCHEMA_VERSION,
        "user_query": user_input,
        "farmer_profile": profile,
        "chat_history": chat_history,
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

    return await _invoke_graph(initial_state, session_id)


# ── Multipart upload endpoint (image + text) ────────────────────────────────


@router.post("/upload", response_model=ChatResponse)
async def chat_with_image(
    message: str = Form(""),
    session_id: str = Form(None),
    state: str = Form(""),
    district: str = Form(""),
    farmer_category: str = Form("marginal"),
    soil_type: str = Form("Loamy"),
    season: str = Form("Kharif"),
    image: UploadFile = File(None),
):
    """Handle text + image upload for pest detection through LangGraph."""
    session_id = session_id or str(uuid.uuid4())

    # Build profile from form data
    profile = {
        "user_id": session_id,
        "state": state or "Madhya Pradesh",
        "district": district or "",
        "farmer_category": farmer_category,
        "soil_type": soil_type,
        "season": season,
        "preferred_language": "ENGLISH",
    }

    # Handle image upload
    image_id = None
    image_metadata = None

    if image and image.filename:
        registry = _get_registry()
        image_bytes = await image.read()
        image_id = await registry.image_store.save(image_bytes, image.filename)
        image_metadata = registry.image_store.get_metadata(
            image_id, image.filename, len(image_bytes)
        )
        logger.info("📸 Image uploaded: id=%s, size=%dKB", image_id, len(image_bytes) // 1024)

    initial_state = {
        "state_schema_version": CURRENT_SCHEMA_VERSION,
        "user_query": message or ("Identify the pest in this image" if image_id else ""),
        "farmer_profile": profile,
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
        "uploaded_image_id": image_id,
        "image_metadata": image_metadata,
    }

    return await _invoke_graph(initial_state, session_id)


# ── Internal helpers ─────────────────────────────────────────────────────────


async def _invoke_graph(initial_state: dict, session_id: str) -> ChatResponse:
    """Invoke the LangGraph orchestrator with runtime context injection."""
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
        result = await graph.ainvoke(initial_state, config=config)

        answer = result.get("final_response", "")
        if not answer:
            answer = "I couldn't process that request. Could you rephrase your question?"

        return ChatResponse(
            answer=answer,
            session_id=session_id,
            graph_path=result.get("graph_path"),
            confidence_scores=result.get("confidence_scores"),
        )

    except Exception as e:
        err_str = str(e).lower()
        is_quota = any(kw in err_str for kw in [
            "429", "resource_exhausted", "quota", "rate limit", "resourceexhausted",
        ])

        if is_quota:
            logger.warning("Quota exhausted during graph invoke: %s", e)
            return ChatResponse(
                answer=(
                    "⚠️ I'm experiencing high traffic right now. "
                    "Please wait a moment and try again."
                ),
                session_id=session_id,
            )

        logger.error("Graph invoke error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")


def _build_farmer_profile(context: dict | None, session_id: str) -> dict:
    """Build farmer profile from request context (including ContextBuilder payload)."""
    profile = {
        "user_id": session_id,
        "state": "Madhya Pradesh",
        "district": "",
        "farmer_category": "marginal",
        "soil_type": "Loamy",
        "season": "Kharif",
        "water_availability": "moderate",
        "preferred_language": "ENGLISH",
    }

    if context:
        # If context is a full ContextBuilder payload (has "profile" key),
        # extract profile fields and merge structured farm data directly.
        if "profile" in context:
            ctx_profile = context["profile"]
            profile.update({
                k: v for k, v in {
                    "name": ctx_profile.get("name"),
                    "state": ctx_profile.get("state"),
                    "district": ctx_profile.get("district"),
                    "village": ctx_profile.get("village"),
                    "farmer_category": ctx_profile.get("category"),
                    "annual_income": ctx_profile.get("annual_income"),
                    "gender": ctx_profile.get("gender"),
                    "age": ctx_profile.get("age"),
                    "land_size_acres": ctx_profile.get("land_size_acres"),
                    "preferred_language": ctx_profile.get("preferred_language"),
                }.items()
                if v is not None
            })
            # Forward structured farm management data
            for key in ("farms", "active_crops", "recent_pests",
                        "recent_journal_entries", "farm_summary", "season_context",
                        "pest_history", "crop_history", "profile"):
                if key in context:
                    profile[key] = context[key]
            # Derive crop_types from active_crops for backward compat
            if "active_crops" in context:
                profile["crop_types"] = [c.get("crop_name", "") for c in context["active_crops"]]
        else:
            # Legacy flat context format (backward compat)
            profile.update({
                k: v for k, v in {
                    "state": context.get("state"),
                    "district": context.get("district") or context.get("city"),
                    "farmer_category": context.get("farmer_category"),
                    "soil_type": context.get("soil_type"),
                    "season": context.get("season"),
                    "water_availability": context.get("water_availability"),
                    "crop_types": context.get("crop_types"),
                    "annual_income": context.get("annual_income"),
                    "gender": context.get("gender"),
                    "age": context.get("age"),
                    "land_size_acres": context.get("land_size_acres"),
                    "past_crops": context.get("past_crops"),
                }.items()
                if v is not None
            })

    return profile
