import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.models.rate_limit_event import RateLimitEvent
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


def log_rate_limit_event(db: Session, identifier: str, event_type: str, ip_address: str = None) -> None:
    """Inserts a rate limit event into the database (for PostgreSQL fallback auditing)."""
    event = RateLimitEvent(
        identifier=identifier,
        event_type=event_type,
        ip_address=ip_address,
        created_at=datetime.now(timezone.utc),
    )
    db.add(event)
    db.commit()


def check_otp_send_limits(db: Session, phone_number: str, ip_address: str) -> None:
    """
    Enforces rate limiting rules for sending OTP:
    1. Max 1 OTP per phone number in 1 Minute.
    2. Max 5 OTPs per phone number in 1 Hour.
    3. Max 20 OTPs per phone number in 24 Hours.
    4. Max 10 OTPs per IP address in 1 Hour.
    Uses Redis when available, falling back to PostgreSQL if Redis is down.
    """
    if not settings.ENABLE_RATE_LIMIT:
        return

    # ── Redis Rate Limiting Check ──
    from backend.app.core.redis import redis_manager
    from backend.app.services.redis_rate_limiter import RedisRateLimiter

    if redis_manager.is_connected:
        try:
            # Rule 1: 1 per phone number in 1 min
            RedisRateLimiter.check_rate_limit(
                f"rate:otp:send:phone_1m:{phone_number}",
                1,
                60,
                "Please wait 1 minute before requesting another OTP.",
            )
            # Rule 2: 5 per phone number in 1 hour
            RedisRateLimiter.check_rate_limit(
                f"rate:otp:send:phone_1h:{phone_number}",
                5,
                3600,
                "Exceeded limit of 5 OTP requests per hour for this phone number.",
            )
            # Rule 3: 20 per phone number in 24 hours
            RedisRateLimiter.check_rate_limit(
                f"rate:otp:send:phone_24h:{phone_number}",
                20,
                86400,
                "Exceeded daily limit of 20 OTP requests for this phone number.",
            )
            # Rule 4: 10 per IP in 1 hour
            RedisRateLimiter.check_rate_limit(
                f"rate:otp:send:ip_1h:{ip_address}",
                10,
                3600,
                "Exceeded limit of 10 OTP requests per hour from this IP address.",
            )
            return  # Redis rate limit passed successfully
        except HTTPException:
            raise
        except Exception as e:
            logger.warning("⚠️ Redis rate limiter failed: %s. Falling back to DB rate limiter.", e)

    # ── Fallback DB Rate Limiting Check ──
    now = datetime.now(timezone.utc)

    # Rule 1: 1 per phone number in 1 min
    one_min_ago = now - timedelta(minutes=1)
    one_min_count = (
        db.query(RateLimitEvent)
        .filter(
            RateLimitEvent.identifier == phone_number,
            RateLimitEvent.event_type == "OTP_REQUEST",
            RateLimitEvent.created_at >= one_min_ago,
        )
        .count()
    )
    if one_min_count >= 1:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Please wait 1 minute before requesting another OTP.",
        )

    # Rule 2: 5 per phone number in 1 hour
    one_hour_ago = now - timedelta(hours=1)
    one_hour_count = (
        db.query(RateLimitEvent)
        .filter(
            RateLimitEvent.identifier == phone_number,
            RateLimitEvent.event_type == "OTP_REQUEST",
            RateLimitEvent.created_at >= one_hour_ago,
        )
        .count()
    )
    if one_hour_count >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Exceeded limit of 5 OTP requests per hour for this phone number.",
        )

    # Rule 3: 20 per phone number in 24 hours
    twenty_four_hours_ago = now - timedelta(hours=24)
    daily_count = (
        db.query(RateLimitEvent)
        .filter(
            RateLimitEvent.identifier == phone_number,
            RateLimitEvent.event_type == "OTP_REQUEST",
            RateLimitEvent.created_at >= twenty_four_hours_ago,
        )
        .count()
    )
    if daily_count >= 20:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Exceeded daily limit of 20 OTP requests for this phone number.",
        )

    # Rule 4: 10 per IP in 1 hour
    ip_count = (
        db.query(RateLimitEvent)
        .filter(
            RateLimitEvent.identifier == ip_address,
            RateLimitEvent.event_type == "OTP_REQUEST",
            RateLimitEvent.created_at >= one_hour_ago,
        )
        .count()
    )
    if ip_count >= 10:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Exceeded limit of 10 OTP requests per hour from this IP address.",
        )

    # Log successful request events in DB
    log_rate_limit_event(db, phone_number, "OTP_REQUEST", ip_address)
    log_rate_limit_event(db, ip_address, "OTP_REQUEST", ip_address)


