"""
Agent proxy endpoints.
Forwards requests to the AI service's multi-agent pipeline.
All payloads are enriched with full FarmerContext via ContextBuilder.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import httpx
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.api import deps
from backend.app.models.user import User
from backend.app.services.context_builder import ContextBuilder

router = APIRouter()

TIMEOUT = httpx.Timeout(90.0, connect=10.0)


def _enrich_payload(payload: dict, db: Session, user: User | None) -> dict:
    """Inject ContextBuilder output into agent payload."""
    if user:
        context = ContextBuilder(db).build(user)
        payload.setdefault("context", context)
        # Also set top-level fields agents may expect directly
        payload.setdefault("state", context["profile"].get("state", ""))
        payload.setdefault("district", context["profile"].get("district", ""))
        payload.setdefault("farmer_category", context["profile"].get("category", "marginal"))
        if context["profile"].get("annual_income"):
            payload.setdefault("annual_income", context["profile"]["annual_income"])
        if context["profile"].get("gender"):
            payload.setdefault("gender", context["profile"]["gender"])
        if context["profile"].get("age"):
            payload.setdefault("age", context["profile"]["age"])
        if context["profile"].get("land_size_acres"):
            payload.setdefault("land_size_acres", context["profile"]["land_size_acres"])
        # Provide crop_types from active crops for backward compat
        crop_types = [c["crop_name"] for c in context.get("active_crops", [])]
        if crop_types:
            payload.setdefault("crop_types", crop_types)
    return payload


@router.post("/crop-recommendation")
async def crop_recommendation(
    payload: dict,
    db: Session = Depends(deps.get_db),
    current_user: Optional[User] = Depends(deps.get_optional_current_user),
):
    """Proxy to AI service crop recommendation agent."""
    payload = _enrich_payload(payload, db, current_user)

    url = f"{settings.AI_SERVICE_URL}/api/v1/agents/crop-recommendation"
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {type(exc).__name__}")


@router.post("/scheme-recommendation")
async def scheme_recommendation(
    payload: dict,
    db: Session = Depends(deps.get_db),
    current_user: Optional[User] = Depends(deps.get_optional_current_user),
):
    """Proxy to AI service scheme recommendation agent."""
    payload = _enrich_payload(payload, db, current_user)

    url = f"{settings.AI_SERVICE_URL}/api/v1/agents/scheme-recommendation"
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {type(exc).__name__}")


@router.post("/full-analysis")
async def full_analysis(
    payload: dict,
    db: Session = Depends(deps.get_db),
    current_user: Optional[User] = Depends(deps.get_optional_current_user),
):
    """Proxy to AI service full orchestrator pipeline."""
    payload = _enrich_payload(payload, db, current_user)

    url = f"{settings.AI_SERVICE_URL}/api/v1/agents/full-analysis"
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {type(exc).__name__}")

