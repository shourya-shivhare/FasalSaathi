"""
Weather tool – stub for LangGraph nodes.
Replace with a real API call (e.g., OpenWeatherMap).
"""
from langchain_core.tools import tool


@tool
def get_weather_summary(location: str = "Delhi") -> str:
    """Fetch current weather summary for a location."""
    # TODO: integrate real weather API
    return f"Sunny, 32°C, humidity 65% in {location}. No rain expected for 3 days."
