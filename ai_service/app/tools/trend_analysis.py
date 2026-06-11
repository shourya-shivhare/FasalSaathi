"""
Trend Analysis Utilities
────────────────────────
Pure-Python price analysis for AGMARKNET mandi records.
No external dependencies beyond stdlib `statistics`.

Functions:
  - compute_price_trend: 7-day & 30-day direction, momentum, volatility
  - compute_moving_averages: simple moving averages
  - compute_market_sentiment: bullish / bearish / neutral / volatile
"""
from __future__ import annotations

import logging
from datetime import datetime
from statistics import mean, stdev
from typing import Optional

logger = logging.getLogger(__name__)


def _parse_date(date_str: str) -> Optional[datetime]:
    """Parse AGMARKNET date formats (dd/mm/yyyy or yyyy-mm-dd)."""
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except (ValueError, AttributeError):
            continue
    return None


def _extract_prices(records: list[dict]) -> list[tuple[datetime, float]]:
    """Extract (date, modal_price) pairs, sorted by date ascending."""
    pairs = []
    for r in records:
        date = _parse_date(str(r.get("arrival_date", "")))
        price = r.get("modal_price")
        if date is not None and price is not None:
            try:
                pairs.append((date, float(price)))
            except (ValueError, TypeError):
                continue
    pairs.sort(key=lambda x: x[0])
    return pairs


def _compute_direction(prices: list[float], threshold_pct: float = 2.0) -> str:
    """Determine trend direction from a price series."""
    if len(prices) < 2:
        return "stable"
    first_avg = mean(prices[: max(1, len(prices) // 3)])
    last_avg = mean(prices[-(max(1, len(prices) // 3)):])
    change_pct = ((last_avg - first_avg) / first_avg) * 100 if first_avg else 0
    if change_pct > threshold_pct:
        return "rising"
    elif change_pct < -threshold_pct:
        return "falling"
    return "stable"


def compute_price_trend(records: list[dict]) -> dict:
    """
    Analyze price trend from AGMARKNET records.

    Returns:
        {trend_7d, trend_30d, momentum_pct, volatility_pct,
         avg_price, min_price, max_price, data_points}
    """
    if not records:
        return {
            "trend_7d": "stable",
            "trend_30d": "stable",
            "momentum_pct": 0.0,
            "volatility_pct": 0.0,
            "avg_price": 0,
            "min_price": 0,
            "max_price": 0,
            "data_points": 0,
        }

    pairs = _extract_prices(records)
    all_prices = [p for _, p in pairs]

    if not all_prices:
        return {
            "trend_7d": "stable",
            "trend_30d": "stable",
            "momentum_pct": 0.0,
            "volatility_pct": 0.0,
            "avg_price": 0,
            "min_price": 0,
            "max_price": 0,
            "data_points": 0,
        }

    # 7-day trend (use last 7 data points)
    recent_7 = all_prices[-7:] if len(all_prices) >= 7 else all_prices
    trend_7d = _compute_direction(recent_7)

    # 30-day trend (all available data, up to 30 points)
    recent_30 = all_prices[-30:] if len(all_prices) >= 30 else all_prices
    trend_30d = _compute_direction(recent_30)

    # Momentum: % change from first to last price
    momentum_pct = 0.0
    if len(all_prices) >= 2 and all_prices[0] > 0:
        momentum_pct = round(
            ((all_prices[-1] - all_prices[0]) / all_prices[0]) * 100, 2
        )

    # Volatility: coefficient of variation (stdev / mean * 100)
    volatility_pct = 0.0
    if len(all_prices) >= 2:
        avg = mean(all_prices)
        if avg > 0:
            volatility_pct = round((stdev(all_prices) / avg) * 100, 2)

    avg_price = round(mean(all_prices))
    min_price = round(min(all_prices))
    max_price = round(max(all_prices))

    return {
        "trend_7d": trend_7d,
        "trend_30d": trend_30d,
        "momentum_pct": momentum_pct,
        "volatility_pct": volatility_pct,
        "avg_price": avg_price,
        "min_price": min_price,
        "max_price": max_price,
        "data_points": len(all_prices),
    }


def compute_moving_averages(
    records: list[dict],
    windows: list[int] | None = None,
) -> dict:
    """
    Compute simple moving averages for given windows.

    Returns: {"sma_7": float | None, "sma_14": float | None, "sma_30": float | None}
    """
    if windows is None:
        windows = [7, 14, 30]

    pairs = _extract_prices(records)
    all_prices = [p for _, p in pairs]

    result = {}
    for w in windows:
        key = f"sma_{w}"
        if len(all_prices) >= w:
            result[key] = round(mean(all_prices[-w:]), 2)
        else:
            result[key] = None

    return result


def compute_market_sentiment(
    trend: str,
    volatility_pct: float,
    weather_risk: str = "low",
) -> str:
    """
    Derive market sentiment from trend direction, volatility, and weather risk.

    Returns one of: "bullish", "bearish", "neutral", "volatile"
    """
    # High volatility overrides everything
    if volatility_pct > 15.0:
        return "volatile"

    # Falling trend is always bearish
    if trend == "falling":
        return "bearish"

    # Rising trend
    if trend == "rising":
        if weather_risk in ("high",):
            return "volatile"  # rising but risky weather
        return "bullish"

    # Stable
    return "neutral"