def check_otp_verify_limits(db: Session, ip_address: str) -> None:
    """
    Enforces rate limiting rules for verifying OTP:
    1. Max 5 verification attempts per IP in 15 Minutes.
    Uses Redis when available, falling back to PostgreSQL if Redis is down.
    """
    if not settings.ENABLE_RATE_LIMIT:
        return

    # ── Redis Rate Limiting Check ──
    from backend.app.core.redis import redis_manager
    from backend.app.services.redis_rate_limiter import RedisRateLimiter

    if redis_manager.is_connected:
        try:
            RedisRateLimiter.check_rate_limit(
                f"rate:otp:verify:ip_15m:{ip_address}",
                5,
                900,
                "Too many OTP verification attempts. Please wait 15 minutes.",
            )
            return
        except HTTPException:
            raise
        except Exception as e:
            logger.warning("⚠️ Redis rate limiter failed: %s. Falling back to DB rate limiter.", e)

    # ── Fallback DB Rate Limiting Check ──
    now = datetime.now(timezone.utc)
    fifteen_mins_ago = now - timedelta(minutes=15)

    count = (
        db.query(RateLimitEvent)
        .filter(
            RateLimitEvent.identifier == ip_address,
            RateLimitEvent.event_type == "OTP_VERIFY",
            RateLimitEvent.created_at >= fifteen_mins_ago,
        )
        .count()
    )

    if count >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many OTP verification attempts. Please wait 15 minutes.",
        )

    # Log verification attempt in DB
    log_rate_limit_event(db, ip_address, "OTP_VERIFY", ip_address)


def check_login_limits(db: Session, username: str, ip_address: str) -> None:
    """
    Enforces rate limiting rules for login attempts:
    1. Max 5 attempts per username in 15 Minutes.
    2. Max 20 attempts per IP address in 1 Hour.
    Uses Redis when available, falling back to PostgreSQL if Redis is down.
    """
    if not settings.ENABLE_RATE_LIMIT:
        return

    # ── Redis Rate Limiting Check ──
    from backend.app.core.redis import redis_manager
    from backend.app.services.redis_rate_limiter import RedisRateLimiter

    if redis_manager.is_connected:
        try:
            # Rule 1: Max 5 attempts per username in 15 Minutes
            RedisRateLimiter.check_rate_limit(
                f"rate:login:username_15m:{username}",
                5,
                900,
                "Too many login attempts for this username. Please wait 15 minutes.",
            )
            # Rule 2: Max 20 attempts per IP address in 1 Hour
            RedisRateLimiter.check_rate_limit(
                f"rate:login:ip_1h:{ip_address}",
                20,
                3600,
                "Too many login attempts from this IP address. Please wait 1 hour.",
            )
            return
        except HTTPException:
            raise
        except Exception as e:
            logger.warning("⚠️ Redis rate limiter failed: %s. Falling back to DB rate limiter.", e)

    # ── Fallback DB Rate Limiting Check ──
    now = datetime.now(timezone.utc)

    # Rule 1: Max 5 attempts per username in 15 Minutes
    fifteen_mins_ago = now - timedelta(minutes=15)
    username_count = (
        db.query(RateLimitEvent)
        .filter(
            RateLimitEvent.identifier == username,
            RateLimitEvent.event_type == "LOGIN_ATTEMPT",
            RateLimitEvent.created_at >= fifteen_mins_ago,
        )
        .count()
    )
    if username_count >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts for this username. Please wait 15 minutes.",
        )

    # Rule 2: Max 20 attempts per IP address in 1 Hour
    one_hour_ago = now - timedelta(hours=1)
    ip_count = (
        db.query(RateLimitEvent)
        .filter(
            RateLimitEvent.identifier == ip_address,
            RateLimitEvent.event_type == "LOGIN_ATTEMPT",
            RateLimitEvent.created_at >= one_hour_ago,
        )
        .count()
    )
    if ip_count >= 20:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts from this IP address. Please wait 1 hour.",
        )

    # Log login attempts in DB
    log_rate_limit_event(db, username, "LOGIN_ATTEMPT", ip_address)
    if ip_address:
        log_rate_limit_event(db, ip_address, "LOGIN_ATTEMPT", ip_address)
