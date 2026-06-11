import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.security_event import SecurityEvent
from backend.app.models.session import Session as UserSession

logger = logging.getLogger(__name__)

# In-memory metrics counter for authentication observability
auth_metrics = {
    "otp_sent_count": 0,
    "otp_verified_count": 0,
    "otp_failed_count": 0,
    "login_success_count": 0,
    "login_failure_count": 0,
    "refresh_token_usage": 0
}

def log_security_event(
    db: Session,
    event_type: str,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    metadata_json: Optional[Dict[str, Any]] = None
) -> None:
    """
    Logs a security event to the database and increments the in-memory observability metrics.
    """
    try:
        # Save to database
        event = SecurityEvent(
            user_id=user_id,
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata_json=metadata_json,
            created_at=datetime.now(timezone.utc)
        )
        db.add(event)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to log security event {event_type} in DB: {e}")
        db.rollback()

    # Update in-memory metrics
    if event_type == "OTP_SENT":
        auth_metrics["otp_sent_count"] += 1
    elif event_type == "OTP_VERIFIED":
        auth_metrics["otp_verified_count"] += 1
    elif event_type == "OTP_FAILED":
        auth_metrics["otp_failed_count"] += 1
    elif event_type == "LOGIN_SUCCESS":
        auth_metrics["login_success_count"] += 1
    elif event_type in ("LOGIN_FAILED", "OTP_FAILED"):
        auth_metrics["login_failure_count"] += 1
    elif event_type == "TOKEN_REFRESH":
        auth_metrics["refresh_token_usage"] += 1

def get_auth_metrics(db: Session) -> Dict[str, Any]:
    """
    Returns the accumulated metrics, querying the active session count in real-time from the database.
    """
    now = datetime.now(timezone.utc)
    active_session_count = db.query(UserSession).filter(
        UserSession.revoked_at.is_(None),
        UserSession.expires_at > now
    ).count()
    
    return {
        "otp_sent_count": auth_metrics["otp_sent_count"],
        "otp_verified_count": auth_metrics["otp_verified_count"],
        "otp_failed_count": auth_metrics["otp_failed_count"],
        "login_success_count": auth_metrics["login_success_count"],
        "login_failure_count": auth_metrics["login_failure_count"],
        "active_session_count": active_session_count,
        "refresh_token_usage": auth_metrics["refresh_token_usage"]
    }
