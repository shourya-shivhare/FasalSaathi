"""
Market Intelligence proxy endpoints.
Forwards requests to the AI service's market intelligence agent.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
import httpx

from app.core.config import settings
from app.api import deps
from app.models.user import User

router = APIRouter()

TIMEOUT = httpx.Timeout(90.0, connect=10.0)


@router.post("/analysis")
async def market_analysis(
    payload: dict,
    current_user: Optional[User] = Depends(deps.get_optional_current_user),
):
    """Proxy to AI service market intelligence agent."""
    # Enrich with user profile if logged in
    if current_user:
        payload.setdefault("state", current_user.state or "")
        payload.setdefault("district", current_user.district or "")

    url = f"{settings.AI_SERVICE_URL}/api/v1/market/analysis"
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {type(exc).__name__}")


@router.get("/prices")
async def raw_prices(
    commodity: str = Query(..., description="Crop name"),
    state: str = Query(None, description="Indian state filter"),
    district: str = Query(None, description="District filter"),
    limit: int = Query(20, le=50),
):
    """Proxy to AI service raw mandi prices."""
    params = {"commodity": commodity, "limit": limit}
    if state:
        params["state"] = state
    if district:
        params["district"] = district

    url = f"{settings.AI_SERVICE_URL}/api/v1/market/prices"
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {type(exc).__name__}")
