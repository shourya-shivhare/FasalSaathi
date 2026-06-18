"""
Data Analysis Node — analyzes ACTUAL farmer data to answer comparative,
ranking, and summarization queries.

CRITICAL RULES:
1. ALL analysis must be grounded in actual farmer data.
2. Retrieve actual records FIRST, then analyze.
3. NEVER fabricate statistics, rankings, or comparisons.
4. If insufficient data exists, say so honestly.
5. Include source references ("Based on your 3 registered farms...").

Route: data_analysis → memory_persist → observability → END
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

# ── Analysis Prompt ──────────────────────────────────────────────────────────
DATA_ANALYSIS_PROMPT = """\
You are FasalSaathi, a personal farm data analyst. The farmer has asked a
question that requires ANALYSIS of their actual data.

{language_directive}

USER QUERY: {query}

FARMER'S ACTUAL DATA:
{farmer_data}

STRICT RULES — VIOLATIONS ARE UNACCEPTABLE:
1. Your analysis MUST be based ONLY on the actual data provided above.
2. Do NOT invent farms, crops, pest detections, or statistics.
3. Start by referencing the actual data ("Based on your {farm_count} farms...").
4. Provide clear comparisons, rankings, or summaries as requested.
5. Use numbers and specifics from the actual records.
6. If there is insufficient data for the requested analysis, say so honestly.
7. After analysis, you MAY offer actionable recommendations based on findings.
8. Format with clear headers and bullet points.

Example analysis for "Which farm is largest?":
"Based on your 2 registered farms:

📊 **Farm Size Comparison:**
1. 🥇 Green Valley Farm — 4.2 acres (largest)
2. North Plot — 2.1 acres

Total registered area: 6.3 acres

Green Valley Farm is twice the size of North Plot.
Would you like crop recommendations for either farm?"

Example BAD response:
"Generally, larger farms can benefit from..." ← NEVER give generic analysis.
"""


async def data_analysis_node(state: FasalSaathiState, config: RunnableConfig) -> dict:
    """
    Analyze actual farmer data to answer comparative/ranking/summary queries.

    Flow:
    1. Load ALL farmer data sections (we need full context for analysis)
    2. Build a comprehensive data payload
    3. Use LLM to analyze the ACTUAL data and answer the query
    4. Ensure all conclusions reference real records
    """
    start = time.time()
    query = state.get("user_query", "")
    farmer_profile = state.get("farmer_profile", {})

    # ── Step 1: Load all data for analysis ────────────────────────────────
    tools = FarmerDataTools(farmer_profile)

    all_sections = ["farms", "active_crops", "crop_history",
                    "pest_history", "farm_summary", "season_context"]
    sections_data = tools.get_sections_data(all_sections)

    # ── Step 2: Build comprehensive data payload ─────────────────────────
    farmer_data_parts = []
    farm_count = 0

    for section_name, section_result in sections_data.items():
        found = section_result.get("found", False)
        data = section_result.get("data", [])

        header = section_name.upper().replace("_", " ")
        farmer_data_parts.append(f"--- {header} ---")

        if found and data:
            if section_name == "farms":
                farm_count = len(data) if isinstance(data, list) else 0
            farmer_data_parts.append(json.dumps(data, indent=2, default=str))
        else:
            farmer_data_parts.append("No data available.")
        farmer_data_parts.append("")

    farmer_data_str = "\n".join(farmer_data_parts)

    # Check if we have any data at all to analyze
    any_data = any(
        s.get("found", False) for s in sections_data.values()
    )

    if not any_data:
        response = (
            "I don't have enough data to perform this analysis. "
            "Your account doesn't have any farms, crops, or pest detection records yet. "
            "Once you add farms and start crop cycles, I'll be able to analyze your data!"
        )
        return {
            "final_response": response,
            "graph_path": ["data_analysis"],
            "timestamps": {"data_analysis_completed": _now_iso()},
            "execution_trace": [{
                "node": "data_analysis", "status": "success",
                "duration_ms": round((time.time() - start) * 1000, 2),
                "reasoning": "No data available for analysis",
                "confidence": 0.9, "timestamp": _now_iso(),
            }],
        }

    # ── Step 3: LLM analysis of actual data ──────────────────────────────
    lang = farmer_profile.get("preferred_language") or "ENGLISH"
    if isinstance(lang, dict):
        lang = lang.get("preferred_language", "ENGLISH")
    language_directive = (
        "RESPOND ENTIRELY IN HINDI (Devanagari script)."
        if lang == "HINDI"
        else "Respond in English."
    )

    prompt = DATA_ANALYSIS_PROMPT.format(
        query=query,
        farmer_data=farmer_data_str,
        language_directive=language_directive,
        farm_count=farm_count,
    )

    try:
        llm = get_llm(temperature=0.3)
        response = await safe_llm_invoke_async(llm, prompt)
    except Exception as e:
        logger.error("Data analysis LLM failed: %s", e)
        # Fallback: present raw summary
        summary = sections_data.get("farm_summary", {}).get("summary", "")
        response = (
            f"I encountered an issue generating the analysis. "
            f"Here's a quick summary of your data:\n\n{summary}\n\n"
            "Please try asking again in a moment."
        )

    logger.info(
        "📊 Data analysis complete: %d sections, duration=%.0fms",
        len(sections_data), (time.time() - start) * 1000,
    )

    return {
        "final_response": response,
        "graph_path": ["data_analysis"],
        "timestamps": {"data_analysis_completed": _now_iso()},
        "execution_trace": [{
            "node": "data_analysis", "status": "success",
            "duration_ms": round((time.time() - start) * 1000, 2),
            "reasoning": f"Analyzed {farm_count} farms and related data",
            "confidence": 0.85, "timestamp": _now_iso(),
        }],
    }


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
