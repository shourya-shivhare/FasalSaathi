from fastapi import APIRouter, HTTPException, Depends, File, Form, UploadFile, Request
import httpx
from typing import Optional
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.api import deps
from backend.app.models.user import User
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.context_builder import ContextBuilder
from backend.app.services.cache_service import CacheService
from backend.app.services.redis_rate_limiter import RedisRateLimiter
from backend.app.utils.cache_keys import make_chat_key

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: Optional[User] = Depends(deps.get_optional_current_user)
):
    """Proxy chat messages to the AI service with enriched farm context."""
    # 1. Enforce Rate Limit (10 chats per minute)
    ip_address = request.client.host if request.client else "127.0.0.1"
    rate_limiter_id = f"user:{current_user.id}" if current_user else f"ip:{ip_address}"
    rate_limit_key = f"rate:chat:{rate_limiter_id}"
    await RedisRateLimiter.check_rate_limit_async(
        rate_limit_key, 10, 60, "Exceeded limit of 10 chat messages per minute."
    )

    url = f"{settings.AI_SERVICE_URL}/api/chat/"
    chat_data = payload.model_dump()
    
    # Enrich context
    if current_user:
        context_obj = ContextBuilder(db).build(current_user)
        if not chat_data.get("context"):
            chat_data["context"] = context_obj.model_dump()

    # 2. Check if caching is eligible (single-turn deterministic queries only)
    is_cacheable = len(payload.messages) == 1 and payload.messages[0].role == "user"
    cache_key = None
    
    if is_cacheable:
        user_id = current_user.id if current_user else 0
        last_message = payload.messages[-1].content
        context = chat_data.get("context")
        language = (current_user.farmer_profile.preferred_language.value if current_user and current_user.farmer_profile and current_user.farmer_profile.preferred_language else "ENGLISH")
        model_version = "gemini-1.5-flash"
        
        cache_key = make_chat_key(user_id, last_message, context, language, model_version)
        cached = await CacheService.get(cache_key)
        if cached is not None:
            return cached

    # 3. Request from AI service
    try:
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            response = await client.post(url, json=chat_data)
            response.raise_for_status()
            res_json = response.json()
            
            # Cache the response if eligible for 30 minutes (1800 seconds)
            if is_cacheable and cache_key:
                await CacheService.set(cache_key, res_json, ttl=1800)
                
            return res_json
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text or f"AI service error: {exc.response.status_code}"
        raise HTTPException(status_code=exc.response.status_code, detail=detail)
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"AI service unavailable — make sure it is running on port 8001. ({type(exc).__name__})",
        )


@router.post("/upload")
async def chat_with_image(
    request: Request,
    message: str = Form(""),
    session_id: str = Form(None),
    state: str = Form(""),
    district: str = Form(""),
    farmer_category: str = Form("marginal"),
    soil_type: str = Form("Loamy"),
    season: str = Form("Kharif"),
    image: UploadFile = File(None),
    db: Session = Depends(deps.get_db),
    current_user: Optional[User] = Depends(deps.get_optional_current_user),
):
    """Proxy multipart chat+image upload to the AI service."""
    # Enforce Rate Limit (10 chats per minute)
    ip_address = request.client.host if request.client else "127.0.0.1"
    rate_limiter_id = f"user:{current_user.id}" if current_user else f"ip:{ip_address}"
    rate_limit_key = f"rate:chat_upload:{rate_limiter_id}"
    await RedisRateLimiter.check_rate_limit_async(
        rate_limit_key, 10, 60, "Exceeded limit of 10 chat messages per minute."
    )
    url = f"{settings.AI_SERVICE_URL}/api/chat/upload"

    if current_user:
        _fp = current_user.farmer_profile
        state = state or (_fp.state if _fp else "") or ""
        district = district or (_fp.district if _fp else "") or ""

    form_data = {
        "message": message,
        "session_id": session_id or "",
        "state": state,
        "district": district,
        "farmer_category": farmer_category,
        "soil_type": soil_type,
        "season": season,
    }

    files = None
    if image and image.filename:
        content = await image.read()
        files = {"image": (image.filename, content, image.content_type or "image/jpeg")}

    try:
        async with httpx.AsyncClient(timeout=90.0, follow_redirects=True) as client:
            resp = await client.post(url, data=form_data, files=files)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"AI service unavailable: {type(exc).__name__}",
        )

