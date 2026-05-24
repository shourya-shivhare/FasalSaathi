"""
Market Intelligence Agent
─────────────────────────
Fetches real AGMARKNET mandi prices + OpenWeather data,
analyzes trends, and produces farmer-friendly sell/hold recommendations.

Independently callable via its own router OR via the orchestrator pipeline.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict

from app.core.llm import get_llm, safe_llm_invoke_async
from app.tools.agmarknet_client import fetch_mandi_prices, fetch_nearby_markets
from app.tools.openweather_client import fetch_current_weather, fetch_forecast_5day
from app.tools.trend_analysis import compute_price_trend, compute_market_sentiment
from app.tools.forecasting import predict_short_term, compute_confidence_score
from app.schemas.agent_schemas import (
    MarketIntelligenceRequest,
    MarketIntelligenceResponse,
    MarketLocation,
    CurrentMarketAnalysis,
    NearbyMarket,
)

logger = logging.getLogger(__name__)

# ── LLM Analysis Prompt ─────────────────────────────────────────────────────

MARKET_ANALYSIS_PROMPT = """\
You are an Agricultural Market Intelligence Expert for Indian farmers.

Analyze the following REAL market data and provide a farmer-friendly assessment.

COMMODITY: {commodity}
LOCATION: {state}, {district}

CURRENT MANDI PRICES:
{prices_summary}

PRICE TREND ANALYSIS:
- 7-day trend: {trend_7d}
- Momentum: {momentum_pct}%
- Volatility: {volatility_pct}%
- Average price: ₹{avg_price}/qtl

WEATHER CONDITIONS:
- Current: {weather_desc}, {temp}°C, humidity {humidity}%
- Rain expected (24h): {rain_24h}
- Rain expected (48h): {rain_48h}

SHORT-TERM FORECAST:
- Direction: {forecast_direction}
- Outlook: {forecast_text}

{extra_context}

Based on this data, provide your analysis as JSON:
{{
  "weather_impact": "1-2 sentences on how weather affects the market",
  "arrival_analysis": "1-2 sentences on crop arrivals and supply",
  "selling_recommendation": "Clear actionable advice — sell now / wait / monitor",
  "risk_level": "LOW or MODERATE or HIGH",
  "short_term_outlook": "1-2 sentences on expected price movement",
  "reasoning": ["reason 1", "reason 2", "reason 3"]
}}

