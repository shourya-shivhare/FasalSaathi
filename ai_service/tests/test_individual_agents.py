from types import SimpleNamespace

import pytest
from langgraph.checkpoint.memory import MemorySaver

from ai_service.app.graph.orchestrator import build_graph
from ai_service.app.graph import planner
from ai_service.app.graph import intent_router
from ai_service.app.nodes import crop_recommendation, market_intelligence
from ai_service.app.nodes import pest_detection, scheme_recommendation
from ai_service.app.nodes import summary_node
from ai_service.app.schemas.agent_schemas import (
    CropRecommendationResponse,
    MarketIntelligenceResponse,
    SchemeRecommendationResponse,
)


@pytest.mark.asyncio
async def test_crop_node_calls_agent_with_profile_context(monkeypatch):
    captured = {}

    async def fake_agent(request):
        captured["request"] = request
        return CropRecommendationResponse(
            recommended_crops=[{
                "crop_name": "Mustard",
                "confidence": 0.86,
                "season": "Rabi",
                "reasoning": "Suitable for the supplied conditions.",
            }],
            reasoning_summary="One crop selected.",
        )

    monkeypatch.setattr(crop_recommendation, "run_crop_recommendation_agent", fake_agent)
    result = await crop_recommendation.crop_recommendation_node({
        "farmer_profile": {
            "state": "Punjab",
            "district": "Amritsar",
            "soil_type": "LOAMY",
            "season": "Rabi",
            "water_availability": "irrigated",
            "land_size_acres": 5.0,
            "past_crops": ["Rice"],
        }
    }, {})

    assert captured["request"].past_crops == ["Rice"]
    assert result["crop_recommendations"]["recommended_crops"][0]["crop_name"] == "Mustard"


@pytest.mark.asyncio
async def test_market_node_calls_agent_and_returns_result(monkeypatch):
    async def fake_agent(request):
        assert request.commodity == "Rice"
        return MarketIntelligenceResponse(
            commodity="Rice",
            location={"state": "Punjab", "district": "Amritsar"},
            current_market_analysis={
                "modal_price": "Rs 3000/qtl", "min_price": "Rs 2800/qtl",
                "max_price": "Rs 3200/qtl", "price_trend": "stable",
                "market_sentiment": "neutral",
            },
            weather_impact="Low impact.", arrival_analysis="Normal arrivals.",
            selling_recommendation="Monitor prices.", risk_level="LOW",
            short_term_outlook="Stable.", reasoning=["Stable records."],
            confidence_score=0.8,
        )

    monkeypatch.setattr(market_intelligence, "run_market_intelligence_agent", fake_agent)
    result = await market_intelligence.market_intelligence_node({
        "user_query": "What is the rice price?",
        "farmer_profile": {"state": "Punjab", "district": "Amritsar"},
    }, {})

    assert result["market_analysis"]["commodity"] == "Rice"
    assert result["confidence_scores"]["market"] == 0.8


@pytest.mark.asyncio
async def test_scheme_node_passes_crop_results_to_agent(monkeypatch):
    captured = {}

    async def fake_agent(request):
        captured["request"] = request
        return SchemeRecommendationResponse(
            matched_schemes=[], total_found=0, farmer_summary="Test farmer."
        )

    monkeypatch.setattr(scheme_recommendation, "run_scheme_recommendation_agent", fake_agent)
    result = await scheme_recommendation.scheme_recommendation_node({
        "farmer_profile": {"state": "Punjab", "crop_types": ["Rice"]},
        "crop_recommendations": {
            "recommended_crops": [{"crop_name": "Wheat"}],
        },
    }, {})

    assert captured["request"].crop_types == ["Rice", "Wheat"]
    assert result["scheme_recommendations"]["total_found"] == 0


@pytest.mark.asyncio
async def test_pest_node_uses_image_store_and_cleans_up(monkeypatch):
    class ImageStore:
        deleted = False

        async def get(self, image_id):
            assert image_id == "image-1"
            return b"image"

        async def delete(self, image_id):
            self.deleted = True

    image_store = ImageStore()
    registry = SimpleNamespace(
        image_store=image_store,
        pest_map=SimpleNamespace(get_full_pest_info=lambda name, confidence: {
            "severity": "Medium", "suggestions": ["Inspect the crop"],
        }),
    )

    async def fake_inference(image_bytes):
        return {
            "detection_count": 1,
            "detections": [{"class": "aphid", "confidence": 0.9}],
        }

    monkeypatch.setattr(pest_detection, "_run_yolo_inference", fake_inference)
    result = await pest_detection.pest_detection_node(
        {"uploaded_image_id": "image-1"},
        {"configurable": {"runtime": SimpleNamespace(tool_registry=registry)}},
    )

    assert result["pest_detection_result"]["detections"][0]["severity"] == "Medium"
    assert image_store.deleted is True


