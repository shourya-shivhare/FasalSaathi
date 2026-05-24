"""
OpenWeather API Client
──────────────────────
Async httpx client for weather data used by the market intelligence agent
and the LangGraph weather worker node.

Features:
  - Current weather + 5-day forecast
  - Graceful fallback to defaults on failure
"""
from __future__ import annotations

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# ── Defaults (returned on API failure) ───────────────────────────────────────
_DEFAULT_WEATHER = {
    "temp": 30,
    "feels_like": 32,
    "humidity": 50,
    "wind_speed": 10,
    "description": "Clear sky",
    "rain_probability": 0,
    "clouds": 20,
}

_DEFAULT_FORECAST = {
    "rain_expected_24h": False,
    "rain_expected_48h": False,
    "max_temp_48h": 35.0,
    "min_temp_48h": 25.0,
    "rainfall_mm_48h": 0.0,
    "forecast_summary": "No significant weather changes expected.",
}


# ── Public API ───────────────────────────────────────────────────────────────

async def fetch_current_weather(city: str, country_code: str = "IN") -> dict:
    """
    Fetch current weather from OpenWeather API.

    Returns normalised dict:
      {temp, feels_like, humidity, wind_speed, description, rain_probability, clouds}
    """
    if not settings.OPENWEATHER_API_KEY:
        logger.warning("OPENWEATHER_API_KEY not set — returning defaults")
        return dict(_DEFAULT_WEATHER)

    url = f"{settings.OPENWEATHER_BASE_URL}/weather"
    params = {
        "q": f"{city},{country_code}",
        "appid": settings.OPENWEATHER_API_KEY,
        "units": "metric",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        main = data.get("main", {})
        wind = data.get("wind", {})
        weather_list = data.get("weather", [{}])
        clouds = data.get("clouds", {})
        rain = data.get("rain", {})

        result = {
            "temp": round(main.get("temp", 30)),
            "feels_like": round(main.get("feels_like", 32)),
            "humidity": main.get("humidity", 50),
            "wind_speed": round(wind.get("speed", 0) * 3.6),  # m/s → km/h
            "description": weather_list[0].get("description", "clear sky").title(),
            "rain_probability": min(100, int(rain.get("1h", 0) * 10)),  # rough estimate
            "clouds": clouds.get("all", 0),
        }

        logger.info("OpenWeather: %s — %s, %d°C", city, result["description"], result["temp"])
        return result

    except httpx.HTTPStatusError as e:
        logger.error("OpenWeather HTTP error %s: %s", e.response.status_code, e)
    except httpx.RequestError as e:
        logger.error("OpenWeather connection error: %s", e)
    except Exception as e:
        logger.error("OpenWeather unexpected error: %s", e)

    return dict(_DEFAULT_WEATHER)


async def fetch_forecast_5day(city: str, country_code: str = "IN") -> dict:
    """
    Fetch 5-day / 3-hour forecast from OpenWeather API.

    Returns:
      {rain_expected_24h, rain_expected_48h, max_temp_48h, min_temp_48h,
       rainfall_mm_48h, forecast_summary}
    """
    if not settings.OPENWEATHER_API_KEY:
        logger.warning("OPENWEATHER_API_KEY not set — returning default forecast")
        return dict(_DEFAULT_FORECAST)

    url = f"{settings.OPENWEATHER_BASE_URL}/forecast"
    params = {
        "q": f"{city},{country_code}",
        "appid": settings.OPENWEATHER_API_KEY,
        "units": "metric",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        forecasts = data.get("list", [])

        rain_24h = False
        rain_48h = False
        max_temp = -100.0
        min_temp = 100.0
        total_rain = 0.0
        conditions = []

        # Each forecast item covers 3 hours
        # 8 items = 24h, 16 items = 48h
        for i, item in enumerate(forecasts[:16]):
            temp = item.get("main", {}).get("temp", 30)
            max_temp = max(max_temp, temp)
            min_temp = min(min_temp, temp)

            # Check for rain
            rain_3h = item.get("rain", {}).get("3h", 0)
            total_rain += rain_3h

            weather_main = item.get("weather", [{}])[0].get("main", "")
            if weather_main in ("Rain", "Drizzle", "Thunderstorm"):
                if i < 8:
                    rain_24h = True
                rain_48h = True
                if weather_main not in conditions:
                    conditions.append(weather_main)

        # Build summary
        if rain_48h:
            if total_rain > 20:
                summary = f"Heavy rainfall expected ({total_rain:.0f}mm in 48h). May disrupt transport and market arrivals."
            elif total_rain > 5:
                summary = f"Moderate rain expected ({total_rain:.1f}mm in 48h). Some transport delays possible."
            else:
                summary = f"Light rain expected ({total_rain:.1f}mm in 48h). Minimal market impact."
        elif max_temp > 42:
            summary = f"Extreme heat expected (up to {max_temp:.0f}°C). Perishable crops may be affected."
        else:
            summary = "No significant weather disruptions expected in the next 48 hours."

        result = {
            "rain_expected_24h": rain_24h,
            "rain_expected_48h": rain_48h,
            "max_temp_48h": round(max_temp, 1),
            "min_temp_48h": round(min_temp, 1),
            "rainfall_mm_48h": round(total_rain, 1),
            "forecast_summary": summary,
        }

        logger.info("OpenWeather forecast: %s — rain_48h=%s, rainfall=%.1fmm",
                     city, rain_48h, total_rain)
        return result

    except httpx.HTTPStatusError as e:
        logger.error("OpenWeather forecast HTTP error %s: %s", e.response.status_code, e)
    except httpx.RequestError as e:
        logger.error("OpenWeather forecast connection error: %s", e)
    except Exception as e:
        logger.error("OpenWeather forecast unexpected error: %s", e)

    return dict(_DEFAULT_FORECAST)
