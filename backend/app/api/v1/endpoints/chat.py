from fastapi import APIRouter, HTTPException, Depends
import httpx
from typing import Optional
from app.core.config import settings
from app.api import deps
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    current_user: Optional[User] = Depends(deps.get_optional_current_user)
):
    """Proxy chat messages to the AI service with user context."""
    url = f"{settings.AI_SERVICE_URL}/api/chat/"
    
    # Enrich payload with user profile if logged in
    chat_data = payload.model_dump()
    if current_user:
        user_ctx = {
            "name": current_user.name,
            "state": current_user.state,
            "district": current_user.district,
            "land_size": current_user.land_size_acres,
            "crops": current_user.crops_grown
        }
        # Only set if payload didn't already have one (allow override)
        if not chat_data.get("context"):
            chat_data["context"] = user_ctx

    try:
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            response = await client.post(url, json=chat_data)
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
