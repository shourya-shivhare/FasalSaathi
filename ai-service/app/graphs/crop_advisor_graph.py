"""
LangGraph-based Crop Advisor Agent.

Graph flow:
  START
    └─► analyze_query  (classifies what the farmer is asking)
          ├─► fetch_weather   (if weather info needed)
          ├─► fetch_market    (if market price needed)
          └─► generate_advice (final answer using gathered context)
  END
"""
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator
from langgraph.graph import StateGraph, END

from app.core.llm import get_llm
from app.prompts.templates import crop_advisor_prompt
from app.tools.weather_tool import get_weather_summary
from app.tools.market_tool import get_market_price


# ── State schema ──────────────────────────────────────────────────────────────
class AdvisorState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    query_type: str          # "weather" | "market" | "general"
    weather_info: str
    market_info: str
    final_answer: str


# ── Nodes ─────────────────────────────────────────────────────────────────────
llm = get_llm()


def analyze_query(state: AdvisorState) -> AdvisorState:
    """Classify the farmer's query."""
    last_msg = state["messages"][-1].content.lower()
    if any(w in last_msg for w in ["weather", "rain", "temperature", "मौसम"]):
        query_type = "weather"
    elif any(w in last_msg for w in ["price", "market", "rate", "mandi", "मंडी"]):
        query_type = "market"
    else:
        query_type = "general"
    return {**state, "query_type": query_type}


def fetch_weather(state: AdvisorState) -> AdvisorState:
    weather = get_weather_summary()
    return {**state, "weather_info": weather}


def fetch_market(state: AdvisorState) -> AdvisorState:
    market = get_market_price()
    return {**state, "market_info": market}


def generate_advice(state: AdvisorState) -> AdvisorState:
    context = ""
    if state.get("weather_info"):
        context += f"\nWeather context: {state['weather_info']}"
    if state.get("market_info"):
        context += f"\nMarket context: {state['market_info']}"

    user_query = state["messages"][-1].content + context
    response = llm.invoke(
        crop_advisor_prompt.format_messages(input=user_query, history=[])
    )
    answer = response.content
    return {
        **state,
        "messages": [AIMessage(content=answer)],
        "final_answer": answer,
    }


# ── Routing ────────────────────────────────────────────────────────────────────
def route_query(state: AdvisorState) -> str:
    return state["query_type"]  # "weather" | "market" | "general"


# ── Graph assembly ─────────────────────────────────────────────────────────────
def build_crop_advisor_graph():
    builder = StateGraph(AdvisorState)

    builder.add_node("analyze_query", analyze_query)
    builder.add_node("fetch_weather", fetch_weather)
    builder.add_node("fetch_market", fetch_market)
    builder.add_node("generate_advice", generate_advice)

    builder.set_entry_point("analyze_query")
    builder.add_conditional_edges(
        "analyze_query",
        route_query,
        {
            "weather": "fetch_weather",
            "market": "fetch_market",
            "general": "generate_advice",
        },
    )
    builder.add_edge("fetch_weather", "generate_advice")
    builder.add_edge("fetch_market", "generate_advice")
    builder.add_edge("generate_advice", END)

    return builder.compile()


crop_advisor_graph = build_crop_advisor_graph()
