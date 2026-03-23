from fastapi import APIRouter
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from app.graphs.crop_advisor_graph import crop_advisor_graph

router = APIRouter()


class AdvisorRequest(BaseModel):
    query: str
    session_id: str | None = None


class AdvisorResponse(BaseModel):
    answer: str


@router.post("/", response_model=AdvisorResponse)
async def crop_advisor(payload: AdvisorRequest):
    initial_state = {
        "messages": [HumanMessage(content=payload.query)],
        "query_type": "",
        "weather_info": "",
        "market_info": "",
        "final_answer": "",
    }
    result = crop_advisor_graph.invoke(initial_state)
    return AdvisorResponse(answer=result["final_answer"])
