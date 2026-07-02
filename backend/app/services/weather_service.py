"""
Weather Service Abstraction Layer
─────────────────────────────────
Provides a decoupled interface for fetching current weather and forecasts.
Supports caching, retries with exponential backoff, and graceful fallbacks.
"""
from __future__ import annotations

import time
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple
import httpx

logger = logging.getLogger(__name__)


class WeatherService(ABC):
    """Abstract base class for all weather service providers."""

    @abstractmethod
    def get_current_weather(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Fetch current weather for the given coordinates."""
        pass

    @abstractmethod
    def get_weather_forecast(self, lat: float, lon: float, days: int = 16) -> Optional[Dict[str, Any]]:
        """
        Fetch weather forecast (current + daily forecast arrays) for the given coordinates.
        
        Returns a dictionary containing:
          - current: dict (same format as get_current_weather)
          - daily: list of dicts (date, temp_min, temp_max, precipitation_mm, humidity_pct, weather_code)
        """
        pass


from backend.app.services.cache_service import CacheService
from backend.app.utils.cache_keys import make_weather_key


class CachingWeatherService(WeatherService):
    """
    Wrapper service that caches weather responses by rounded coordinates
    in Redis with local memory fallback to avoid excessive API rate limits.
    """

    def __init__(self, raw_service: WeatherService, cache_ttl_seconds: int = 900):
        self.raw_service = raw_service
        self.cache_ttl = cache_ttl_seconds
        # Current local cache key: (round(lat, 3), round(lon, 3)), value: (timestamp, weather_dict)
        self._current_cache: Dict[Tuple[float, float], Tuple[float, Dict[str, Any]]] = {}
        # Forecast local cache key: (round(lat, 3), round(lon, 3), days), value: (timestamp, forecast_dict)
        self._forecast_cache: Dict[Tuple[float, float, int], Tuple[float, Dict[str, Any]]] = {}

    def get_current_weather(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        redis_key = make_weather_key(lat, lon, forecast=False)
        cached = CacheService.get_sync(redis_key)
        if cached is not None:
            return cached

        key = (round(lat, 3), round(lon, 3))
        now = time.time()

        if key in self._current_cache:
            ts, cached_data = self._current_cache[key]
            if now - ts < self.cache_ttl:
                logger.info("🌤️ WeatherService local current-cache hit for coordinates %s", key)
                # Store in Redis since it was a Redis cache miss
                CacheService.set_sync(redis_key, cached_data, ttl=self.cache_ttl)
                return cached_data

        logger.info("🌤️ WeatherService current-cache miss for coordinates %s", key)
        data = self.raw_service.get_current_weather(lat, lon)
        if data:
            self._current_cache[key] = (now, data)
            CacheService.set_sync(redis_key, data, ttl=self.cache_ttl)
        return data

    def get_weather_forecast(self, lat: float, lon: float, days: int = 16) -> Optional[Dict[str, Any]]:
        redis_key = make_weather_key(lat, lon, forecast=True, days=days)
        cached = CacheService.get_sync(redis_key)
        if cached is not None:
            return cached

        key = (round(lat, 3), round(lon, 3), days)
        now = time.time()

        if key in self._forecast_cache:
            ts, cached_data = self._forecast_cache[key]
            if now - ts < self.cache_ttl:
                logger.info("🌤️ WeatherService local forecast-cache hit for coordinates %s", key)
                # Store in Redis since it was a Redis cache miss
                CacheService.set_sync(redis_key, cached_data, ttl=self.cache_ttl)
                return cached_data

        logger.info("🌤️ WeatherService forecast-cache miss for coordinates %s", key)
        data = self.raw_service.get_weather_forecast(lat, lon, days)
        if data:
            self._forecast_cache[key] = (now, data)
            CacheService.set_sync(redis_key, data, ttl=self.cache_ttl)
        return data



class OpenMeteoWeatherService(WeatherService):
    """Fetches weather synchronously from Open-Meteo with retries and fallback."""

    def __init__(
        self,
        timeout: float = 5.0,
        max_retries: int = 3,
        backoff_factor: float = 1.5,
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.wmo_conditions = {
            0: "Sunny", 1: "Partly Cloudy", 2: "Partly Cloudy", 3: "Cloudy",
            45: "Foggy", 48: "Foggy",
            51: "Drizzle", 53: "Drizzle", 55: "Drizzle",
            61: "Rainy", 63: "Rainy", 65: "Heavy Rain",
            71: "Snowy", 73: "Snowy", 75: "Heavy Snow",
            80: "Showers", 81: "Showers", 82: "Heavy Showers",
            85: "Snow Showers", 86: "Snow Showers",
            95: "Thunderstorm", 96: "Thunderstorm", 99: "Thunderstorm",
        }

    def get_current_weather(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&current_weather=true"
            f"&hourly=relative_humidity_2m,windspeed_10m"
            f"&forecast_days=1"
        )

        delay = 1.0
        for attempt in range(self.max_retries):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    resp = client.get(url)
                    resp.raise_for_status()
                    data = resp.json()

                    cw = data.get("current_weather", {})
                    hourly = data.get("hourly", {})
                    temperature = cw.get("temperature", 28.0)
                    wind_speed = cw.get("windspeed", 12.0)
                    weather_code = cw.get("weathercode", 0)
                    condition = self.wmo_conditions.get(weather_code, "Clear")
                    humidity_list = hourly.get("relative_humidity_2m") or hourly.get("relativehumidity_2m") or [60.0]
                    humidity = humidity_list[0] if humidity_list else 60.0
                    risk_level = "HIGH" if (humidity and humidity > 80) else "MODERATE" if (humidity and humidity > 60) else "LOW"

                    return {
                        "temperature_c": float(temperature) if temperature is not None else 28.0,
                        "humidity_pct": float(humidity) if humidity is not None else 60.0,
                        "wind_speed_kmh": float(wind_speed) if wind_speed is not None else 12.0,
                        "condition": condition,
                        "weather_code": int(weather_code) if weather_code is not None else 0,
                        "risk_level": risk_level,
                        "lat": lat,
                        "lon": lon,
                    }
            except Exception as e:
                logger.warning("🌤️ OpenMeteo get_current_weather: Attempt %d failed: %s", attempt + 1, e)
                if attempt < self.max_retries - 1:
                    time.sleep(delay)
                    delay *= self.backoff_factor
                else:
                    logger.error("🌤️ OpenMeteo get_current_weather: All %d attempts failed.", self.max_retries)

        return None

    def get_weather_forecast(self, lat: float, lon: float, days: int = 16) -> Optional[Dict[str, Any]]:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&current_weather=true"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,relative_humidity_2m_mean,weathercode"
            f"&forecast_days={days}"
            f"&timezone=auto"
        )

        delay = 1.0
        for attempt in range(self.max_retries):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    resp = client.get(url)
                    resp.raise_for_status()
                    data = resp.json()

                    # 1. Parse Current Weather
                    cw = data.get("current_weather", {})
                    temperature = cw.get("temperature", 28.0)
                    wind_speed = cw.get("windspeed", 12.0)
                    weather_code = cw.get("weathercode", 0)
                    condition = self.wmo_conditions.get(weather_code, "Clear")
                    
                    # Estimate current humidity from daily mean if not available hourly
                    daily = data.get("daily", {})
                    humidity_list = daily.get("relative_humidity_2m_mean") or daily.get("relativehumidity_2m_mean") or [60.0]
                    current_humidity = humidity_list[0] if humidity_list else 60.0
                    risk_level = "HIGH" if (current_humidity and current_humidity > 80) else "MODERATE" if (current_humidity and current_humidity > 60) else "LOW"

                    current = {
                        "temperature_c": float(temperature) if temperature is not None else 28.0,
                        "humidity_pct": float(current_humidity) if current_humidity is not None else 60.0,
                        "wind_speed_kmh": float(wind_speed) if wind_speed is not None else 12.0,
                        "condition": condition,
                        "weather_code": int(weather_code) if weather_code is not None else 0,
                        "risk_level": risk_level,
                        "lat": lat,
                        "lon": lon,
                    }

                    # 2. Parse Daily Forecasts
                    daily_forecasts = []
                    dates = daily.get("time", [])
                    t_maxs = daily.get("temperature_2m_max", [])
                    t_mins = daily.get("temperature_2m_min", [])
                    precips = daily.get("precipitation_sum", [])
                    humidities = daily.get("relative_humidity_2m_mean") or daily.get("relativehumidity_2m_mean") or [60.0] * len(dates)
                    codes = daily.get("weathercode", [])

                    for i in range(len(dates)):
                        code = codes[i] if (i < len(codes) and codes[i] is not None) else 0
                        daily_forecasts.append({
                            "date": dates[i],
                            "temp_min": float(t_mins[i]) if (i < len(t_mins) and t_mins[i] is not None) else 20.0,
                            "temp_max": float(t_maxs[i]) if (i < len(t_maxs) and t_maxs[i] is not None) else 30.0,
                            "precipitation_mm": float(precips[i]) if (i < len(precips) and precips[i] is not None) else 0.0,
                            "humidity_pct": float(humidities[i]) if (i < len(humidities) and humidities[i] is not None) else 60.0,
                            "condition": self.wmo_conditions.get(code, "Clear"),
                            "weather_code": int(code),
                        })

                    return {
                        "current": current,
                        "daily": daily_forecasts,
                    }
            except Exception as e:
                logger.warning("🌤️ OpenMeteo get_weather_forecast: Attempt %d failed: %s", attempt + 1, e)
                if attempt < self.max_retries - 1:
                    time.sleep(delay)
                    delay *= self.backoff_factor
                else:
                    logger.error("🌤️ OpenMeteo get_weather_forecast: All %d attempts failed.", self.max_retries)

        return None


# ── Global Service Instance (OpenMeteo wrapped in Caching) ───────────────────

_default_weather_service = CachingWeatherService(OpenMeteoWeatherService())


def get_weather_service() -> WeatherService:
    """Retrieve the configured global WeatherService instance."""
    return _default_weather_service
