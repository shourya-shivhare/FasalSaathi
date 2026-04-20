"""
LangGraph-based Crop Advisor Agent.

Optimized for Gemini 2.5 Flash Free Tier (10 RPM):
  - Supervisor + Worker merged into a SINGLE LLM call where possible
  - Keyword-based fast routing to skip the supervisor LLM call
  - Max 2 LLM calls per chat message (down from 3)

Flow:
  START
    └─► router (keyword-first, LLM-fallback)
          ├─► weather_agent (Specialist) ─► END
          ├─► market_agent  (Specialist) ─► END
          ├─► pest_agent    (Specialist) ─► END
          └─► general_agent (Direct)     ─► END
"""
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator
import re
import logging
from langgraph.graph import StateGraph, END

from app.core.llm import get_llm, safe_llm_invoke
from app.prompts.templates import (
    weather_specialist_prompt,
    market_specialist_prompt,
    pest_specialist_prompt
)
from app.tools.weather_tool import get_weather_summary
from app.tools.market_tool import get_market_price

logger = logging.getLogger(__name__)

# ── State schema ──────────────────────────────────────────────────────────────
class AdvisorState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_agent: str          # "WEATHER_EXPERT" | "MARKET_EXPERT" | "PEST_EXPERT" | "GENERAL"
    worker_context: str      # Collected info from workers
    location: str
    final_answer: str
    analysis_context: dict   # Orchestrator pipeline output (crops, schemes, summary)


# ── Keyword-based fast router (saves 1 LLM call per message) ─────────────────
WEATHER_KEYWORDS = re.compile(
    r"\b(weather|mausam|barish|rain|temperature|taapmaan|forecast|humidity|"
    r"irrigation|sinchai|monsoon|hail|frost|drought|sukhaa|badal|cloud|storm|toofan)\b",
    re.IGNORECASE
)
MARKET_KEYWORDS = re.compile(
    r"\b(price|daam|rate|mandi|market|bazaar|sell|bech|msp|khareed|buy|cost|"
    r"महंगा|सस्ता|भाव|मंडी|minimum support|procurement)\b",
    re.IGNORECASE
)
PEST_KEYWORDS = re.compile(
    r"\b(pest|keeda|keet|rog|disease|infection|fungus|blight|insect|bug|"
    r"spray|dawai|pesticide|कीट|रोग|फफूंद|इल्ली|aphid|mite|wilt|rot|borer|"
    r"leaf spot|yellow|brown|damage|attacked)\b",
    re.IGNORECASE
)


# ── Nodes ─────────────────────────────────────────────────────────────────────
llm = get_llm()


def router_node(state: AdvisorState) -> AdvisorState:
    """
    Smart router: tries keyword matching FIRST (free, instant).
    Only falls back to LLM if keywords don't match.
    This saves 1 LLM call (~6 seconds) for most queries.
    """
    user_text = state["messages"][-1].content if state["messages"] else ""

    # Keyword-based routing (no LLM call needed)
    if WEATHER_KEYWORDS.search(user_text):
        logger.info("⚡ Fast-routed to WEATHER_EXPERT via keywords")
        return {**state, "next_agent": "WEATHER_EXPERT"}

    if MARKET_KEYWORDS.search(user_text):
        logger.info("⚡ Fast-routed to MARKET_EXPERT via keywords")
        return {**state, "next_agent": "MARKET_EXPERT"}

    if PEST_KEYWORDS.search(user_text):
        logger.info("⚡ Fast-routed to PEST_EXPERT via keywords")
        return {**state, "next_agent": "PEST_EXPERT"}

    # No keyword match → route to general (direct LLM answer, still only 1 call)
    logger.info("⚡ No specialist keywords found, routing to GENERAL")
    return {**state, "next_agent": "GENERAL"}


def weather_worker(state: AdvisorState) -> AdvisorState:
    """Specialized node for solving weather queries. Single LLM call."""
    weather_data = get_weather_summary.invoke(state.get("location", "Delhi"))
    user_query = state["messages"][-1].content

    # Include analysis context if available
    analysis_text = _build_analysis_context_text(state)
    context = f"{weather_data}"
    if analysis_text:
        context += f"\n\nFarmer's analysis context:\n{analysis_text}"

    content = safe_llm_invoke(
        llm,
        weather_specialist_prompt.format_messages(
            input=user_query,
            context=context
        ),
        fallback=f"Based on available weather data for your area: {weather_data}"
    )
    return {
        **state,
        "messages": [AIMessage(content=content)],
        "final_answer": content,
    }


