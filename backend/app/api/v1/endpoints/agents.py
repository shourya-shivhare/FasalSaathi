"""
Agent proxy endpoints.
Forwards requests to the AI service's multi-agent pipeline.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import httpx

from app.core.config import settings
from app.api import deps
from app.models.user import User

router = APIRouter()

TIMEOUT = httpx.Timeout(90.0, connect=10.0)


@router.post("/crop-recommendation")
async def crop_recommendation(
    payload: dict,
    current_user: Optional[User] = Depends(deps.get_optional_current_user),
):
    """Proxy to AI service crop recommendation agent."""
    # Enrich with user profile if logged in
    if current_user:
        payload.setdefault("state", current_user.state or "")
        payload.setdefault("district", current_user.district or "")
        if current_user.land_size_acres:
            payload.setdefault("land_size_acres", current_user.land_size_acres)

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
    current_user: Optional[User] = Depends(deps.get_optional_current_user),
):
    """Proxy to AI service scheme recommendation agent."""
    if current_user:
        payload.setdefault("state", current_user.state or "")
        payload.setdefault("district", current_user.district or "")
        payload.setdefault("farmer_category", current_user.category or "marginal")
        if current_user.crops_grown:
            payload.setdefault("crop_types", current_user.crops_grown.split(","))
        if current_user.annual_income:
            payload.setdefault("annual_income", current_user.annual_income)
        if current_user.gender:
            payload.setdefault("gender", current_user.gender)
        if current_user.age:
            payload.setdefault("age", current_user.age)

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
    current_user: Optional[User] = Depends(deps.get_optional_current_user),
):
    """Proxy to AI service full orchestrator pipeline."""
    if current_user:
        payload.setdefault("state", current_user.state or "")
        payload.setdefault("district", current_user.district or "")
        payload.setdefault("farmer_category", current_user.category or "marginal")
        if current_user.crops_grown:
            payload.setdefault("crop_types", current_user.crops_grown.split(","))
        if current_user.annual_income:
            payload.setdefault("annual_income", current_user.annual_income)
        if current_user.gender:
            payload.setdefault("gender", current_user.gender)
        if current_user.age:
            payload.setdefault("age", current_user.age)
        if current_user.land_size_acres:
            payload.setdefault("land_size_acres", current_user.land_size_acres)

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
