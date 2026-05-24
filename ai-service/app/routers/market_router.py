"""
Market Intelligence Router
──────────────────────────
Endpoints:
  POST /api/v1/market/analysis  — Full market intelligence report
  GET  /api/v1/market/prices    — Raw mandi prices (no LLM)
"""
from __future__ import annotations

import logging
from fastapi import APIRouter, HTTPException, Query

from app.agents.market_intelligence_agent import run_market_intelligence_agent
from app.tools.agmarknet_client import fetch_mandi_prices
from app.schemas.agent_schemas import (
    MarketIntelligenceRequest,
    MarketIntelligenceResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/analysis",
    response_model=MarketIntelligenceResponse,
    summary="Get full market intelligence analysis",
    description="Fetches live mandi prices, weather data, and produces AI-powered sell/hold recommendation.",
)
async def market_analysis(request: MarketIntelligenceRequest):
    try:
        return await run_market_intelligence_agent(request)
    except Exception as e:
        logger.error("Market analysis endpoint error: %s", e)
        raise HTTPException(status_code=500, detail=f"Market analysis failed: {str(e)}")


@router.get(
    "/prices",
    summary="Get raw mandi prices",
    description="Lightweight endpoint — returns raw AGMARKNET price data without LLM analysis.",
)
async def raw_prices(
    commodity: str = Query(..., description="Crop name, e.g. 'Wheat'"),
    state: str = Query(None, description="Indian state filter"),
    district: str = Query(None, description="District filter"),
    limit: int = Query(20, le=50),
):
    try:
        records = await fetch_mandi_prices(commodity, state, district, limit=limit)
        return {"commodity": commodity, "count": len(records), "records": records}
    except Exception as e:
        logger.error("Raw prices endpoint error: %s", e)
        raise HTTPException(status_code=500, detail=f"Price fetch failed: {str(e)}")
