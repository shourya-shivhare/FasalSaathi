"""
weather.py — Weather endpoint for FasalSaathi backend.
Uses Open-Meteo free API (no API key required).
"""
from fastapi import APIRouter, HTTPException, Query
import httpx

router = APIRouter()

# WMO weather code → human-readable condition
WMO_CONDITIONS = {
    0: "Sunny", 1: "Partly Cloudy", 2: "Partly Cloudy", 3: "Cloudy",
    45: "Foggy", 48: "Foggy",
    51: "Drizzle", 53: "Drizzle", 55: "Drizzle",
    61: "Rainy", 63: "Rainy", 65: "Heavy Rain",
    71: "Snowy", 73: "Snowy", 75: "Heavy Snow",
    80: "Showers", 81: "Showers", 82: "Heavy Showers",
    85: "Snow Showers", 86: "Snow Showers",
    95: "Thunderstorm", 96: "Thunderstorm", 99: "Thunderstorm",
}


@router.get("/current")
async def get_current_weather(
    lat: float = Query(28.6139, description="Latitude"),
    lon: float = Query(77.2090, description="Longitude"),
):
    """
    Return current weather for the given coordinates using Open-Meteo.
    Falls back to default values if the upstream API is unreachable.
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current_weather=true"
        f"&hourly=relativehumidity_2m,windspeed_10m"
        f"&forecast_days=1"
    )
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Weather service unreachable: {exc}",
        )

    cw = data.get("current_weather", {})
    hourly = data.get("hourly", {})

    temperature = round(cw.get("temperature", 28))
    wind_speed  = round(cw.get("windspeed",   12))
    weather_code = cw.get("weathercode", 0)
    condition   = WMO_CONDITIONS.get(weather_code, "Clear")

    # First hourly value — close to now
    humidity = (hourly.get("relativehumidity_2m") or [60])[0]

    risk_level = "HIGH" if humidity > 80 else "MODERATE" if humidity > 60 else "LOW"

    return {
        "temp":         temperature,
        "humidity":     humidity,
        "windSpeed":    wind_speed,
        "condition":    condition,
        "weatherCode":  weather_code,
        "riskLevel":    risk_level,
        "lat":          lat,
        "lon":          lon,
    }
