"""
Market Intelligence REST Endpoints
───────────────────────────────────
Exposes AGMARKNET data + trend analysis as REST endpoints,
consumed by the FastAPI backend proxy (backend/app/api/v1/endpoints/market.py).

Routes:
  POST /analysis  — AI-enriched market analysis for a commodity
  GET  /prices    — Raw mandi price records
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from ai_service.app.tools.agmarknet_client import fetch_mandi_prices, fetch_nearby_markets
from ai_service.app.tools.trend_analysis import (
    compute_price_trend,
    compute_moving_averages,
    compute_market_sentiment,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Request / Response models ────────────────────────────────────────────────

class AnalysisRequest(BaseModel):
    commodity: str = "Wheat"
    state: Optional[str] = None
    district: Optional[str] = None


# ── POST /analysis ───────────────────────────────────────────────────────────

@router.post("/analysis")
async def market_analysis(req: AnalysisRequest):
    """
    Return AI-enriched market analysis for a commodity.
    Combines live AGMARKNET data with trend + sentiment analysis.
    """
    commodity = req.commodity
    state = req.state or None
    district = req.district or None

    # 1. Fetch raw price records
    records = await fetch_mandi_prices(commodity, state=state, district=district, limit=50)

    # 2. Compute analytics
    trend = compute_price_trend(records)
    moving_avgs = compute_moving_averages(records)
    sentiment = compute_market_sentiment(
        trend.get("trend_7d", "stable"),
        trend.get("volatility_pct", 0.0),
    )

    # 3. Fetch nearby markets for comparison
    nearby = []
    if state:
        try:
            nearby_records = await fetch_nearby_markets(commodity, state, limit=8)
            nearby = [
                {
                    "market_name": r.get("market", "Unknown"),
                    "district": r.get("district", ""),
                    "modal_price": int(r.get("modal_price", 0)),
                    "min_price": int(r.get("min_price", 0)),
                    "max_price": int(r.get("max_price", 0)),
                }
                for r in nearby_records
            ]
        except Exception as e:
            logger.warning("Nearby markets fetch failed: %s", e)

    # 4. Build current market analysis summary
    latest = records[0] if records else {}
    modal_price = int(latest.get("modal_price", 0))
    min_price = int(latest.get("min_price", 0))
    max_price = int(latest.get("max_price", 0))

    # Determine price trend label
    price_trend = trend.get("trend_7d", "stable")

    # Build selling recommendation
    if sentiment == "bullish":
        selling_rec = f"Market is bullish for {commodity}. Consider selling at current prices for good returns."
    elif sentiment == "bearish":
        selling_rec = f"Market is bearish for {commodity}. Consider holding stock if storage is available."
    elif sentiment == "volatile":
        selling_rec = f"Market is volatile for {commodity}. Sell in small batches to manage risk."
    else:
        selling_rec = f"Market is stable for {commodity}. Current prices are fair for selling."

    # Short-term outlook
    momentum = trend.get("momentum_pct", 0)
    if momentum > 3:
        outlook = f"Prices have risen {momentum}% recently. Upward momentum may continue short-term."
    elif momentum < -3:
        outlook = f"Prices have dropped {abs(momentum)}% recently. Watch for further dips before selling."
    else:
        outlook = "Prices are relatively stable. No major changes expected in the near term."

    # Confidence score based on data points
    data_points = trend.get("data_points", 0)
    if data_points >= 20:
        confidence = 0.85
    elif data_points >= 10:
        confidence = 0.70
    elif data_points >= 3:
        confidence = 0.55
    else:
        confidence = 0.35

    # Risk level
    volatility = trend.get("volatility_pct", 0)
    if volatility > 15:
        risk_level = "HIGH"
    elif volatility > 8:
        risk_level = "MODERATE"
    else:
        risk_level = "LOW"

    # Reasoning
    reasoning = []
    reasoning.append(f"Based on {data_points} price data points from AGMARKNET")
    if price_trend == "rising":
        reasoning.append("Prices show an upward trend in the last 7 days")
    elif price_trend == "falling":
        reasoning.append("Prices show a downward trend in the last 7 days")
    else:
        reasoning.append("Prices have been stable in the last 7 days")

    if volatility > 10:
        reasoning.append(f"High volatility ({volatility}%) indicates price uncertainty")
    elif volatility > 5:
        reasoning.append(f"Moderate volatility ({volatility}%) — some price fluctuation expected")
    else:
        reasoning.append("Low volatility indicates predictable pricing")

    if nearby:
        best_price = max(m["modal_price"] for m in nearby)
        reasoning.append(f"Best nearby market price: ₹{best_price}/quintal")

    return {
        "commodity": commodity,
        "location": {
            "state": state or "India",
            "market": district or (latest.get("market", "")),
            "district": district or (latest.get("district", "")),
        },
        "current_market_analysis": {
            "modal_price": f"₹{modal_price:,}",
            "min_price": f"₹{min_price:,}",
            "max_price": f"₹{max_price:,}",
            "price_trend": price_trend,
            "market_sentiment": sentiment,
        },
        "trend": trend,
        "moving_averages": moving_avgs,
        "nearby_markets": nearby,
        "selling_recommendation": selling_rec,
        "short_term_outlook": outlook,
        "weather_impact": "Weather data not yet integrated — no impact estimated.",
        "confidence_score": confidence,
        "risk_level": risk_level,
        "reasoning": reasoning,
    }


# ── GET /prices ──────────────────────────────────────────────────────────────

@router.get("/prices")
async def raw_prices(
    commodity: str = Query(..., description="Crop name"),
    state: Optional[str] = Query(None, description="Indian state filter"),
    district: Optional[str] = Query(None, description="District filter"),
    limit: int = Query(20, le=50),
):
    """Return raw AGMARKNET mandi price records."""
    records = await fetch_mandi_prices(
        commodity, state=state, district=district, limit=limit
    )
    return {
        "commodity": commodity,
        "count": len(records),
        "records": records,
    }
