"""
Forecasting Utilities
─────────────────────
Heuristic-based short-term price outlook for Indian agricultural markets.

Uses rule-based logic combining:
  - Price trend direction
  - Weather disruption risk
  - Arrival volume signals
  - Seasonal patterns

Never claims guaranteed profits — all outputs are clearly labeled as estimates.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def predict_short_term(
    trend_data: dict,
    weather_data: dict,
    records: list[dict] | None = None,
) -> dict:
    """
    Predict short-term price movement using heuristic rules.

    Args:
        trend_data: Output from compute_price_trend()
        weather_data: Output from fetch_forecast_5day()
        records: Raw AGMARKNET records (optional, for arrival analysis)

    Returns:
        {direction: "up"/"down"/"stable", confidence: 0.0-1.0,
         outlook_text: str, factors: list[str]}
    """
    trend_7d = trend_data.get("trend_7d", "stable")
    volatility = trend_data.get("volatility_pct", 0.0)
    momentum = trend_data.get("momentum_pct", 0.0)

    rain_24h = weather_data.get("rain_expected_24h", False)
    rain_48h = weather_data.get("rain_expected_48h", False)
    rainfall_mm = weather_data.get("rainfall_mm_48h", 0.0)

    factors = []
    direction = "stable"
    confidence = 0.6

    # ── Rule 1: Rising trend + no rain disruption ────────────────────────
    if trend_7d == "rising" and not rain_48h:
        direction = "up"
        confidence = 0.75
        factors.append("Prices have been rising over the past week")
        factors.append("No weather disruptions expected")
        outlook = (
            "Prices are likely to remain stable or increase slightly. "
            "This is a reasonable window to sell if you need immediate income."
        )

    # ── Rule 2: Rising trend + heavy rain expected ───────────────────────
    elif trend_7d == "rising" and rainfall_mm > 15:
        direction = "up"
        confidence = 0.7
        factors.append("Prices are already rising")
        factors.append(f"Heavy rain expected ({rainfall_mm:.0f}mm) may disrupt transport")
        factors.append("Reduced arrivals could push prices higher")
        outlook = (
            "Prices may spike further as heavy rainfall could reduce crop arrivals "
            "at mandis. However, this also carries higher uncertainty."
        )

    # ── Rule 3: Rising trend + light rain ────────────────────────────────
    elif trend_7d == "rising" and rain_48h:
        direction = "up"
        confidence = 0.65
        factors.append("Upward price trend continues")
        factors.append("Light rain may cause minor transport delays")
        outlook = (
            "Prices likely to hold or edge up slightly. "
            "Light rain is not expected to significantly impact market supply."
        )

    # ── Rule 4: Falling trend ────────────────────────────────────────────
    elif trend_7d == "falling" and not rain_48h:
        direction = "down"
        confidence = 0.7
        factors.append("Prices have been falling over the past week")
        factors.append("No weather disruptions to slow supply")
        outlook = (
            "Prices may continue to fall as supply remains steady. "
            "Consider selling soon if holding costs are high."
        )

    # ── Rule 5: Falling trend + rain disruption ──────────────────────────
    elif trend_7d == "falling" and rainfall_mm > 10:
        direction = "stable"
        confidence = 0.55
        factors.append("Prices were falling recently")
        factors.append("Rain may reduce new arrivals, potentially slowing the decline")
        outlook = (
            "The falling price trend may stabilize as rain reduces fresh "
            "crop arrivals. Monitor prices closely over the next few days."
        )

    # ── Rule 6: Stable + high volatility ─────────────────────────────────
    elif trend_7d == "stable" and volatility > 10:
        direction = "stable"
        confidence = 0.5
        factors.append("Prices are stable but showing high day-to-day variation")
        factors.append("Market conditions are uncertain")
        outlook = (
            "Prices are fluctuating significantly. Selling at current "
            "prices is reasonable, but waiting carries risk of both gains and losses."
        )

    # ── Rule 7: Default — stable market ──────────────────────────────────
    else:
        direction = "stable"
        confidence = 0.6
        factors.append("No strong price signals in either direction")
        if rain_48h:
            factors.append("Some rain expected but unlikely to impact prices significantly")
        outlook = (
            "Market conditions are relatively stable. "
            "Selling at current prices is a safe option."
        )

    # ── Adjust confidence based on data quality ──────────────────────────
    data_points = trend_data.get("data_points", 0)
    if data_points < 3:
        confidence = min(confidence, 0.45)
        factors.append("Limited data available — estimate has low confidence")
    elif data_points > 20:
        confidence = min(confidence + 0.1, 0.95)

    return {
        "direction": direction,
        "confidence": round(confidence, 2),
        "outlook_text": outlook,
        "factors": factors,
    }


def compute_confidence_score(trend_data: dict, weather_data: dict) -> float:
    """
    Compute overall confidence score for the market analysis.

    Scoring rubric:
        0.9 – 1.0: Strong API data, stable trend, consistent signals
        0.7 – 0.89: Moderate confidence, some volatility
        0.5 – 0.69: Uncertain trend, incomplete signals
        Below 0.5: Insufficient data, unstable conditions
    """
    score = 0.7  # Base score

    data_points = trend_data.get("data_points", 0)
    volatility = trend_data.get("volatility_pct", 0.0)
    trend_7d = trend_data.get("trend_7d", "stable")
    trend_30d = trend_data.get("trend_30d", "stable")

    rain_48h = weather_data.get("rain_expected_48h", False)
    rainfall_mm = weather_data.get("rainfall_mm_48h", 0.0)

    # Data quality bonus/penalty
    if data_points >= 20:
        score += 0.15
    elif data_points >= 10:
        score += 0.08
    elif data_points < 3:
        score -= 0.25

    # Trend consistency bonus
    if trend_7d == trend_30d:
        score += 0.05  # Both trends agree

    # Volatility penalty
    if volatility > 15:
        score -= 0.15
    elif volatility > 10:
        score -= 0.08
    elif volatility < 5:
        score += 0.05

    # Weather uncertainty
    if rainfall_mm > 20:
        score -= 0.1
    elif rain_48h:
        score -= 0.05

    # Clamp to valid range
    return round(max(0.1, min(0.95, score)), 2)
