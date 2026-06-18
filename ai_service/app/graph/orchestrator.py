"""
FasalSaathi Unified LangGraph Orchestrator — full graph assembly.

Graph topology:
    START → memory_retrieve → intent_router → {greeting | data_retrieval | data_analysis | conversational | context_retrieval | planner}
    planner → validator → {dispatch agents via conditional_edges + Send()}
    agents → {human_intervention | manual_review | summary} → memory_persist → observability → END
    data_retrieval → memory_persist → observability → END
    data_analysis → memory_persist → observability → END

No executor node — LangGraph orchestrates via conditional edges.
"""
from __future__ import annotations

import logging
from typing import Union

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from ai_service.app.graph.state import FasalSaathiState
from ai_service.app.graph.checkpoints import get_checkpointer

# ── Import all nodes ─────────────────────────────────────────────────────────
from ai_service.app.nodes.memory_node import memory_retrieve_node, memory_persist_node
from ai_service.app.graph.intent_router import intent_router_node
from ai_service.app.nodes.conversational import greeting_node, conversational_node
from ai_service.app.nodes.context_retrieval import context_retrieval_node
from ai_service.app.graph.planner import planner_node
from ai_service.app.graph.validator import validator_node
from ai_service.app.nodes.crop_recommendation import crop_recommendation_node
from ai_service.app.nodes.market_intelligence import market_intelligence_node
from ai_service.app.nodes.scheme_recommendation import scheme_recommendation_node
from ai_service.app.nodes.pest_detection import pest_detection_node
from ai_service.app.nodes.image_upload import image_upload_node
from ai_service.app.nodes.human_intervention import human_intervention_node
from ai_service.app.nodes.manual_review import manual_review_node
from ai_service.app.nodes.summary_node import summary_node
from ai_service.app.nodes.observability import observability_node
from ai_service.app.nodes.data_retrieval_node import data_retrieval_node
from ai_service.app.nodes.data_analysis_node import data_analysis_node

# ── Import routing functions ─────────────────────────────────────────────────
from ai_service.app.graph.routing import (
    route_after_intent,
    route_after_validation,
    route_after_agent,
    # route_after_intervention removed: human_intervention now ends the turn
    # (sets final_response + pending_action) and flows to memory_persist.
)

logger = logging.getLogger(__name__)


