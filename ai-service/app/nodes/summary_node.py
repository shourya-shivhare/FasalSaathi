"""
Summary Node — PRESENTATION-ONLY LLM.
Step 1: Deterministic structured synthesis from agent outputs (locked conclusions)
Step 2: LLM converts to farmer-friendly text (cannot modify logic)
Step 3: Append confidence disclaimer for low-confidence results
"""
from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone

from app.core.llm import get_llm, safe_llm_invoke_async
from app.graph.state import FasalSaathiState
from langchain_core.runnables import RunnableConfig

logger = logging.getLogger(__name__)


async def summary_node(state: FasalSaathiState, config: RunnableConfig) -> dict:
    """
    Summary LLM role: PRESENTATION ONLY.
    - Logic comes ONLY from structured agent outputs
    - LLM converts conclusions into farmer-friendly language
    - LLM CANNOT infer new recommendations
    - LLM CANNOT modify trends
    - LLM CANNOT invent reasoning
    """
    start = time.time()

    # ── Step 1: Build structured summary input (locked conclusions) ───────
    structured = _build_structured_input(state)

    # ── Step 2: LLM presentation formatting ──────────────────────────────
    prompt = _build_presentation_prompt(structured)
    try:
        llm = get_llm(temperature=0.2)
        summary_text = await safe_llm_invoke_async(llm, prompt)
    except Exception as e:
        logger.error("Summary LLM failed: %s", e)
        summary_text = _build_text_fallback(structured)

    # ── Step 3: Append confidence disclaimer ─────────────────────────────
    conf = state.get("confidence_scores", {})
    low = [f"{a} ({c:.0%})" for a, c in conf.items() if c < 0.6]
    if low:
        summary_text += (
            f"\n\n⚠️ Note: {', '.join(low)} results have lower confidence. "
            "Please verify with your local agricultural extension office."
        )

    # Check for manual review warnings
    errors = state.get("errors", [])
    for err in errors:
        if err.get("node") == "manual_review" and err.get("warning"):
            summary_text += f"\n\n{err['warning']}"

    min_conf = min(conf.values()) if conf else 0.5

    logger.info("📝 Summary: %d sections, min_conf=%.2f", len(structured["sections"]), min_conf)

    return {
        "final_summary": summary_text,
        "final_response": summary_text,
        "graph_path": ["summary"],
        "timestamps": {"summary_completed": _now_iso()},
        "reasoning_steps": [{
            "agent": "summary",
            "reasoning": f"Presented outputs from {len(structured['sections'])} agents.",
            "confidence": min_conf,
        }],
        "execution_trace": [{
            "node": "summary", "status": "success",
            "duration_ms": round((time.time() - start) * 1000, 2),
            "reasoning": f"Summary generated from {len(structured['sections'])} agent outputs",
            "confidence": min_conf, "timestamp": _now_iso(),
        }],
    }


def _build_structured_input(state: FasalSaathiState) -> dict:
    """
    Extract LOCKED conclusions from agent outputs.
    This is what the LLM receives — it cannot add logic beyond this.
    """
    sections = []

    pest = state.get("pest_detection_result")
    if pest:
        sections.append({
            "agent": "pest_detection",
            "locked_conclusions": {
                "pests_detected": [d.get("class", "") for d in pest.get("detections", [])],
                "count": pest.get("detection_count", 0),
                "suggestions": [
                    s for d in pest.get("detections", [])[:3]
                    for s in d.get("suggestions", [])[:2]
                ],
            },
            "agent_reasoning": _find_reasoning("pest_detection", state),
            "confidence": state.get("confidence_scores", {}).get("pest", 0),
        })

    crops = state.get("crop_recommendations")
    if crops:
        sections.append({
            "agent": "crop_recommendation",
            "locked_conclusions": {
                "recommended_crops": [
                    {"name": c.get("crop_name"), "confidence": c.get("confidence"),
                     "season": c.get("season"), "reasoning": c.get("reasoning")}
                    for c in crops.get("recommended_crops", [])[:5]
                ],
            },
            "agent_reasoning": _find_reasoning("crop_recommendation", state),
            "confidence": state.get("confidence_scores", {}).get("crop", 0),
        })

    market = state.get("market_analysis")
    if market:
        analysis = market.get("current_market_analysis", {})
        sections.append({
            "agent": "market_intelligence",
            "locked_conclusions": {
                "commodity": market.get("commodity", ""),
                "trend_direction": analysis.get("price_trend", "stable"),
                "modal_price": analysis.get("modal_price", ""),
                "recommendation": market.get("selling_recommendation", ""),
                "risk_level": market.get("risk_level", "MODERATE"),
            },
            "agent_reasoning": _find_reasoning("market_intelligence", state),
            "confidence": state.get("confidence_scores", {}).get("market", 0),
        })

    schemes = state.get("scheme_recommendations")
    if schemes:
        sections.append({
            "agent": "scheme_recommendation",
            "locked_conclusions": {
                "matched_schemes": [
                    {"name": s.get("scheme_name"), "score": s.get("eligibility_score"),
                     "why": s.get("why_recommended")}
                    for s in schemes.get("matched_schemes", [])[:5]
                ],
            },
            "agent_reasoning": _find_reasoning("scheme_recommendation", state),
            "confidence": state.get("confidence_scores", {}).get("scheme", 0),
        })

    return {
        "sections": sections,
        "errors": state.get("errors", []),
    }


def _find_reasoning(agent_node: str, state: FasalSaathiState) -> str:
    """Find reasoning from reasoning_steps for a specific agent."""
    for step in state.get("reasoning_steps", []):
        if step.get("agent") == agent_node:
            return step.get("reasoning", "")
    return ""


def _build_presentation_prompt(structured: dict) -> str:
    """Prompt that STRICTLY forbids LLM from modifying agent conclusions."""
    return f"""\
You are FasalSaathi's summary PRESENTER. Convert the structured agent results below
into a clear, farmer-friendly advisory.

STRICT RULES — VIOLATIONS ARE UNACCEPTABLE:
1. You may ONLY present the conclusions marked "locked_conclusions"
2. You CANNOT change trend directions (if "falling" → say "falling")
3. You CANNOT invent new recommendations beyond what agents concluded
4. You CANNOT modify prices, confidence levels, or scheme details
5. You CANNOT override agent reasoning
6. You CAN simplify language, improve readability, and translate
7. Use confidence qualifiers:
   ≥0.85: "Based on strong data"
   ≥0.70: "Based on our analysis"
   ≥0.50: "With moderate confidence"
   <0.50: "With limited confidence (please verify)"
8. For each section, explain WHY using the provided "agent_reasoning"
9. Use the farmer's language if they wrote in Hindi/regional language
10. Structure with clear headers and bullet points

STRUCTURED INPUT (all conclusions are FINAL — do not alter):
{json.dumps(structured, indent=2, default=str)}

Write a practical, helpful advisory using simple language.
"""


def _build_text_fallback(structured: dict) -> str:
    """Build plain text summary when LLM is unavailable."""
    parts = ["📋 **FasalSaathi Advisory**\n"]
    for section in structured.get("sections", []):
        agent = section.get("agent", "")
        conclusions = section.get("locked_conclusions", {})
        parts.append(f"\n**{agent.replace('_', ' ').title()}:**")
        for key, value in conclusions.items():
            if isinstance(value, list):
                parts.append(f"  • {key}: {', '.join(str(v) for v in value[:3])}")
            else:
                parts.append(f"  • {key}: {value}")
    return "\n".join(parts)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
