from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.models.rate_limit_event import RateLimitEvent

def log_rate_limit_event(db: Session, identifier: str, event_type: str, ip_address: str = None):
    """
    Inserts a rate limit event into the database.
    """
    event = RateLimitEvent(
        identifier=identifier,
        event_type=event_type,
        ip_address=ip_address,
        created_at=datetime.now(timezone.utc)
    )
    db.add(event)
    db.commit()

def check_otp_send_limits(db: Session, phone_number: str, ip_address: str) -> None:
    """
    Enforces the rate limiting rules for sending OTP:
    1. Max 1 OTP per phone number in 1 Minute.
    2. Max 5 OTPs per phone number in 1 Hour.
    3. Max 20 OTPs per phone number in 24 Hours.
    4. Max 10 OTPs per IP address in 1 Hour.
    Raises HTTPException (429) if limit exceeded.
    """
    now = datetime.now(timezone.utc)
    
    # Rule 1: 1 per phone number in 1 min
    one_min_ago = now - timedelta(minutes=1)
    one_min_count = db.query(RateLimitEvent).filter(
        RateLimitEvent.identifier == phone_number,
        RateLimitEvent.event_type == "OTP_REQUEST",
        RateLimitEvent.created_at >= one_min_ago
    ).count()
    if one_min_count >= 1:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Please wait 1 minute before requesting another OTP."
        )
        
    # Rule 2: 5 per phone number in 1 hour
    one_hour_ago = now - timedelta(hours=1)
    one_hour_count = db.query(RateLimitEvent).filter(
        RateLimitEvent.identifier == phone_number,
        RateLimitEvent.event_type == "OTP_REQUEST",
        RateLimitEvent.created_at >= one_hour_ago
    ).count()
    if one_hour_count >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Exceeded limit of 5 OTP requests per hour for this phone number."
        )
        
    # Rule 3: 20 per phone number in 24 hours
    twenty_four_hours_ago = now - timedelta(hours=24)
    daily_count = db.query(RateLimitEvent).filter(
        RateLimitEvent.identifier == phone_number,
        RateLimitEvent.event_type == "OTP_REQUEST",
        RateLimitEvent.created_at >= twenty_four_hours_ago
    ).count()
    if daily_count >= 20:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Exceeded daily limit of 20 OTP requests for this phone number."
        )
        
    # Rule 4: 10 per IP in 1 hour
    ip_count = db.query(RateLimitEvent).filter(
        RateLimitEvent.identifier == ip_address,
        RateLimitEvent.event_type == "OTP_REQUEST",
        RateLimitEvent.created_at >= one_hour_ago
    ).count()
    if ip_count >= 10:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Exceeded limit of 10 OTP requests per hour from this IP address."
        )

    # Log the successful request events
    log_rate_limit_event(db, phone_number, "OTP_REQUEST", ip_address)
    log_rate_limit_event(db, ip_address, "OTP_REQUEST", ip_address)

def check_otp_verify_limits(db: Session, ip_address: str) -> None:
    """
    Enforces the rate limiting rules for verifying OTP:
    1. Max 5 verification attempts per IP in 15 Minutes.
    Raises HTTPException (429) if limit exceeded.
    """
    now = datetime.now(timezone.utc)
    fifteen_mins_ago = now - timedelta(minutes=15)
    
    count = db.query(RateLimitEvent).filter(
        RateLimitEvent.identifier == ip_address,
        RateLimitEvent.event_type == "OTP_VERIFY",
        RateLimitEvent.created_at >= fifteen_mins_ago
    ).count()
    
    if count >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many OTP verification attempts. Please wait 15 minutes."
        )
        
    # Log this verification attempt
    log_rate_limit_event(db, ip_address, "OTP_VERIFY", ip_address)
