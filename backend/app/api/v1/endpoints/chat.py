from fastapi import APIRouter, HTTPException
import httpx
from app.core.config import settings
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    """Proxy chat messages to the AI service (LangChain / Gemini)."""
    # ai-service mounts the chat router at /api/chat — note trailing slash
    url = f"{settings.AI_SERVICE_URL}/api/chat/"
    try:
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            response = await client.post(
                url,
                json=payload.model_dump(),
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        # Surface the actual error from the ai-service
        detail = exc.response.text or f"AI service error: {exc.response.status_code}"
        raise HTTPException(status_code=exc.response.status_code, detail=detail)
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"AI service unavailable — make sure it is running on port 8001. ({type(exc).__name__})",
        )
