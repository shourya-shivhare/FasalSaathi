"""
Intent Router — LLM-first classification.
Regex ONLY for trivial greetings/thanks (zero LLM calls).
Everything else → Gemini classification.

Intent categories:
  - greeting: trivial greetings/thanks (regex)
  - data_retrieval: farmer is asking for THEIR OWN data
  - data_analysis: farmer wants analysis OF their data
  - conversational: general questions, advice, educational
  - workflow: needs AI agent execution (crop advice, market data, pest ID, schemes)
  - follow_up: references prior results
"""
from __future__ import annotations

import json
import re
import logging
import time

from ai_service.app.core.llm import get_llm, safe_llm_invoke_async
from ai_service.app.core.retry import retry_async, GEMINI_RETRY
from ai_service.app.graph.state import FasalSaathiState
from langchain_core.runnables import RunnableConfig

logger = logging.getLogger(__name__)

# ── Regex fast-path: ONLY greetings & thanks ─────────────────────────────────
GREETING_RE = re.compile(
    r"^\s*(hi|hello|hey|namaste|namaskar|ram ram|jai hind|"
    r"good\s*(morning|afternoon|evening)|kaise\s+ho|kya\s+hal)\s*[!?.]*\s*$",
    re.IGNORECASE,
)
THANKS_RE = re.compile(
    r"^\s*(thanks?|thank\s*you|dhanyavaad|shukriya|okay|ok|bye|alvida)\s*[!?.]*\s*$",
    re.IGNORECASE,
)

# ── LLM Classification Prompt ────────────────────────────────────────────────
INTENT_PROMPT = """\
You are an intent classifier for FasalSaathi, an Indian agricultural AI assistant.

Classify the farmer's message into ONE intent and zero or more sub_intents.

INTENTS (choose exactly ONE):

- "data_retrieval": The farmer is asking about THEIR OWN data that exists in the database.
  MUST classify as this when user says anything like:
    "my farms", "my crops", "show me my", "what do I have", "list my",
    "how many farms", "what is planted", "what pests were detected",
    "my profile", "my pest history", "show my scan history",
    "what land do I own", "tell me about my farms", "which crops are active",
    "what crop cycles", "what farms do I have", "show my farms",
    "show my crops", "what notifications", "my recent scans"
  The key signal is the user asking to SEE or LIST their own records.

- "data_analysis": The farmer wants ANALYSIS of their own data.
  Examples: "which farm is largest?", "compare my farms", "best performing crop",
    "summarize my farms", "which crop has most pest detections?",
    "total area across my farms"
  The key signal is comparison, ranking, summary, or aggregation of their data.

- "conversational": General questions, explanations, advice not needing agent workflows or data.
  Examples: "what is crop rotation?", "explain pest management", "how does nitrogen affect crops?"

- "workflow": Requests needing AI agent execution (crop recommendations, market data, pest ID, schemes)
  Examples: "what should I grow?", "recommend crops", "identify this pest", "market prices",
    "government schemes for me", "mandi rates"

- "follow_up": References prior results ("tell me more", "the first crop", "explain why")

SUB_INTENTS (only for "workflow"):
- "pest": Insects, disease, damage, infection, spots, image upload requests
- "crop": What to grow, rotation, seasonal planning, crop recommendations
- "market": Price, mandi, sell, buy, MSP, rate, profit, market trends
- "scheme": Subsidy, loan, insurance, government, yojana, PM Kisan

A query CAN have MULTIPLE sub_intents.

CRITICAL RULES:
1. If the user is asking to SEE, LIST, or SHOW their own data → "data_retrieval"
2. If the user is asking to COMPARE, RANK, or SUMMARIZE their data → "data_analysis"
3. "data_retrieval" and "data_analysis" NEVER have sub_intents
4. When in doubt between "data_retrieval" and "conversational", prefer "data_retrieval"
   if the query mentions "my", "I have", or personal possessive language

Return ONLY valid JSON:
{"intent": "data_retrieval", "sub_intents": [], "confidence": 0.95}
"""


