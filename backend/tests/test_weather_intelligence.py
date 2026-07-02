import pytest
from datetime import datetime, timedelta
from backend.app.services.weather_intelligence import (
    WeatherIntelligenceService,
    DailyForecastInfo,
)
from backend.tests.test_weather_service import MockWeatherProvider


def test_gdd_calculation():
    """Assert Growing Degree Days calculation matches expectations (base 10°C)."""
    service = WeatherIntelligenceService(MockWeatherProvider())
    
    # Mock daily forecast: 7 days of 25°C max, 15°C min. Mean = 20°C. GDD per day = 10.0
    forecast = [
        DailyForecastInfo(
            date="2026-07-01",
            temp_min=15.0,
            temp_max=25.0,
            precipitation_mm=0.0,
            humidity_pct=60.0,
            condition="Sunny"
        )
        for _ in range(30)
    ]
    
    gdd = service._calculate_gdd(forecast)
    assert gdd.base_temperature_c == 10.0
    assert gdd.accumulated_7day == 70.0  # 7 * 10
    assert gdd.projected_30day == 300.0  # 30 * 10


def test_trend_classification_increasing():
    """Assert trend analyzer detects increasing temperatures."""
    service = WeatherIntelligenceService(MockWeatherProvider())
    
    # Temperatures increase from 15°C max to 35°C max
    forecast = []
    for i in range(30):
        forecast.append(
            DailyForecastInfo(
                date=f"2026-07-{i+1:02d}",
                temp_min=10.0,
                temp_max=15.0 + (i / 29.0) * 20.0,  # 15 to 35
                precipitation_mm=0.0,
                humidity_pct=60.0,
                condition="Sunny"
            )
        )
        
    trend = service._calculate_trend(forecast, attribute="temp_max", unit="°C")
    assert trend.trend_type == "Increasing"
    assert "trending higher" in trend.description.lower()


def test_trend_classification_decreasing():
    """Assert trend analyzer detects decreasing temperatures."""
    service = WeatherIntelligenceService(MockWeatherProvider())
    
    # Temperatures decrease from 30°C max to 10°C max
    forecast = []
    for i in range(30):
        forecast.append(
            DailyForecastInfo(
                date=f"2026-07-{i+1:02d}",
                temp_min=5.0,
                temp_max=30.0 - (i / 29.0) * 20.0,  # 30 to 10
                precipitation_mm=0.0,
                humidity_pct=60.0,
                condition="Sunny"
            )
        )
        
    trend = service._calculate_trend(forecast, attribute="temp_max", unit="°C")
    assert trend.trend_type == "Decreasing"
    assert "trending cooler" in trend.description.lower()


def test_risk_triggers_frost_and_heatwave():
    """Assert Frost and Heatwave warnings trigger on threshold breaches."""
    service = WeatherIntelligenceService(MockWeatherProvider())
    
    # 1. Test Frost (min temp < 4°C)
    forecast_frost = [
        DailyForecastInfo(
            date="2026-07-01",
            temp_min=3.0, # Frost breach
            temp_max=20.0,
            precipitation_mm=0.0,
            humidity_pct=50.0,
            condition="Sunny"
        )
        for _ in range(30)
    ]
    risks = service._assess_weather_risks(forecast_frost)
    risk_types = {r.risk_type for r in risks}
    assert "Frost" in risk_types
    assert any("frost detected" in r.description.lower() for r in risks)

    # 2. Test Heatwave (>= 40°C for 3 consecutive days)
    forecast_heat = [
        DailyForecastInfo(
            date="2026-07-01",
            temp_min=25.0,
            temp_max=41.0 if idx in (5, 6, 7) else 35.0, # 3 consecutive heatwave days
            precipitation_mm=0.0,
            humidity_pct=50.0,
            condition="Sunny"
        )
        for idx in range(30)
    ]
    risks = service._assess_weather_risks(forecast_heat)
    risk_types = {r.risk_type for r in risks}
    assert "Heatwave" in risk_types


def test_risk_triggers_pest_and_drought():
    """Assert Pest risk and Drought trigger on conditions."""
    service = WeatherIntelligenceService(MockWeatherProvider())
    
    # 1. Pest Risk (Humidity > 80% and temp 20-30°C for >= 4 days)
    forecast_pest = [
        DailyForecastInfo(
            date="2026-07-01",
            temp_min=22.0,
            temp_max=28.0,
            precipitation_mm=5.0,
            humidity_pct=85.0, # Pest breach
            condition="Rainy"
        )
        for _ in range(30)
    ]
    risks = service._assess_weather_risks(forecast_pest)
    risk_types = {r.risk_type for r in risks}
    assert "Pest Risk" in risk_types

    # 2. Drought Risk (precipitation < 10mm total in 30 days)
    forecast_dry = [
        DailyForecastInfo(
            date="2026-07-01",
            temp_min=20.0,
            temp_max=35.0,
            precipitation_mm=0.1, # dry
            humidity_pct=40.0,
            condition="Sunny"
        )
        for _ in range(30)
    ]
    risks = service._assess_weather_risks(forecast_dry)
    risk_types = {r.risk_type for r in risks}
    assert "Drought" in risk_types