Rules:
- ONLY reference the data provided above
- Keep language simple and farmer-friendly
- Never guarantee profits
- Mention uncertainty if volatility is high
- Return ONLY the JSON, no other text
"""


def _build_prices_summary(records: list[dict]) -> str:
    """Format AGMARKNET records into a readable summary for the LLM prompt."""
    if not records:
        return "No price data available."
    lines = []
    for r in records[:8]:
        lines.append(
            f"  • {r.get('market', 'Unknown')} ({r.get('district', '')}): "
            f"₹{r.get('modal_price', 'N/A')}/qtl "
            f"(Min: ₹{r.get('min_price', 'N/A')}, Max: ₹{r.get('max_price', 'N/A')}) "
            f"— {r.get('arrival_date', '')}"
        )
    return "\n".join(lines)


def _parse_llm_json(raw: str) -> dict | None:
    """Extract JSON from LLM response, handling markdown code fences."""
    # Try to extract JSON from code fences
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if match:
        raw = match.group(1)
    # Try direct parse
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Try to find JSON object in the response
        match = re.search(r"\{[^{}]*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return None


def _build_fallback_analysis(
    trend_data: dict,
    weather_data: dict,
    forecast_data: dict,
    weather_current: dict,
) -> dict:
    """Build analysis fields from raw data when LLM is unavailable."""
    trend_7d = trend_data.get("trend_7d", "stable")
    volatility = trend_data.get("volatility_pct", 0)
    desc = weather_current.get("description", "Clear")
    rain_48h = weather_data.get("rain_expected_48h", False)
    rainfall_mm = weather_data.get("rainfall_mm_48h", 0)

    # Weather impact
    if rain_48h and rainfall_mm > 10:
        weather_impact = (
            f"Weather shows {desc}. Rainfall of {rainfall_mm:.0f}mm expected in 48 hours "
            "which may delay transport and reduce market arrivals."
        )
    else:
        weather_impact = (
            f"Weather shows {desc}. No significant weather disruptions expected for market operations."
        )

    # Arrival analysis
    arrival_analysis = (
        "Arrival data is based on available mandi records. "
        "Multiple markets reporting suggests normal supply flow."
    )

    # Selling recommendation
    if trend_7d == "rising":
        selling_rec = "Prices are trending upward. You may want to hold for a few more days if storage is available."
    elif trend_7d == "falling":
        selling_rec = "Prices are declining. Consider selling soon to avoid further price drops."
    else:
        selling_rec = "Prices are stable. Selling at current rates is a reasonable option."

    # Risk level
    if volatility > 15:
        risk_level = "HIGH"
    elif volatility > 8:
        risk_level = "MODERATE"
    else:
        risk_level = "LOW"

    return {
        "weather_impact": weather_impact,
        "arrival_analysis": arrival_analysis,
        "selling_recommendation": selling_rec,
        "risk_level": risk_level,
        "short_term_outlook": forecast_data.get("outlook_text", "Market conditions appear stable."),
        "reasoning": forecast_data.get("factors", ["Based on available market data."]),
    }


# ── Main Agent Function ─────────────────────────────────────────────────────

async def run_market_intelligence_agent(
    request: MarketIntelligenceRequest,
) -> MarketIntelligenceResponse:
    """
    Run the full market intelligence analysis pipeline.

    Steps:
      1. Fetch mandi prices from AGMARKNET
      2. Fetch nearby markets for comparison
      3. Fetch weather data from OpenWeather
      4. Compute price trends and sentiment
      5. Generate short-term forecast
      6. Send to LLM for farmer-friendly analysis
      7. Build and return structured response
    """
    commodity = request.commodity
    state = request.state
    district = request.district or ""
    market = request.market

    logger.info("🏪 Market Intelligence Agent: %s in %s, %s", commodity, state, district)

    # ── Step 1 & 2: Fetch market data ────────────────────────────────────
    records = await fetch_mandi_prices(commodity, state, district, market)
    nearby = await fetch_nearby_markets(commodity, state)

    # ── Step 3: Fetch weather data ───────────────────────────────────────
    weather_city = district if district else state
    weather_current = await fetch_current_weather(weather_city)
    weather_forecast = await fetch_forecast_5day(weather_city)

    # ── Step 4: Compute trends ───────────────────────────────────────────
    trend_data = compute_price_trend(records)

    # Determine weather risk level for sentiment
    rainfall = weather_forecast.get("rainfall_mm_48h", 0)
    if rainfall > 20:
        weather_risk = "high"
    elif rainfall > 5:
        weather_risk = "moderate"
    else:
        weather_risk = "low"

    sentiment = compute_market_sentiment(
        trend_data.get("trend_7d", "stable"),
        trend_data.get("volatility_pct", 0),
        weather_risk,
    )

    # ── Step 5: Forecast ─────────────────────────────────────────────────
    forecast = predict_short_term(trend_data, weather_forecast, records)
    confidence = compute_confidence_score(trend_data, weather_forecast)

    # ── Step 6: LLM Analysis ─────────────────────────────────────────────
    prices_summary = _build_prices_summary(records)
    extra_context = ""
    if not records:
        extra_context = "NOTE: No price records were found. Provide a cautious assessment."

    prompt_text = MARKET_ANALYSIS_PROMPT.format(
        commodity=commodity,
        state=state,
        district=district or "N/A",
        prices_summary=prices_summary,
        trend_7d=trend_data.get("trend_7d", "stable"),
        momentum_pct=trend_data.get("momentum_pct", 0),
        volatility_pct=trend_data.get("volatility_pct", 0),
        avg_price=trend_data.get("avg_price", 0),
        weather_desc=weather_current.get("description", "Clear"),
        temp=weather_current.get("temp", 30),
        humidity=weather_current.get("humidity", 50),
        rain_24h="Yes" if weather_forecast.get("rain_expected_24h") else "No",
        rain_48h="Yes" if weather_forecast.get("rain_expected_48h") else "No",
        forecast_direction=forecast.get("direction", "stable"),
        forecast_text=forecast.get("outlook_text", "No forecast available."),
        extra_context=extra_context,
    )

    llm = get_llm(temperature=0.2)
    llm_raw = await safe_llm_invoke_async(
        llm, prompt_text,
        fallback="LLM_FALLBACK",
    )

    # Parse LLM response or use fallback
    llm_analysis = None
    if llm_raw != "LLM_FALLBACK":
        llm_analysis = _parse_llm_json(llm_raw)

    if llm_analysis is None:
        logger.warning("LLM analysis unavailable — using fallback logic")
        llm_analysis = _build_fallback_analysis(
            trend_data, weather_forecast, forecast, weather_current
        )

    # ── Step 7: Build response ───────────────────────────────────────────
    # Determine best price record for the hero card
    best_record = records[0] if records else {}

    # Build nearby markets list
    nearby_list = []
    for n in nearby[:5]:
        try:
            nearby_list.append(NearbyMarket(
                market_name=n.get("market", "Unknown"),
                district=n.get("district", ""),
                modal_price=int(n.get("modal_price", 0)),
                min_price=int(n.get("min_price", 0)),
                max_price=int(n.get("max_price", 0)),
            ))
        except (ValueError, TypeError):
            continue

    response = MarketIntelligenceResponse(
        commodity=commodity,
        location=MarketLocation(
            state=state,
            district=best_record.get("district", district),
            market=best_record.get("market", ""),
        ),
        current_market_analysis=CurrentMarketAnalysis(
            modal_price=f"₹{trend_data.get('avg_price', 0)}/qtl",
            min_price=f"₹{trend_data.get('min_price', 0)}/qtl",
            max_price=f"₹{trend_data.get('max_price', 0)}/qtl",
            price_trend=trend_data.get("trend_7d", "stable"),
            market_sentiment=sentiment,
        ),
        weather_impact=llm_analysis.get("weather_impact", "Weather data unavailable."),
        arrival_analysis=llm_analysis.get("arrival_analysis", "Arrival data unavailable."),
        selling_recommendation=llm_analysis.get(
            "selling_recommendation", "Unable to generate recommendation at this time."
        ),
        risk_level=llm_analysis.get("risk_level", "MODERATE"),
        short_term_outlook=llm_analysis.get(
            "short_term_outlook", forecast.get("outlook_text", "No outlook available.")
        ),
        reasoning=llm_analysis.get("reasoning", ["Analysis based on available data."]),
        confidence_score=confidence,
        nearby_markets=nearby_list,
    )

    logger.info(
        "🏪 Market Agent complete: %s @ %s, sentiment=%s, confidence=%.2f",
        commodity,
        response.current_market_analysis.modal_price,
        sentiment,
        confidence,
    )

    return response
