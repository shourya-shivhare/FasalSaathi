import asyncio

from ai_service.app.graph.routing import route_after_intent
from ai_service.app.nodes.data_analysis_node import data_analysis_node
from ai_service.app.tools.farmer_data_tools import FarmerDataTools


def test_tools_retrieve_actual_records_and_empty_profile_is_empty():
    tools = FarmerDataTools({
        "preferred_language": "ENGLISH",
        "farms": [{"farm_name": "North Plot", "total_area": 4.0}],
        "active_crops": [{"crop_name": "Rice", "status": "ACTIVE"}],
        "pest_history": [{"disease_name": "Blast"}],
    })

    assert tools.list_farms()["data"][0]["farm_name"] == "North Plot"
    assert tools.list_active_crops()["data"][0]["crop_name"] == "Rice"
    assert tools.get_pest_history()["data"][0]["disease_name"] == "Blast"
    assert FarmerDataTools({"preferred_language": "ENGLISH"}).get_farmer_profile()["found"] is False


def test_new_intents_route_to_their_nodes():
    assert route_after_intent({"intent": "data_retrieval"}) == "data_retrieval"
    assert route_after_intent({"intent": "data_analysis"}) == "data_analysis"


def test_analysis_empty_state_does_not_call_llm():
    state = {
        "user_query": "Which farm is largest?",
        "farmer_profile": {
            "farms": [],
            "active_crops": [],
            "crop_history": [],
            "pest_history": [],
            "farm_summary": {"total_farms": 0},
            "season_context": {"current_season": "KHARIF"},
        },
    }

    result = asyncio.run(data_analysis_node(state, {}))

    assert "don't have enough data" in result["final_response"]
    assert result["graph_path"] == ["data_analysis"]
