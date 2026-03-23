from fastapi import APIRouter, HTTPException
import httpx
from app.core.config import settings
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    """Proxy chat messages to the AI service (LangChain/LangGraph)."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.AI_SERVICE_URL}/api/chat",
                json=payload.model_dump(),
                timeout=60.0,
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"AI service unavailable: {exc}")
