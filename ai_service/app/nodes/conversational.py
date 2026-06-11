"""
Conversational + Greeting nodes.
Greeting: static response, no LLM call.
Conversational: LLM-powered general chat with farmer context.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from ai_service.app.core.llm import get_llm, safe_llm_invoke_async
from ai_service.app.graph.state import FasalSaathiState
from langchain_core.runnables import RunnableConfig

logger = logging.getLogger(__name__)

GREETING_RESPONSE = (
    "Namaste! 🌾 I'm FasalSaathi, your smart farming companion. I can help you with:\n\n"
    "🌦️ **Weather updates** for your area\n"
    "💰 **Market prices** & mandi rates\n"
    "🐛 **Pest identification** & crop disease advice\n"
    "🌱 **Crop advisory** & farming tips\n"
    "🏛️ **Government schemes** & subsidies\n\n"
    "How can I help you today?"
)

CONVERSATIONAL_PROMPT = """\
You are FasalSaathi, an expert Indian agricultural AI assistant.
You help farmers with crop advice, market prices, pest management, and government schemes.

{language_directive}

FARMER PROFILE:
{farmer_profile}

FARM CONTEXT (active crops, recent pests, farm summary):
{farm_context}

MEMORY CONTEXT (previous interactions):
{memory_context}

CONVERSATION HISTORY:
{chat_history}

USER QUERY: {query}

Provide a helpful, farmer-friendly response. Use simple language.
If the query is about something specific (weather, crops, etc.), provide useful information.
If you need more details, ask clearly.
Keep responses concise but informative.
"""


async def greeting_node(state: FasalSaathiState, config: RunnableConfig) -> dict:
    """Static greeting response — zero LLM calls."""
    return {
        "final_response": GREETING_RESPONSE,
        "graph_path": ["greeting"],
        "timestamps": {"greeting_completed": _now_iso()},
        "execution_trace": [{
            "node": "greeting", "status": "success",
            "duration_ms": 0, "reasoning": "Static greeting",
            "confidence": 1.0, "timestamp": _now_iso(),
        }],
    }


async def conversational_node(state: FasalSaathiState, config: RunnableConfig) -> dict:
    """LLM-powered general conversation with context."""
    start = time.time()
    query = state.get("user_query", "")
    farmer_profile = state.get("farmer_profile", {})
    memory_context = state.get("memory_context", {})
    chat_history = state.get("chat_history", [])

    # Build conversation history string
    history_str = ""
    for msg in chat_history[-6:]:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        history_str += f"{role}: {content}\n"

    # Build language directive
    lang = farmer_profile.get("preferred_language", "ENGLISH")
    language_directive = (
        "RESPOND ENTIRELY IN HINDI (Devanagari script)."
        if lang == "HINDI"
        else "Respond in English."
    )

    # Build farm context summary
    farm_context_parts = []
    active_crops = farmer_profile.get("active_crops", [])
    if active_crops:
        crop_lines = [f"- {c.get('crop_name', '?')} ({c.get('crop_variety', '')}), Stage: {c.get('current_stage', '?')}" for c in active_crops[:5]]
        farm_context_parts.append("Active Crops:\n" + "\n".join(crop_lines))
    recent_pests = farmer_profile.get("recent_pests", [])
    if recent_pests:
        pest_lines = [f"- {p.get('disease_name', '?')} ({p.get('created_at', '')})" for p in recent_pests[:3]]
        farm_context_parts.append("Recent Pests:\n" + "\n".join(pest_lines))
    farm_summary = farmer_profile.get("farm_summary", {})
    if farm_summary:
        farm_context_parts.append(f"Farm Summary: {farm_summary.get('total_farms', 0)} farms, {farm_summary.get('active_crop_count', 0)} active crops")
    farm_context_str = "\n".join(farm_context_parts) if farm_context_parts else "No farm data available."

    prompt = CONVERSATIONAL_PROMPT.format(
        query=query,
        farmer_profile=_safe_json(farmer_profile),
        farm_context=farm_context_str,
        language_directive=language_directive,
        memory_context=_safe_json(
            {k: v[:2] if isinstance(v, list) else v
             for k, v in memory_context.items()}
        ),
        chat_history=history_str or "No previous conversation.",
    )

    try:
        llm = get_llm(temperature=0.4)
        response = await safe_llm_invoke_async(llm, prompt)

        return {
            "final_response": response,
            "graph_path": ["conversational"],
            "timestamps": {"conversational_completed": _now_iso()},
            "execution_trace": [{
                "node": "conversational", "status": "success",
                "duration_ms": round((time.time() - start) * 1000, 2),
                "reasoning": "LLM conversational response",
                "confidence": 0.8, "timestamp": _now_iso(),
            }],
        }
    except Exception as e:
        logger.error("Conversational node error: %s", e)
        return {
            "final_response": (
                "I'm having trouble processing your request right now. "
                "Could you try again in a moment?"
            ),
            "graph_path": ["conversational"],
            "errors": [{"node": "conversational", "error": str(e)}],
            "execution_trace": [{
                "node": "conversational", "status": "failed",
                "duration_ms": round((time.time() - start) * 1000, 2),
                "reasoning": f"Error: {e}", "confidence": 0.3,
                "timestamp": _now_iso(),
            }],
        }


def _safe_json(obj) -> str:
    import json
    try:
        return json.dumps(obj, default=str, indent=2)
    except Exception:
        return str(obj)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
