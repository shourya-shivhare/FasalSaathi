"""
Crop Recommendation Node — wraps existing crop_recommendation_agent.
Bridges the LangGraph state to the existing agent's request/response schema.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
import os
import joblib
import numpy as np

from ai_service.app.agents.crop_recommendation_agent import run_crop_recommendation_agent
from ai_service.app.schemas.agent_schemas import CropRecommendationRequest
from ai_service.app.graph.state import FasalSaathiState
from langchain_core.runnables import RunnableConfig

logger = logging.getLogger(__name__)

# Load the model into a global variable
MODEL_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..", "..", "models", "crop_recommendation_model.pkl"
    )
)

try:
    if os.path.exists(MODEL_PATH):
        ml_model = joblib.load(MODEL_PATH)
        logger.info("🤖 Loaded Random Forest crop recommendation model from %s", MODEL_PATH)
    else:
        ml_model = None
        logger.warning("🤖 Crop recommendation model not found at %s", MODEL_PATH)
except Exception as e:
    ml_model = None
    logger.error("🤖 Failed to load Random Forest model: %s", e)



async def crop_recommendation_node(state: FasalSaathiState, config: RunnableConfig) -> dict:
    """
    Run crop recommendation agent with context from graph state.
    Reads pest_detection_result if available (pest → crop dependency).
    """
    start = time.time()
    profile = state.get("farmer_profile", {})

    # Build pest context from upstream pest detection
    pest_context = None
    context_from_agents: dict = {}
    pest_result = state.get("pest_detection_result")
    if pest_result:
        detections = pest_result.get("detections", [])
        if detections:
            pest_names = [d.get("class", "") for d in detections[:5]]
            pest_context = f"Detected pests: {', '.join(pest_names)}"
            context_from_agents["pest_detection"] = pest_context

    # Try running the ML prediction model
    try:
        if ml_model is None:
            raise ValueError("ML Model is not loaded.")
        
        # Extract features from state or farmer_profile fallback
        N = state.get("N")
        if N is None:
            N = profile.get("nitrogen") if profile.get("nitrogen") is not None else profile.get("N")
            
        P = state.get("P")
        if P is None:
            P = profile.get("phosphorus") if profile.get("phosphorus") is not None else profile.get("P")
            
        K = state.get("K")
        if K is None:
            K = profile.get("potassium") if profile.get("potassium") is not None else profile.get("K")
            
        ph = state.get("ph")
        if ph is None:
            ph = profile.get("ph")
            
        temperature = state.get("temperature")
        if temperature is None:
            temperature = profile.get("temperature")
            
        humidity = state.get("humidity")
        if humidity is None:
            humidity = profile.get("humidity")
            
        rainfall = state.get("rainfall")
        if rainfall is None:
            rainfall = profile.get("rainfall")
            
        # Validate that all required features are present
        if any(v is None for v in [N, P, K, temperature, humidity, ph, rainfall]):
            missing = [k for k, v in {
                'N': N, 'P': P, 'K': K, 'temperature': temperature, 
                'humidity': humidity, 'ph': ph, 'rainfall': rainfall
            }.items() if v is None]
            raise ValueError(f"Missing required ML features: {missing}")
            
        # Format features into a 2D NumPy array
        features = np.array([[float(N), float(P), float(K), float(temperature), float(humidity), float(ph), float(rainfall)]])
        
        # Run model prediction
        predicted_crop = ml_model.predict(features)[0]
        logger.info("🤖 ML model predicted crop: %s", predicted_crop)
        
        # Append predicted crop to the context dictionary passed to the LLM agent
        context_from_agents["ml_predicted_crop"] = str(predicted_crop)
        
    except Exception as e:
        logger.warning("🤖 ML prediction failed/skipped (falling back to pure LLM): %s", e)

    try:
        request = CropRecommendationRequest(
            state=profile.get("state", ""),
            district=profile.get("district"),
            soil_type=profile.get("soil_type", "Loamy"),
            season=profile.get("season", "Kharif"),
            water_availability=profile.get("water_availability", "moderate"),
            land_size_acres=profile.get("land_size_acres"),
            past_crops=profile.get("past_crops", []),
            pest_context=pest_context,
            context_from_agents=context_from_agents,
        )

        response = await run_crop_recommendation_agent(request)
        result = response.model_dump()

        # Inject the ML baseline predicted crop if available
        if "ml_predicted_crop" in context_from_agents:
            result["ml_predicted_crop"] = context_from_agents["ml_predicted_crop"]

        # Compute confidence from average crop confidence scores
        crops = result.get("recommended_crops", [])
        avg_conf = (
            sum(c.get("confidence", 0.5) for c in crops) / len(crops)
            if crops else 0.5
        )

        logger.info("🌱 Crop node: %d recommendations, avg_conf=%.2f", len(crops), avg_conf)

        return {
            "crop_recommendations": result,
            "confidence_scores": {"crop": avg_conf},
            "reasoning_steps": [{
                "agent": "crop_recommendation",
                "reasoning": result.get("reasoning_summary", ""),
                "confidence": avg_conf,
            }],
            "graph_path": ["crop_recommendation"],
            "timestamps": {"crop_completed": _now_iso()},
            "execution_trace": [{
                "node": "crop_recommendation", "status": "success",
                "duration_ms": round((time.time() - start) * 1000, 2),
                "tools_used": ["weather_client", "gemini_llm"],
                "reasoning": f"{len(crops)} crops recommended",
                "confidence": avg_conf, "timestamp": _now_iso(),
            }],
        }

    except Exception as e:
        logger.error("Crop recommendation failed: %s", e)
        return {
            "graph_path": ["crop_recommendation"],
            "errors": [{"node": "crop_recommendation", "error": str(e)}],
            "confidence_scores": {"crop": 0.0},
            "execution_trace": [{
                "node": "crop_recommendation", "status": "failed",
                "duration_ms": round((time.time() - start) * 1000, 2),
                "reasoning": f"Error: {e}", "confidence": 0.0,
                "timestamp": _now_iso(),
            }],
        }


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