def market_worker(state: AdvisorState) -> AdvisorState:
    """Specialized node for solving market/price queries. Single LLM call."""
    prices = get_market_price.invoke({})
    user_query = state["messages"][-1].content

    analysis_text = _build_analysis_context_text(state)
    context = f"{prices}"
    if analysis_text:
        context += f"\n\nFarmer's analysis context:\n{analysis_text}"

    content = safe_llm_invoke(
        llm,
        market_specialist_prompt.format_messages(
            input=user_query,
            context=context
        ),
        fallback=f"Current market information: {prices}"
    )
    return {
        **state,
        "messages": [AIMessage(content=content)],
        "final_answer": content,
    }


def pest_worker(state: AdvisorState) -> AdvisorState:
    """Specialized node for solving pest/disease queries. Single LLM call."""
    user_query = state["messages"][-1].content

    analysis_text = _build_analysis_context_text(state)
    context = "Visual detection data provides context for this diagnosis."
    if analysis_text:
        context += f"\n\nFarmer's analysis context:\n{analysis_text}"

    content = safe_llm_invoke(
        llm,
        pest_specialist_prompt.format_messages(
            input=user_query,
            context=context
        ),
        fallback="For pest identification, please upload a clear photo of the affected crop area."
    )
    return {
        **state,
        "messages": [AIMessage(content=content)],
        "final_answer": content,
    }


def _build_analysis_context_text(state: AdvisorState) -> str:
    """Extract structured context from analysis_context for the LLM prompt."""
    ctx = state.get("analysis_context", {}) or {}
    parts = []

    # Extract crop recommendations
    crops_data = ctx.get("crops")
    if crops_data:
        rec_crops = crops_data.get("recommended_crops", [])
        if rec_crops:
            crop_names = [c.get("crop_name", "") for c in rec_crops if c.get("crop_name")]
            if crop_names:
                parts.append(f"Recommended crops: {', '.join(crop_names)}")
            reasoning = crops_data.get("reasoning_summary", "")
            if reasoning:
                parts.append(f"Crop reasoning: {reasoning[:200]}")

    # Extract matched schemes
    schemes_data = ctx.get("schemes")
    if schemes_data:
        matched = schemes_data.get("matched_schemes", [])
        if matched:
            scheme_names = [s.get("scheme_name", "") for s in matched[:5] if s.get("scheme_name")]
            if scheme_names:
                parts.append(f"Eligible government schemes: {', '.join(scheme_names)}")

    # Include pipeline summary if provided
    summary = ctx.get("summary", "")
    if summary:
        parts.append(f"Previous analysis summary: {summary[:300]}")

    return "\n".join(parts)


def general_node(state: AdvisorState) -> AdvisorState:
    """Handle general queries directly. Single LLM call — no supervisor overhead."""
    user_query = state["messages"][-1].content
    analysis_text = _build_analysis_context_text(state)

    context_section = ""
    if analysis_text:
        context_section = f"""\nThe farmer has this analysis context from a previous assessment:
{analysis_text}

Use this context naturally to personalize your answer. Don't repeat it all — only reference what's relevant to the question.
"""

    answer = safe_llm_invoke(
        llm,
        f"""You are FasalSaathi, a friendly Indian farming assistant.
{context_section}
The farmer asked: {user_query}

Give simple, actionable, warm advice. If analysis context is available, refer to it naturally.
Answer in the same language the farmer used.""",
        fallback="Namaste! I'm FasalSaathi, your farming companion. I can help you with weather updates, market prices, and pest identification. How can I assist you today?"
    )

    return {
        **state,
        "messages": [AIMessage(content=answer)],
        "final_answer": answer,
    }


# ── Routing Logic ──────────────────────────────────────────────────────────────
def route_decision(state: AdvisorState) -> str:
    return state["next_agent"]


# ── Graph assembly ─────────────────────────────────────────────────────────────
def build_crop_advisor_graph():
    builder = StateGraph(AdvisorState)

    builder.add_node("router", router_node)
    builder.add_node("weather_agent", weather_worker)
    builder.add_node("market_agent", market_worker)
    builder.add_node("pest_agent", pest_worker)
    builder.add_node("general_agent", general_node)

    builder.set_entry_point("router")
    
    builder.add_conditional_edges(
        "router",
        route_decision,
        {
            "WEATHER_EXPERT": "weather_agent",
            "MARKET_EXPERT": "market_agent",
            "PEST_EXPERT": "pest_agent",
            "GENERAL": "general_agent",
        },
    )
    
    # All workers go directly to END (no separate synthesizer step)
    builder.add_edge("weather_agent", END)
    builder.add_edge("market_agent", END)
    builder.add_edge("pest_agent", END)
    builder.add_edge("general_agent", END)

    return builder.compile()


crop_advisor_graph = build_crop_advisor_graph()
