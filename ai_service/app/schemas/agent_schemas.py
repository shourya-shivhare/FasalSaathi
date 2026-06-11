"""
Pydantic schemas for the multi-agent pipeline.

Covers:
  - SchemeRecommendationRequest / Response
  - CropRecommendationRequest  / Response
  - AgentPipelineRequest       / Response  (orchestrator)
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════════════════
# SCHEME RECOMMENDATION
# ═══════════════════════════════════════════════════════════════════════════════

class SchemeRecommendationRequest(BaseModel):
    """Input for the Government Scheme Recommendation Agent."""
    user_id: Optional[str] = None
    state: str = Field(..., description="Indian state, e.g. 'Uttar Pradesh'")
    district: Optional[str] = None
    farmer_category: str = Field(
        "marginal",
        description="marginal | small | semi-medium | medium | large"
    )
    crop_types: List[str] = Field(default_factory=list)
    annual_income: Optional[int] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    language_preference: str = "en"
    context_from_agents: Dict[str, Any] = Field(
        default_factory=dict,
        description="Context injected by the orchestrator from upstream agents"
    )


class MatchedScheme(BaseModel):
    """A single scheme matched for the farmer."""
    scheme_name: str
    ministry: str
    eligibility_score: float = Field(
        ..., ge=0.0, le=1.0,
        description="0.0–1.0 confidence that the farmer qualifies"
    )
    benefits: str
    why_recommended: str = Field(
        ..., description="LLM-generated plain-language explanation"
    )
    apply_url: str = ""
    category_tags: List[str] = Field(default_factory=list)


class SchemeRecommendationResponse(BaseModel):
    """Output from the Scheme Recommendation Agent."""
    matched_schemes: List[MatchedScheme]
    total_found: int
    farmer_summary: str = Field(
        ..., description="Brief profile recap used for matching"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CROP RECOMMENDATION
# ═══════════════════════════════════════════════════════════════════════════════

class CropRecommendationRequest(BaseModel):
    """Input for the Crop Recommendation Agent."""
    state: str = Field(..., description="Indian state")
    district: Optional[str] = None
    soil_type: str = Field("Loamy", description="e.g. Loamy, Clayey, Sandy, Alluvial")
    season: str = Field("Kharif", description="Kharif | Rabi | Zaid")
    water_availability: str = Field(
        "moderate",
        description="low | moderate | high | irrigated"
    )
    land_size_acres: Optional[float] = None
    past_crops: List[str] = Field(default_factory=list)
    pest_context: Optional[str] = Field(
        None,
        description="Pest/disease info from the pest detection agent"
    )
    context_from_agents: Dict[str, Any] = Field(default_factory=dict)


class RecommendedCrop(BaseModel):
    """A single recommended crop."""
    crop_name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    season: str
    reasoning: str
    estimated_yield_per_acre: Optional[str] = None
    water_requirement: Optional[str] = None


class CropRecommendationResponse(BaseModel):
    """Output from the Crop Recommendation Agent."""
    recommended_crops: List[RecommendedCrop]
    reasoning_summary: str
    pest_considerations: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# MARKET INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════════════════

class MarketIntelligenceRequest(BaseModel):
    """Input for the Market Intelligence Agent."""
    commodity: str = Field(..., description="Crop name, e.g. 'Wheat'")
    state: str = Field(..., description="Indian state")
    district: Optional[str] = None
    market: Optional[str] = None


class MarketLocation(BaseModel):
    """Location details for market analysis."""
    state: str
    district: str = ""
    market: str = ""


class CurrentMarketAnalysis(BaseModel):
    """Price snapshot and trend summary."""
    modal_price: str
    min_price: str
    max_price: str
    price_trend: str
    market_sentiment: str


class NearbyMarket(BaseModel):
    """A nearby mandi with its price for comparison."""
    market_name: str
    district: str
    modal_price: int
    min_price: int
    max_price: int


class MarketIntelligenceResponse(BaseModel):
    """Output from the Market Intelligence Agent."""
    commodity: str
    location: MarketLocation
    current_market_analysis: CurrentMarketAnalysis
    weather_impact: str
    arrival_analysis: str
    selling_recommendation: str
    risk_level: str = Field(..., description="LOW / MODERATE / HIGH")
    short_term_outlook: str
    reasoning: List[str]
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    nearby_markets: List[NearbyMarket] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# ORCHESTRATOR — FULL PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

class AgentPipelineRequest(BaseModel):
    """Input for the full agent orchestration pipeline."""
    # Query for dynamic agent routing
    user_query: Optional[str] = Field(None, description="Natural language input to decide which agents to run")
    previous_analysis_context: Optional[Dict[str, Any]] = Field(None, description="Past crops or schemes already generated")

    # User identity
    user_id: Optional[str] = None

    # Location
    state: str = Field(..., description="Indian state")
    district: Optional[str] = None

    # Farmer profile
    farmer_category: str = "marginal"
    crop_types: List[str] = Field(default_factory=list)
    annual_income: Optional[int] = None
    gender: Optional[str] = None
    age: Optional[int] = None

    # Crop recommendation inputs
    soil_type: str = "Loamy"
    season: str = "Kharif"
    water_availability: str = "moderate"
    land_size_acres: Optional[float] = None
    past_crops: List[str] = Field(default_factory=list)

    # Optional pest context (e.g. from a scan)
    pest_detection_result: Optional[str] = None

    language_preference: str = "en"


class AgentStepResult(BaseModel):
    """Result from one step in the pipeline."""
    agent_name: str
    success: bool
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class AgentPipelineResponse(BaseModel):
    """Unified response from the full orchestration pipeline."""
    pipeline_id: str
    steps: List[AgentStepResult]
    crop_recommendations: Optional[CropRecommendationResponse] = None
    market_analysis: Optional[MarketIntelligenceResponse] = None
    scheme_recommendations: Optional[SchemeRecommendationResponse] = None
    summary: str = Field(
        ..., description="Final natural-language summary for the farmer"
    )

class PlannerResponse(BaseModel):
    """Output from the Planner Agent indicating which agents to execute."""
    agents: List[str]
    priority: List[str]
    reasoning: str

