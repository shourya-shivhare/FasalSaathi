"""
Weather tool — fetches real weather from OpenWeather API.
Used by LangGraph weather_worker node in crop_advisor_graph.
"""
import asyncio
import logging
from langchain_core.tools import tool
from app.tools.openweather_client import fetch_current_weather

logger = logging.getLogger(__name__)


@tool
def get_weather_summary(location: str = "Delhi") -> str:
    """Fetch current weather summary from OpenWeather API."""
    try:
        # Extract city name (handle "City, State" format)
        city = location.split(",")[0].strip()

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, fetch_current_weather(city))
                data = future.result(timeout=10)
        else:
            data = asyncio.run(fetch_current_weather(city))

        return (
            f"Weather in {location}: {data.get('description', 'Clear')}, "
            f"{data.get('temp', 28)}°C (feels like {data.get('feels_like', 28)}°C), "
            f"humidity {data.get('humidity', 50)}%, "
            f"wind {data.get('wind_speed', 0)} km/h, "
            f"clouds {data.get('clouds', 0)}%."
        )

    except Exception as e:
        logger.error("get_weather_summary tool error: %s", e)
        return f"Weather data temporarily unavailable for {location}."
