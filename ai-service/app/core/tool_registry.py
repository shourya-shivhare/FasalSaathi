"""
Dependency Injection container for all tool clients.
Injected via GraphRuntimeContext — never as a global singleton.

Easily mockable for testing:
    mock_registry = ToolRegistry(weather_client=MockWeather(), ...)
    set on test runtime context
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ToolRegistry:
    """DI container for all tools. Injected via GraphRuntimeContext."""
    weather_client: Any       # openweather: fetch_current_weather, fetch_forecast_5day
    market_client: Any        # agmarknet: fetch_mandi_prices, fetch_nearby_markets
    memory_store: Any         # FarmerMemoryStore (SQLiteMemoryStore)
    scheme_db: Any            # scheme_db: search_schemes, get_all_schemes
    trend_analyzer: Any       # trend_analysis: compute_price_trend, compute_market_sentiment
    forecaster: Any           # forecasting: predict_short_term, compute_confidence_score
    pest_map: Any             # pest_map: get_full_pest_info, get_suggestions
    image_store: Any          # ImageStore: save, get, delete
    memory_tools: Any         # MemoryTools: get_past_crops, get_pest_history


def create_production_registry() -> ToolRegistry:
    """Build registry with real tool implementations for production."""
    from app.tools import weather_client as wc
    from app.tools import agmarknet_client as mc
    from app.tools import scheme_db as sdb
    from app.tools import trend_analysis as ta
    from app.tools import forecasting as fc
    from app.tools import pest_map as pm
    from app.tools import memory_tools as mt
    from app.storage.image_store import ImageStore
    from app.memory.store import SQLiteMemoryStore

    mem_store = SQLiteMemoryStore()

    return ToolRegistry(
        weather_client=wc,
        market_client=mc,
        memory_store=mem_store,
        scheme_db=sdb,
        trend_analyzer=ta,
        forecaster=fc,
        pest_map=pm,
        image_store=ImageStore(),
        memory_tools=mt.MemoryTools(mem_store),
    )
