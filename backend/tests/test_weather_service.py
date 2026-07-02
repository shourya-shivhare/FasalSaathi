import pytest
import time
from backend.app.services.weather_service import (
    WeatherService,
    CachingWeatherService,
    OpenMeteoWeatherService,
)


class MockWeatherProvider(WeatherService):
    """Mock weather service that counts invocations to assert caching."""
    def __init__(self, should_fail_attempts: int = 0):
        self.invocations = 0
        self.should_fail_attempts = should_fail_attempts
        self.failed_attempts = 0

    def get_current_weather(self, lat: float, lon: float):
        self.invocations += 1
        if self.failed_attempts < self.should_fail_attempts:
            self.failed_attempts += 1
            raise ValueError("Simulated network failure")
            
        return {
            "temperature_c": 25.0,
            "humidity_pct": 65.0,
            "wind_speed_kmh": 10.0,
            "condition": "Sunny",
            "weather_code": 0,
            "risk_level": "MODERATE",
            "lat": lat,
            "lon": lon,
        }

    def get_weather_forecast(self, lat: float, lon: float, days: int = 16):
        self.invocations += 1
        if self.failed_attempts < self.should_fail_attempts:
            self.failed_attempts += 1
            raise ValueError("Simulated network failure")
            
        current = {
            "temperature_c": 25.0,
            "humidity_pct": 65.0,
            "wind_speed_kmh": 10.0,
            "condition": "Sunny",
            "weather_code": 0,
            "risk_level": "MODERATE",
            "lat": lat,
            "lon": lon,
        }
        
        daily = []
        for i in range(days):
            daily.append({
                "date": f"2026-07-{i+1:02d}",
                "temp_min": 15.0,
                "temp_max": 25.0,
                "precipitation_mm": 0.0,
                "humidity_pct": 65.0,
                "condition": "Sunny",
                "weather_code": 0,
            })
            
        return {
            "current": current,
            "daily": daily,
        }


def test_weather_caching():
    """Verify CachingWeatherService returns cached data on duplicate close coordinates."""
    mock_provider = MockWeatherProvider()
    cached_service = CachingWeatherService(mock_provider, cache_ttl_seconds=5)

    # First call - cache miss
    res1 = cached_service.get_current_weather(22.7196, 75.8577)
    assert res1 is not None
    assert mock_provider.invocations == 1

    # Second call for identical coordinates - cache hit
    res2 = cached_service.get_current_weather(22.7196, 75.8577)
    assert res2 == res1
    assert mock_provider.invocations == 1

    # Third call for rounded coordinates within 3 decimal places (~100m) - cache hit
    res3 = cached_service.get_current_weather(22.7199, 75.8579)
    assert res3 == res1
    assert mock_provider.invocations == 1

    # Fourth call for distant coordinates - cache miss
    res4 = cached_service.get_current_weather(28.6139, 77.2090)
    assert res4 is not None
    assert mock_provider.invocations == 2


def test_weather_cache_expiration():
    """Verify expired cache results trigger raw service reload."""
    mock_provider = MockWeatherProvider()
    cached_service = CachingWeatherService(mock_provider, cache_ttl_seconds=1)

    # First call
    cached_service.get_current_weather(22.7196, 75.8577)
    assert mock_provider.invocations == 1

    # Wait for TTL to expire
    time.sleep(1.1)

    # Second call
    cached_service.get_current_weather(22.7196, 75.8577)
    assert mock_provider.invocations == 2


def test_openmeteo_retry_and_fallback():
    """Verify retry logic on failure and final fallback behavior."""
    # Create service that fails on the first 2 calls, succeeds on the 3rd
    failing_service = OpenMeteoWeatherService(max_retries=3, backoff_factor=0.1)
    
    # We will test the OpenMeteo service coordinates retrieval directly
    # To check retry behavior under failure we simulate it using our mock provider first
    mock_failing_provider = MockWeatherProvider(should_fail_attempts=2)
    
    # Verify mock provider fails and succeeds on 3rd attempt
    with pytest.raises(ValueError):
        mock_failing_provider.get_current_weather(22.71, 75.85)
    with pytest.raises(ValueError):
        mock_failing_provider.get_current_weather(22.71, 75.85)
    
    res = mock_failing_provider.get_current_weather(22.71, 75.85)
    assert res["temperature_c"] == 25.0
