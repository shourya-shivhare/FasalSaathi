"""
Orchestrator Router
───────────────────
Exposes three endpoints:
  POST /api/v1/agents/crop-recommendation
  POST /api/v1/agents/scheme-recommendation
  POST /api/v1/agents/full-analysis  (orchestrator pipeline)
"""
from __future__ import annotations

import logging
from fastapi import APIRouter, HTTPException

from app.agents.crop_recommendation_agent import run_crop_recommendation_agent
from app.agents.scheme_recommendation_agent import run_scheme_recommendation_agent
from app.schemas.agent_schemas import (
    AgentPipelineRequest,
    AgentPipelineResponse,
    CropRecommendationRequest,
    CropRecommendationResponse,
    SchemeRecommendationRequest,
    SchemeRecommendationResponse,
)
from services.agent_orchestrator import orchestrator

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Individual Agent Endpoints ────────────────────────────────────────────────

@router.post(
    "/crop-recommendation",
    response_model=CropRecommendationResponse,
    summary="Get AI-powered crop recommendations",
    description="Independently callable crop recommendation agent.",
)
async def crop_recommendation(request: CropRecommendationRequest):
    """Recommend 3-5 best crops based on farmer's land and conditions."""
    try:
        return await run_crop_recommendation_agent(request)
    except Exception as e:
        logger.error("Crop recommendation endpoint error: %s", e)
        raise HTTPException(status_code=500, detail=f"Crop recommendation failed: {str(e)}")


@router.post(
    "/scheme-recommendation",
    response_model=SchemeRecommendationResponse,
    summary="Get government scheme recommendations",
    description="Independently callable scheme recommendation agent.",
)
async def scheme_recommendation(request: SchemeRecommendationRequest):
    """Match farmer profile against 25+ Indian government schemes."""
    try:
        return await run_scheme_recommendation_agent(request)
    except Exception as e:
        logger.error("Scheme recommendation endpoint error: %s", e)
        raise HTTPException(status_code=500, detail=f"Scheme recommendation failed: {str(e)}")


# ── Full Pipeline Endpoint ────────────────────────────────────────────────────

@router.post(
    "/full-analysis",
    response_model=AgentPipelineResponse,
    summary="Run the full agent pipeline",
    description="Runs pest → crop → scheme agents sequentially with shared context.",
)
async def full_analysis(request: AgentPipelineRequest):
    """
    Execute the full orchestrator pipeline:
      1. Inject pest context (if provided)
      2. Crop Recommendation Agent
      3. Scheme Recommendation Agent
      4. Unified summary
    """
    try:
        return await orchestrator.run_full_pipeline(request)
    except Exception as e:
        logger.error("Full analysis pipeline error: %s", e)
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")