@pytest.mark.asyncio
async def test_planner_llm_failure_runs_known_sub_intent(monkeypatch):
    monkeypatch.setattr(planner, "get_llm", lambda **kwargs: object())

    async def fail_to_fallback(*args, **kwargs):
        return "__PLANNER_FALLBACK__"

    monkeypatch.setattr(planner, "safe_llm_invoke_async", fail_to_fallback)
    result = await planner.planner_node({
        "user_query": "Recommend a crop",
        "sub_intents": ["crop"],
        "farmer_profile": {},
        "memory_context": {},
    }, {})

    assert isinstance(result, dict)
    assert result["planner_output"]["agents"] == ["crop"]
    assert result["planner_output"]["confidence"] == 0.8


def test_orchestrator_compiles_with_registered_agents():
    graph = build_graph(checkpointer=MemorySaver()).get_graph()
    for node in (
        "crop_recommendation", "market_intelligence", "scheme_recommendation",
        "pest_detection", "data_retrieval", "data_analysis",
    ):
        assert node in graph.nodes


@pytest.mark.asyncio
async def test_agents_run_through_parallel_and_sequential_graph(monkeypatch):
    async def classify(*args, **kwargs):
        return '{"intent":"workflow","sub_intents":["crop","market","scheme"],"confidence":0.95}'

    async def plan(*args, **kwargs):
        return (
            '{"agents":["crop","market","scheme"],"execution_hints":'
            '{"parallel":[["crop","market"]],"priority":'
            '{"crop":1,"market":1,"scheme":2}},"requires_image":false,'
            '"reasoning":"combined request",'
            '"confidence":0.95}'
        )

    async def present(*args, **kwargs):
        return "Grow mustard based on the supplied farm conditions."

    async def fake_crop_agent(request):
        return CropRecommendationResponse(
            recommended_crops=[{
                "crop_name": "Mustard", "confidence": 0.9,
                "season": "Rabi", "reasoning": "Matches conditions.",
            }],
            reasoning_summary="Mustard is suitable.",
        )

    async def fake_market_agent(request):
        return MarketIntelligenceResponse(
            commodity=request.commodity,
            location={"state": request.state},
            current_market_analysis={
                "modal_price": "Rs 3000/qtl", "min_price": "Rs 2800/qtl",
                "max_price": "Rs 3200/qtl", "price_trend": "stable",
                "market_sentiment": "neutral",
            },
            weather_impact="Low.", arrival_analysis="Normal.",
            selling_recommendation="Monitor.", risk_level="LOW",
            short_term_outlook="Stable.", reasoning=["Stable."],
            confidence_score=0.8,
        )

    async def fake_scheme_agent(request):
        return SchemeRecommendationResponse(
            matched_schemes=[], total_found=0, farmer_summary="Test farmer."
        )

    class MemoryStore:
        async def retrieve(self, user_id):
            return {}

        async def persist(self, user_id, data):
            return None

    monkeypatch.setattr(intent_router, "get_llm", lambda **kwargs: object())
    monkeypatch.setattr(intent_router, "safe_llm_invoke_async", classify)
    monkeypatch.setattr(planner, "get_llm", lambda **kwargs: object())
    monkeypatch.setattr(planner, "safe_llm_invoke_async", plan)
    monkeypatch.setattr(summary_node, "get_llm", lambda **kwargs: object())
    monkeypatch.setattr(summary_node, "safe_llm_invoke_async", present)
    monkeypatch.setattr(crop_recommendation, "run_crop_recommendation_agent", fake_crop_agent)
    monkeypatch.setattr(market_intelligence, "run_market_intelligence_agent", fake_market_agent)
    monkeypatch.setattr(scheme_recommendation, "run_scheme_recommendation_agent", fake_scheme_agent)

    graph = build_graph(checkpointer=MemorySaver())
    runtime = SimpleNamespace(
        tool_registry=SimpleNamespace(memory_store=MemoryStore())
    )
    result = await graph.ainvoke({
        "user_query": "What should I grow?",
        "farmer_profile": {
            "user_id": "agent-test", "state": "Punjab",
            "soil_type": "LOAMY", "season": "Rabi",
        },
        "chat_history": [], "messages": [], "reasoning_steps": [],
        "confidence_scores": {}, "execution_trace": [], "graph_path": [],
        "errors": [], "tool_outputs": {}, "timestamps": {},
        "intervention_attempts": {}, "memory_context": {},
    }, config={
        "configurable": {"thread_id": "agent-test", "runtime": runtime},
    })

    assert result["crop_recommendations"]["recommended_crops"][0]["crop_name"] == "Mustard"
    assert result["market_analysis"]["confidence_score"] == 0.8
    assert result["scheme_recommendations"]["total_found"] == 0
    assert result["final_response"].startswith("Grow mustard")
    assert "observability" in result["graph_path"]