def build_graph(checkpointer=None) -> StateGraph:
    """
    Build the FasalSaathi LangGraph pipeline.

    Returns compiled graph ready for .invoke() or .ainvoke().
    """
    graph = StateGraph(FasalSaathiState)

    # ── Register all nodes ───────────────────────────────────────────────
    graph.add_node("memory_retrieve", memory_retrieve_node)
    graph.add_node("intent_router", intent_router_node)
    graph.add_node("greeting", greeting_node)
    graph.add_node("conversational", conversational_node)
    graph.add_node("context_retrieval", context_retrieval_node)
    graph.add_node("planner", planner_node)
    graph.add_node("validator", validator_node)
    graph.add_node("crop_recommendation", crop_recommendation_node)
    graph.add_node("market_intelligence", market_intelligence_node)
    graph.add_node("scheme_recommendation", scheme_recommendation_node)
    graph.add_node("pest_detection", pest_detection_node)
    graph.add_node("image_upload", image_upload_node)
    graph.add_node("human_intervention", human_intervention_node)
    graph.add_node("manual_review", manual_review_node)
    graph.add_node("summary", summary_node)
    graph.add_node("memory_persist", memory_persist_node)
    graph.add_node("observability", observability_node)
    graph.add_node("data_retrieval", data_retrieval_node)
    graph.add_node("data_analysis", data_analysis_node)

    # ── Edges ─────────────────────────────────────────────────────────────

    # START → memory_retrieve → intent_router
    graph.add_edge(START, "memory_retrieve")
    graph.add_edge("memory_retrieve", "intent_router")

    # intent_router → {greeting, data_retrieval, data_analysis, conversational, context_retrieval, planner}
    graph.add_conditional_edges(
        "intent_router",
        route_after_intent,
        {
            "greeting": "greeting",
            "data_retrieval": "data_retrieval",
            "data_analysis": "data_analysis",
            "conversational": "conversational",
            "context_retrieval": "context_retrieval",
            "planner": "planner",
        },
    )

    # greeting → memory_persist → observability → END
    graph.add_edge("greeting", "memory_persist")

    # conversational → memory_persist
    graph.add_edge("conversational", "memory_persist")

    # data_retrieval → memory_persist
    graph.add_edge("data_retrieval", "memory_persist")

    # data_analysis → memory_persist
    graph.add_edge("data_analysis", "memory_persist")

    # context_retrieval → conversational
    graph.add_edge("context_retrieval", "conversational")

    # planner → validator
    graph.add_edge("planner", "validator")

    # validator → {dispatch agents via conditional edges + Send()}
    graph.add_conditional_edges(
        "validator",
        route_after_validation,
        {
            "conversational": "conversational",
            "image_upload": "image_upload",
            "crop_recommendation": "crop_recommendation",
            "market_intelligence": "market_intelligence",
            "scheme_recommendation": "scheme_recommendation",
            "pest_detection": "pest_detection",
        },
    )

    # Each agent → route_after_agent (next group, intervention, or summary)
    for agent_node in [
        "crop_recommendation",
        "market_intelligence",
        "scheme_recommendation",
        "pest_detection",
    ]:
        graph.add_conditional_edges(
            agent_node,
            route_after_agent,
            {
                "crop_recommendation": "crop_recommendation",
                "market_intelligence": "market_intelligence",
                "scheme_recommendation": "scheme_recommendation",
                "pest_detection": "pest_detection",
                "human_intervention": "human_intervention",
                "manual_review": "manual_review",
                "summary": "summary",
            },
        )

    # Bug Fix: image_upload now ends the current turn (returns a final_response
    # asking the farmer for an image) and flows to memory_persist so the state
    # is persisted.  On the NEXT API call for the same session the intent_router
    # detects (uploaded_image_id + pending_action=="waiting_for_image") and
    # re-enters the pest workflow.  The old direct edge to pest_detection would
    # have caused pest_detection to run without any uploaded image.
    graph.add_edge("image_upload", "memory_persist")

    # Bug Fix: human_intervention now ends the turn (sets final_response to the
    # clarification message) instead of looping back to agents via
    # route_after_intervention.  It needs a direct edge to memory_persist so
    # intervention_attempts and final_response are checkpointed before END.
    graph.add_edge("human_intervention", "memory_persist")

    # manual_review → summary
    graph.add_edge("manual_review", "summary")

    # summary → memory_persist
    graph.add_edge("summary", "memory_persist")

    # memory_persist → observability
    graph.add_edge("memory_persist", "observability")

    # observability → END
    graph.add_edge("observability", END)

    # ── Compile ──────────────────────────────────────────────────────────
    if checkpointer is None:
        checkpointer = get_checkpointer()

    compiled = graph.compile(checkpointer=checkpointer)
    logger.info("✅ FasalSaathi graph compiled: %d nodes", len(graph.nodes))

    return compiled


# ── Module-level singleton ───────────────────────────────────────────────────
# Lazy initialized on first call via get_orchestrator()

_compiled_graph = None
_compiled_loop = None


async def get_orchestrator():
    """Get or create the compiled orchestrator graph."""
    global _compiled_graph, _compiled_loop
    import asyncio
    try:
        current_loop = asyncio.get_running_loop()
    except RuntimeError:
        current_loop = None

    if _compiled_graph is None or _compiled_loop != current_loop:
        from ai_service.app.graph.checkpoints import get_async_checkpointer
        checkpointer = await get_async_checkpointer()
        _compiled_graph = build_graph(checkpointer=checkpointer)
        _compiled_loop = current_loop
    return _compiled_graph


