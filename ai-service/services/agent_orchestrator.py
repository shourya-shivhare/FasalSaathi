"""
Agent Orchestrator — Sequential Pipeline with Context Sharing
─────────────────────────────────────────────────────────────

Flow:
  User Input
     │
     ▼
  [Pest Context Injection]  (optional, from scan result)
     │
     ▼
  [Crop Recommendation Agent]  ── uses pest context
     │
     ▼
  [Scheme Recommendation Agent] ── uses crop + pest context
     │
     ▼
  Unified Response to User

Each agent receives a shared_context dict and appends its results.
Failures are isolated — if one agent fails, the next still runs.
"""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict

from app.agents.crop_recommendation_agent import run_crop_recommendation_agent
from app.agents.scheme_recommendation_agent import run_scheme_recommendation_agent
from app.agents.planner_agent import run_planner_agent
from app.schemas.agent_schemas import (
    AgentPipelineRequest,
    AgentPipelineResponse,
    AgentStepResult,
    CropRecommendationRequest,
    CropRecommendationResponse,
    SchemeRecommendationRequest,
    SchemeRecommendationResponse,
)

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Central orchestrator that runs agents sequentially,
    passing each agent's output as context to downstream agents.
    """

    async def run_full_pipeline(
        self, request: AgentPipelineRequest
    ) -> AgentPipelineResponse:
        """
        Execute the full agent pipeline:
          1. Pest context injection (passthrough)
          2. Crop Recommendation Agent
          3. Scheme Recommendation Agent
          4. Produce unified summary

        Args:
            request: Full user profile and optional pest detection context.

        Returns:
            AgentPipelineResponse with all step results and unified summary.
        """
        pipeline_id = f"pipeline-{uuid.uuid4().hex[:12]}"
        logger.info("═══ Starting pipeline %s ═══", pipeline_id)

        shared_context: Dict[str, Any] = request.previous_analysis_context.copy() if request.previous_analysis_context else {}
        steps: list[AgentStepResult] = []
        crop_response: CropRecommendationResponse | None = None
        scheme_response: SchemeRecommendationResponse | None = None

        # ── Step 0: Dynamic Agent Planning ───────────────────────────────────
        plan = await run_planner_agent(request.user_query, shared_context)
        steps.append(AgentStepResult(
            agent_name="planner_agent",
            success=True,
            data={"agents_selected": plan.priority, "reasoning": plan.reasoning}
        ))

        # ── Step 1: Pest Context (passthrough from scan, not an LLM call) ────
        if "pest" in plan.agents:
            if request.pest_detection_result:
                shared_context["pest_detection"] = request.pest_detection_result
                steps.append(AgentStepResult(
                    agent_name="pest_context_injection",
                    success=True,
                    data={"pest_info": request.pest_detection_result},
                ))
                logger.info("  ✅ Pest context injected")
            else:
                steps.append(AgentStepResult(
                    agent_name="pest_context_injection",
                    success=True,
                    data={"pest_info": "No pest data provided but pest agent requested"}
                ))

        # ── Step 2: Crop Recommendation Agent ────────────────────────────────
        if "crop" in plan.agents:
            try:
                crop_req = CropRecommendationRequest(
                    state=request.state,
                    district=request.district,
                    soil_type=request.soil_type,
                    season=request.season,
                    water_availability=request.water_availability,
                    land_size_acres=request.land_size_acres,
                    past_crops=request.past_crops,
                    pest_context=request.pest_detection_result,
                    context_from_agents=shared_context,
                )
                crop_response = await run_crop_recommendation_agent(crop_req)

                # Add crop results to shared context for the scheme agent
                shared_context["crop_recommendations"] = ", ".join(
                    [c.crop_name for c in crop_response.recommended_crops]
                )
                shared_context["crop_reasoning"] = crop_response.reasoning_summary

                steps.append(AgentStepResult(
                    agent_name="crop_recommendation_agent",
                    success=True,
                    data={
                        "count": len(crop_response.recommended_crops),
                        "crops": [c.crop_name for c in crop_response.recommended_crops],
                    },
                ))
                logger.info("  ✅ Crop Agent: %d recommendations", len(crop_response.recommended_crops))

            except Exception as e:
                logger.error("  ❌ Crop Agent failed: %s", e)
                steps.append(AgentStepResult(
                    agent_name="crop_recommendation_agent",
                    success=False,
                    error=str(e),
                ))
        else:
            logger.info("  ⏭️ Skipping Crop Agent per Planner decision.")

        # ── Step 3: Scheme Recommendation Agent ──────────────────────────────
        if "scheme" in plan.agents:
            try:
                scheme_req = SchemeRecommendationRequest(
                    user_id=request.user_id,
                    state=request.state,
                    district=request.district,
                    farmer_category=request.farmer_category,
                    crop_types=request.crop_types,
                    annual_income=request.annual_income,
                    gender=request.gender,
                    age=request.age,
                    context_from_agents=shared_context,
                )
                scheme_response = await run_scheme_recommendation_agent(scheme_req)

                steps.append(AgentStepResult(
                    agent_name="scheme_recommendation_agent",
                    success=True,
                    data={
                        "count": scheme_response.total_found,
                        "schemes": [s.scheme_name for s in scheme_response.matched_schemes[:5]],
                    },
                ))
                logger.info("  ✅ Scheme Agent: %d matches", scheme_response.total_found)

            except Exception as e:
                logger.error("  ❌ Scheme Agent failed: %s", e)
                steps.append(AgentStepResult(
                    agent_name="scheme_recommendation_agent",
                    success=False,
                    error=str(e),
                ))
        else:
            logger.info("  ⏭️ Skipping Scheme Agent per Planner decision.")

        # ── Step 4: Build unified summary ────────────────────────────────────
        summary = self._build_summary(request, plan, crop_response, scheme_response)
        logger.info("═══ Pipeline %s complete ═══", pipeline_id)

        return AgentPipelineResponse(
            pipeline_id=pipeline_id,
            steps=steps,
            crop_recommendations=crop_response,
            scheme_recommendations=scheme_response,
            summary=summary,
        )

    # ── Private ───────────────────────────────────────────────────────────────

    @staticmethod
    def _build_summary(
        req: AgentPipelineRequest,
        plan: PlannerResponse,
        crops: CropRecommendationResponse | None,
        schemes: SchemeRecommendationResponse | None,
    ) -> str:
        """Generate a farmer-friendly plain-language summary."""
        parts = [f"Analysis for {req.farmer_category} farmer in {req.state}:"]

        if crops and crops.recommended_crops:
            crop_names = ", ".join(c.crop_name for c in crops.recommended_crops[:3])
            parts.append(
                f"🌱 Top crop suggestions for {req.season} season: {crop_names}."
            )
        elif "crop" not in plan.agents:
            parts.append("🌱 Crop recommendations were not requested.")
        else:
            parts.append("🌱 Crop recommendations could not be generated at this time.")

        if schemes and schemes.matched_schemes:
            scheme_names = ", ".join(s.scheme_name for s in schemes.matched_schemes[:3])
            parts.append(
                f"🏛️ You may be eligible for: {scheme_names}."
            )
        elif "scheme" not in plan.agents:
            parts.append("🏛️ Scheme suggestions were not targeted by your query.")
        else:
            parts.append("🏛️ Scheme recommendations could not be generated at this time.")

        if req.pest_detection_result:
            parts.append(f"🐛 Pest context considered: {req.pest_detection_result}")

        return " ".join(parts)


# Singleton orchestrator instance
orchestrator = AgentOrchestrator()
