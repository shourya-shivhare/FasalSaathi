"""
Conversational + Greeting nodes.
Greeting: static response, no LLM call.
Conversational: LLM-powered general chat with farmer context.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from app.core.llm import get_llm, safe_llm_invoke_async
from app.graph.state import FasalSaathiState
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

FARMER PROFILE:
{farmer_profile}

MEMORY CONTEXT (previous interactions):
{memory_context}

CONVERSATION HISTORY:
{chat_history}

USER QUERY: {query}

Provide a helpful, farmer-friendly response. Use simple language.
If the query is about something specific (weather, crops, etc.), provide useful information.
If you need more details, ask clearly.
Keep responses concise but informative.
If the farmer writes in Hindi, respond in Hindi.
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

    prompt = CONVERSATIONAL_PROMPT.format(
        query=query,
        farmer_profile=_safe_json(farmer_profile),
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
