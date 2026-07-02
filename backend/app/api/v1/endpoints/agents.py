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
        context_obj = ContextBuilder(db).build(user)
        context = context_obj.model_dump()
        payload.setdefault("context", context)
        # Also set top-level fields agents may expect directly
        payload.setdefault("state", context["profile"].get("state") or "")
        payload.setdefault("district", context["profile"].get("district") or "")
        payload.setdefault("farmer_category", context["profile"].get("category") or "marginal")
        if context["profile"].get("annual_income"):
            payload.setdefault("annual_income", context["profile"]["annual_income"])
        if context["profile"].get("gender"):
            payload.setdefault("gender", context["profile"]["gender"])
        if context["profile"].get("age"):
            payload.setdefault("age", context["profile"]["age"])
        
        land_size = context["farm_summary"].get("total_registered_area") or 0.0
        payload.setdefault("land_size_acres", land_size)
        
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

    # Fetch and inject live data.gov.in crop context
    from backend.app.services.context_builder import build_crop_context
    gov_context = build_crop_context(settings.DATA_GOV_API_KEY, settings.DATA_GOV_RESOURCE_ID)
    if gov_context:
        if "context" not in payload:
            payload["context"] = {}
        payload["context"]["data_gov_context"] = gov_context

    from backend.app.services.cache_service import CacheService
    from backend.app.utils.cache_keys import make_crop_recommendation_key
    import hashlib
    import json

    user_id = current_user.id if current_user else 0
    context_data = payload.get("context") or payload
    context_str = json.dumps(context_data, sort_keys=True)
    context_hash = hashlib.md5(context_str.encode("utf-8")).hexdigest()

    cache_key = make_crop_recommendation_key(user_id, context_hash)
    cached = await CacheService.get(cache_key)
    if cached is not None:
        return cached

    url = f"{settings.AI_SERVICE_URL}/api/v1/agents/crop-recommendation"
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            res_json = resp.json()
            # Cache for 6 hours (21600 seconds)
            await CacheService.set(cache_key, res_json, ttl=21600)
            return res_json
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

    from backend.app.services.cache_service import CacheService
    from backend.app.utils.cache_keys import make_scheme_recommendation_key
    import hashlib
    import json

    user_id = current_user.id if current_user else 0
    context_data = payload.get("context") or payload
    context_str = json.dumps(context_data, sort_keys=True)
    context_hash = hashlib.md5(context_str.encode("utf-8")).hexdigest()

    cache_key = make_scheme_recommendation_key(user_id, context_hash)
    cached = await CacheService.get(cache_key)
    if cached is not None:
        return cached

    url = f"{settings.AI_SERVICE_URL}/api/v1/agents/scheme-recommendation"
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            res_json = resp.json()
            # Cache for 24 hours (86400 seconds)
            await CacheService.set(cache_key, res_json, ttl=86400)
            return res_json
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

