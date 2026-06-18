"""
Data Retrieval Node — presents ACTUAL farmer database records.

CRITICAL RULES:
1. NEVER hallucinate farm names, crops, pest detections, or land areas.
2. ONLY return data that exists in the farmer_profile context.
3. If data does not exist, say so honestly.
4. Data retrieval ALWAYS takes priority over recommendations.
5. Present actual records first, then optionally offer analysis.

Route: data_retrieval → memory_persist → observability → END
"""
from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone

from ai_service.app.core.llm import get_llm, safe_llm_invoke_async
from ai_service.app.tools.farmer_data_tools import FarmerDataTools
from ai_service.app.graph.state import FasalSaathiState
from langchain_core.runnables import RunnableConfig

logger = logging.getLogger(__name__)

# ── Presentation Prompt ──────────────────────────────────────────────────────
DATA_PRESENTATION_PROMPT = """\
You are FasalSaathi, a personal farm assistant. The farmer asked a question
about their own data, and the actual database records are provided below.

{language_directive}

USER QUERY: {query}

RETRIEVED DATA SECTIONS:
{data_sections}

STRICT RULES — VIOLATIONS ARE UNACCEPTABLE:
1. You MUST present the ACTUAL data provided above — do NOT invent or fabricate any records.
2. If data says "No farms registered" or similar, say EXACTLY that. Do NOT make up farms.
3. Format the data in a clean, farmer-friendly way using bullet points or numbered lists.
4. Include all relevant fields (names, areas, soil types, dates, stages, etc.).
5. Do NOT replace data with generic agricultural advice.
6. Do NOT add recommendations UNLESS the farmer explicitly asks for them.
7. If some data sections are empty, acknowledge what's missing.
8. Keep your response focused on presenting the farmer's actual records.
9. After presenting data, you MAY ask if they need any analysis or recommendations.
10. Use emojis sparingly (🌾 🌱 🐛 📊) to make the response friendly.

Example good response for "What farms do I have?":
"You have 2 farms registered:

1. 🌾 Green Valley Farm
   • Area: 4.2 acres
   • Soil: Loamy
   • Irrigation: Borewell
   • Active crops: 1

2. 🌾 North Plot
   • Area: 2.1 acres
   • Soil: Clay
   • Irrigation: Rainfed
   • Active crops: 0

Would you like me to analyze your farms or recommend crops?"

Example BAD response:
"You should consider growing wheat next season..." ← NEVER do this for data queries.
"""


async def data_retrieval_node(state: FasalSaathiState, config: RunnableConfig) -> dict:
    """
    Retrieve and present actual farmer data from the injected context.

    Flow:
    1. Initialize FarmerDataTools with farmer_profile from state
    2. Determine which data sections are relevant to the query
    3. Extract the actual records
    4. Use LLM to format them into a farmer-friendly response
    5. NEVER hallucinate — only present what exists
    """
    start = time.time()
    query = state.get("user_query", "")
    farmer_profile = state.get("farmer_profile", {})

    # ── Step 1: Initialize tools ─────────────────────────────────────────
    tools = FarmerDataTools(farmer_profile)

    # ── Step 2: Determine relevant sections ──────────────────────────────
    sections = tools.determine_relevant_sections(query)
    logger.info("📋 Data retrieval: query=%r, sections=%s", query[:80], sections)

    # ── Step 3: Extract actual records ───────────────────────────────────
    sections_data = tools.get_sections_data(sections)

    # Build a structured data string for the LLM
    data_parts = []
    any_data_found = False

    for section_name, section_result in sections_data.items():
        found = section_result.get("found", False)
        count = section_result.get("count", 0)
        data = section_result.get("data", [])
        summary = section_result.get("summary", "")

        if found:
            any_data_found = True

        header = section_name.upper().replace("_", " ")
        data_parts.append(f"--- {header} ---")
        data_parts.append(f"Records found: {count}")
        data_parts.append(f"Summary: {summary}")

        if found and data:
            # Serialize data for the LLM
            data_parts.append(f"Records: {json.dumps(data, indent=2, default=str)}")
        else:
            data_parts.append("No records found for this section.")

        data_parts.append("")

    data_sections_str = "\n".join(data_parts)

    # ── Step 4: Format with LLM ──────────────────────────────────────────
    lang = farmer_profile.get("preferred_language") or "ENGLISH"
    if isinstance(lang, dict):
        lang = lang.get("preferred_language", "ENGLISH")
    language_directive = (
        "RESPOND ENTIRELY IN HINDI (Devanagari script)."
        if lang == "HINDI"
        else "Respond in English."
    )

    prompt = DATA_PRESENTATION_PROMPT.format(
        query=query,
        data_sections=data_sections_str,
        language_directive=language_directive,
    )

    try:
        llm = get_llm(temperature=0.2)
        response = await safe_llm_invoke_async(llm, prompt)
    except Exception as e:
        logger.error("Data retrieval LLM formatting failed: %s", e)
        # Fallback: present raw data without LLM formatting
        response = _build_fallback_response(sections_data, any_data_found)

    logger.info(
        "📋 Data retrieval complete: %d sections, data_found=%s, duration=%.0fms",
        len(sections_data), any_data_found,
        (time.time() - start) * 1000,
    )

    return {
        "final_response": response,
        "graph_path": ["data_retrieval"],
        "timestamps": {"data_retrieval_completed": _now_iso()},
        "execution_trace": [{
            "node": "data_retrieval", "status": "success",
            "duration_ms": round((time.time() - start) * 1000, 2),
            "reasoning": f"Retrieved {len(sections_data)} data sections, data_found={any_data_found}",
            "confidence": 0.95 if any_data_found else 0.8,
            "timestamp": _now_iso(),
        }],
    }


def _build_fallback_response(sections_data: dict, any_data_found: bool) -> str:
    """Build a plain-text response when LLM is unavailable."""
    if not any_data_found:
        return (
            "I couldn't find any data registered in your account. "
            "You can add farms, crop cycles, and more through the FasalSaathi app."
        )

    parts = ["📋 **Your FasalSaathi Data**\n"]

    for section_name, section_result in sections_data.items():
        if not section_result.get("found"):
            continue

        header = section_name.replace("_", " ").title()
        parts.append(f"\n**{header}:**")
        data = section_result.get("data", [])

        if isinstance(data, list):
            for item in data[:10]:  # Limit display
                if isinstance(item, dict):
                    name = (
                        item.get("farm_name")
                        or item.get("crop_name")
                        or item.get("disease_name")
                        or item.get("title")
                        or "Record"
                    )
                    parts.append(f"  • {name}")
                else:
                    parts.append(f"  • {item}")
        elif isinstance(data, dict):
            for k, v in data.items():
                if v is not None:
                    parts.append(f"  • {k.replace('_', ' ').title()}: {v}")

    return "\n".join(parts)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
