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
You are FasalSaathi, a personal farm assistant for Indian farmers.
You help with crop advice, market prices, pest management, and government schemes.

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

CRITICAL DATA-FIRST RULES (MUST follow in order):

1. DATA RETRIEVAL PRIORITY: If the farmer is asking about THEIR OWN data
   (farms, crops, pests, profile, land, scans) AND actual data exists in
   FARM CONTEXT above — you MUST present that actual data first.
   NEVER generate generic advice when actual records exist.

2. If FARM CONTEXT shows farms, crops, or pest data — reference the
   ACTUAL names, areas, soil types, and stages from the data above.
   NEVER invent farm names, crop names, or pest detections.

3. If FARM CONTEXT shows "No farm data available" or is empty,
   acknowledge it honestly: "I couldn't find any farms/crops registered
   in your account."

4. ONLY after presenting actual data, you MAY offer additional insights
   or recommendations based on that data.

5. For educational/general questions (not about personal data), provide
   helpful agricultural knowledge using simple language.

6. Keep responses concise but informative. Use bullet points for lists.
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

    # Build farm context summary — include actual data for data-first safety net
    farm_context_parts = []

    # Include farm details
    farms = farmer_profile.get("farms", [])
    if farms:
        farm_lines = [
            f"- {f.get('farm_name', '?')}: {f.get('total_area', '?')} acres, "
            f"Soil: {f.get('soil_type', '?')}, Irrigation: {f.get('irrigation_source', '?')}, "
            f"Active crops: {f.get('active_crop_count', 0)}"
            for f in farms[:10]
        ]
        farm_context_parts.append("Farms:\n" + "\n".join(farm_lines))

    active_crops = farmer_profile.get("active_crops", [])
    if active_crops:
        crop_lines = [
            f"- {c.get('crop_name', '?')} ({c.get('crop_variety', '')}), "
            f"Stage: {c.get('current_stage', '?')}, Farm: {c.get('farm_name', '?')}"
            for c in active_crops[:10]
        ]
        farm_context_parts.append("Active Crops:\n" + "\n".join(crop_lines))

    # Include pest history
    pest_data = farmer_profile.get("pest_history") or farmer_profile.get("recent_pests", [])
    if pest_data:
        pest_lines = [
            f"- {p.get('disease_name', '?')} (Confidence: {p.get('confidence', '?')}, "
            f"Date: {p.get('created_at', '?')}, Farm: {p.get('farm_name', '?')})"
            for p in pest_data[:5]
        ]
        farm_context_parts.append("Pest History:\n" + "\n".join(pest_lines))

    farm_summary = farmer_profile.get("farm_summary", {})
    if farm_summary:
        farm_context_parts.append(
            f"Farm Summary: {farm_summary.get('total_farms', 0)} farms, "
            f"{farm_summary.get('total_registered_area', 0)} acres total, "
            f"{farm_summary.get('active_crop_count', 0)} active crops, "
            f"{farm_summary.get('recent_pest_count', 0)} pest detections"
        )
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