def _parse_json_response(raw: str) -> dict:
    """Extract JSON from LLM response, handling markdown fences."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        text = text.rsplit("```", 1)[0]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find embedded JSON
        match = re.search(r"\{[^{}]*\}", text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return {"intent": "conversational", "sub_intents": [], "confidence": 0.5}


async def intent_router_node(state: FasalSaathiState, config: RunnableConfig) -> dict:
    """
    LLM-first intent classification.
    Regex only for trivial greetings/thanks.
    """
    start = time.time()
    query = state.get("user_query", "")

    # ── Regex fast-path: greetings (zero LLM calls) ──────────────────────
    if GREETING_RE.match(query):
        return {
            "intent": "greeting",
            "sub_intents": [],
            "intent_confidence": 1.0,
            "graph_path": ["intent_router"],
            "execution_trace": [{
                "node": "intent_router", "status": "success",
                "duration_ms": round((time.time() - start) * 1000, 2),
                "reasoning": "Greeting regex match", "confidence": 1.0,
                "timestamp": _now_iso(),
            }],
        }

    if THANKS_RE.match(query):
        return {
            "intent": "greeting",
            "sub_intents": [],
            "intent_confidence": 1.0,
            "graph_path": ["intent_router"],
            "execution_trace": [{
                "node": "intent_router", "status": "success",
                "duration_ms": round((time.time() - start) * 1000, 2),
                "reasoning": "Thanks/bye regex match", "confidence": 1.0,
                "timestamp": _now_iso(),
            }],
        }

    # ── Image resumption after interrupt ──────────────────────────────────
    if state.get("uploaded_image_id") and state.get("pending_action") == "waiting_for_image":
        return {
            "intent": "workflow",
            "sub_intents": ["pest"],
            "intent_confidence": 0.95,
            "pending_action": None,
            "graph_path": ["intent_router"],
            "execution_trace": [{
                "node": "intent_router", "status": "success",
                "duration_ms": round((time.time() - start) * 1000, 2),
                "reasoning": "Image upload detected — resuming pest workflow",
                "confidence": 0.95, "timestamp": _now_iso(),
            }],
        }

    # ── LLM classification (all other queries) ────────────────────────────
    try:
        llm = get_llm(temperature=0.0)
        raw = await safe_llm_invoke_async(
            llm,
            INTENT_PROMPT + f"\n\nFarmer message: {query}",
            fallback='{"intent": "conversational", "sub_intents": [], "confidence": 0.5}',
        )
        parsed = _parse_json_response(raw)

        intent = parsed.get("intent", "conversational")
        # Validate intent is one of the known types
        valid_intents = {"greeting", "data_retrieval", "data_analysis",
                         "conversational", "workflow", "follow_up"}
        if intent not in valid_intents:
            intent = "conversational"

        return {
            "intent": intent,
            "sub_intents": parsed.get("sub_intents", []),
            "intent_confidence": parsed.get("confidence", 0.7),
            "graph_path": ["intent_router"],
            "execution_trace": [{
                "node": "intent_router", "status": "success",
                "duration_ms": round((time.time() - start) * 1000, 2),
                "reasoning": f"LLM classified as {intent}",
                "confidence": parsed.get("confidence", 0.7),
                "timestamp": _now_iso(),
            }],
        }

    except Exception as e:
        logger.error("Intent router error: %s", e)
        return {
            "intent": "conversational",
            "sub_intents": [],
            "intent_confidence": 0.3,
            "graph_path": ["intent_router"],
            "errors": [{"node": "intent_router", "error": str(e)}],
            "execution_trace": [{
                "node": "intent_router", "status": "failed",
                "duration_ms": round((time.time() - start) * 1000, 2),
                "reasoning": f"Error: {e}", "confidence": 0.3,
                "timestamp": _now_iso(),
            }],
        }


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
