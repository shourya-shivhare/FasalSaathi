from fastapi import APIRouter, HTTPException, Depends, File, Form, UploadFile
import httpx
from typing import Optional
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.api import deps
from backend.app.models.user import User
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.context_builder import ContextBuilder

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    db: Session = Depends(deps.get_db),
    current_user: Optional[User] = Depends(deps.get_optional_current_user)
):
    """Proxy chat messages to the AI service with enriched farm context."""
    url = f"{settings.AI_SERVICE_URL}/api/chat/"
    
    chat_data = payload.model_dump()
    if current_user:
        # Use ContextBuilder for rich context instead of manual user_ctx
        context = ContextBuilder(db).build(current_user)
        if not chat_data.get("context"):
            chat_data["context"] = context

    try:
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            response = await client.post(url, json=chat_data)
            response.raise_for_status()
            return response.json()
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

