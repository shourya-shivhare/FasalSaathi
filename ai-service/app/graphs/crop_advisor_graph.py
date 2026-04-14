"""
LangGraph-based Crop Advisor Agent.

True Agentic Flow:
  START
    └─► supervisor (LLM-based Router)
          ├─► weather_agent (Specialist)
          ├─► market_agent  (Specialist)
          ├─► pest_agent    (Specialist)
          └─► synthesizer   (Final Response)
  END
"""
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator
import logging
from langgraph.graph import StateGraph, END

from app.core.llm import get_llm, safe_llm_invoke
from app.prompts.templates import (
    supervisor_prompt,
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
    next_agent: str          # "WEATHER_EXPERT" | "MARKET_EXPERT" | "PEST_EXPERT" | "FINISH"
    worker_context: str      # Collected info from workers
    location: str
    final_answer: str


# ── Nodes ─────────────────────────────────────────────────────────────────────
llm = get_llm()

def supervisor_node(state: AdvisorState) -> AdvisorState:
    """The brain of the orchestration. Decides who speaks next."""
    content = safe_llm_invoke(
        llm,
        supervisor_prompt.format_messages(
            history=state["messages"][:-1],
            input=state["messages"][-1].content
        ),
        fallback="FINISH"
    ).upper()
    
    # Simple parsing logic for the Supervisor's decision
    if "WEATHER_EXPERT" in content:
        next_agent = "WEATHER_EXPERT"
    elif "MARKET_EXPERT" in content:
        next_agent = "MARKET_EXPERT"
    elif "PEST_EXPERT" in content:
        next_agent = "PEST_EXPERT"
    else:
        next_agent = "FINISH"
        
    return {**state, "next_agent": next_agent}


def weather_worker(state: AdvisorState) -> AdvisorState:
    """Specialized node for solving weather queries."""
    weather_data = get_weather_summary.invoke(state.get("location", "Delhi"))
    user_query = state["messages"][-1].content
    
    content = safe_llm_invoke(
        llm,
        weather_specialist_prompt.format_messages(
            input=user_query,
            context=weather_data
        ),
        fallback=f"Based on available weather data for your area: {weather_data}"
    )
    return {
        **state, 
        "worker_context": f"WEATHER ADVICE: {content}",
        "next_agent": "FINISH"
    }


def market_worker(state: AdvisorState) -> AdvisorState:
    """Specialized node for solving market/price queries."""
    prices = get_market_price.invoke({})
    user_query = state["messages"][-1].content
    
    content = safe_llm_invoke(
        llm,
        market_specialist_prompt.format_messages(
            input=user_query,
            context=prices
        ),
        fallback=f"Current market information: {prices}"
    )
    return {
        **state, 
        "worker_context": f"MARKET ADVICE: {content}",
        "next_agent": "FINISH"
    }


def pest_worker(state: AdvisorState) -> AdvisorState:
    """Specialized node for solving pest/disease queries."""
    user_query = state["messages"][-1].content
    # Context usually contains the secret detection metadata
    content = safe_llm_invoke(
        llm,
        pest_specialist_prompt.format_messages(
            input=user_query,
            context="Visual detection data provides context for this diagnosis."
        ),
        fallback="For pest identification, please upload a clear photo of the affected crop area."
    )
    return {
        **state, 
        "worker_context": f"PEST ADVICE: {content}",
        "next_agent": "FINISH"
    }


def synthesizer_node(state: AdvisorState) -> AdvisorState:
    """Final node to produce the polished response."""
    # If a worker provided advice, use it. Otherwise, supervisor handles it directly.
    if state.get("worker_context"):
        answer = state["worker_context"]
    else:
        # Supervisor handles general chat
        user_query = state["messages"][-1].content
        answer = safe_llm_invoke(
            llm,
            f"You are FasalSaathi, a friendly Indian farming assistant. Answer the farmer simply and warmly: {user_query}",
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

    builder.add_node("supervisor", supervisor_node)
    builder.add_node("weather_agent", weather_worker)
    builder.add_node("market_agent", market_worker)
    builder.add_node("pest_agent", pest_worker)
    builder.add_node("synthesizer", synthesizer_node)

    builder.set_entry_point("supervisor")
    
    builder.add_conditional_edges(
        "supervisor",
        route_decision,
        {
            "WEATHER_EXPERT": "weather_agent",
            "MARKET_EXPERT": "market_agent",
            "PEST_EXPERT": "pest_agent",
            "FINISH": "synthesizer",
        },
    )
    
    # From workers, go to synthesizer to wrap up
    builder.add_edge("weather_agent", "synthesizer")
    builder.add_edge("market_agent", "synthesizer")
    builder.add_edge("pest_agent", "synthesizer")
    
    builder.add_edge("synthesizer", END)

    return builder.compile()


crop_advisor_graph = build_crop_advisor_graph()
