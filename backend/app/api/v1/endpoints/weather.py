"""
weather.py — Weather endpoint for FasalSaathi backend.
Uses the centralized, cached WeatherService.
"""
from fastapi import APIRouter, HTTPException, Query
from backend.app.services.weather_service import get_weather_service

router = APIRouter()


@router.get("/current")
def get_current_weather(
    lat: float = Query(28.6139, description="Latitude"),
    lon: float = Query(77.2090, description="Longitude"),
):
    """
    Return current weather for the given coordinates using the centralized WeatherService.
    Provides automatic caching, retries, and fallback.
    """
    weather = get_weather_service().get_current_weather(lat, lon)
    if not weather:
        raise HTTPException(
            status_code=502,
            detail="Weather service unreachable or failed to return data",
        )

    return {
        "temp":         round(weather["temperature_c"]),
        "humidity":     round(weather["humidity_pct"]),
        "windSpeed":    round(weather["wind_speed_kmh"]),
        "condition":    weather["condition"],
        "weatherCode":  weather["weather_code"],
        "riskLevel":    weather["risk_level"],
        "lat":          lat,
        "lon":          lon,
    }

