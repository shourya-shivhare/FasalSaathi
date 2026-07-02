import hashlib
import json
from typing import Optional


def make_weather_key(lat: float, lon: float, forecast: bool = False, days: int = 16) -> str:
    """Generate weather key with rounded coordinates."""
    flat_lat = round(lat, 3)
    flat_lon = round(lon, 3)
    suffix = f":forecast:{days}" if forecast else ":current"
    return f"weather:{flat_lat}:{flat_lon}{suffix}"


def make_market_key(
    state: Optional[str],
    district: Optional[str],
    crop: Optional[str],
) -> str:
    """Generate market prices key."""
    s = (state or "all").strip().lower()
    d = (district or "all").strip().lower()
    c = (crop or "all").strip().lower()
    return f"market:{s}:{d}:{c}"


def make_context_key(user_id: int) -> str:
    """Generate user context key."""
    return f"context:{user_id}"


def make_schemes_key(state: Optional[str]) -> str:
    """Generate state schemes list key."""
    s = (state or "all").strip().lower()
    return f"schemes:{s}"


def make_schemes_list_key(
    category: Optional[str],
    state: Optional[str],
    crop: Optional[str],
    skip: int,
    limit: int,
) -> str:
    """Generate list of schemes cache key."""
    cat = (category or "all").strip().lower()
    st = (state or "all").strip().lower()
    cr = (crop or "all").strip().lower()
    return f"schemes:list:{cat}:{st}:{cr}:{skip}:{limit}"


def make_chat_key(
    user_id: int,
    last_message: str,
    context: Optional[dict],
    language: str,
    model_version: str,
) -> str:
    """Generate user chat key incorporating context hash and message query hash."""
    context_str = json.dumps(context or {}, sort_keys=True)
    context_hash = hashlib.md5(context_str.encode("utf-8")).hexdigest()
    msg_hash = hashlib.md5(last_message.strip().lower().encode("utf-8")).hexdigest()
    lang = language.strip().lower()
    mv = model_version.strip().lower()
    return f"chat:{user_id}:{lang}:{mv}:{context_hash}:{msg_hash}"


def make_profile_key(user_id: int) -> str:
    """Generate profile key."""
    return f"profile:{user_id}"


def make_farm_key(farm_id: int) -> str:
    """Generate farm detail key."""
    return f"farm:{farm_id}"


def make_dashboard_key(user_id: int) -> str:
    """Generate dashboard metrics key."""
    return f"dashboard:{user_id}"


def make_crop_recommendation_key(user_id: int, context_hash: str) -> str:
    """Generate crop recommendation key."""
    return f"crop_rec:{user_id}:{context_hash}"


def make_scheme_recommendation_key(user_id: int, context_hash: str) -> str:
    """Generate scheme recommendation key."""
    return f"scheme_rec:{user_id}:{context_hash}"


def make_notification_summary_key(user_id: int) -> str:
    """Generate notification summary key."""
    return f"notification_summary:{user_id}"
