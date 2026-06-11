import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from backend.app.models.session import Session as UserSession
from backend.app.models.security_event import SecurityEvent

logger = logging.getLogger(__name__)

def cleanup_expired_sessions(db: Session) -> int:
    """
    Deletes sessions where expires_at < now().
    Returns the number of deleted records.
    """
    now = datetime.now(timezone.utc)
    try:
        deleted = db.query(UserSession).filter(UserSession.expires_at < now).delete()
        db.commit()
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} expired sessions.")
        return deleted
    except Exception as e:
        logger.error(f"Error cleaning up expired sessions: {e}")
        db.rollback()
        return 0

def cleanup_revoked_sessions(db: Session) -> int:
    """
    Deletes sessions where revoked_at is not null.
    Returns the number of deleted records.
    """
    try:
        deleted = db.query(UserSession).filter(UserSession.revoked_at.isnot(None)).delete()
        db.commit()
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} revoked sessions.")
        return deleted
    except Exception as e:
        logger.error(f"Error cleaning up revoked sessions: {e}")
        db.rollback()
        return 0

def cleanup_old_security_events(db: Session) -> int:
    """
    Prunes security_events older than 90 days.
    Returns the number of deleted records.
    """
    threshold = datetime.now(timezone.utc) - timedelta(days=90)
    try:
        deleted = db.query(SecurityEvent).filter(SecurityEvent.created_at < threshold).delete()
        db.commit()
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} security events older than 90 days.")
        return deleted
    except Exception as e:
        logger.error(f"Error cleaning up old security events: {e}")
        db.rollback()
        return 0

def run_all_cleanup_jobs(db: Session) -> dict:
    """
    Runs all cleanup tasks and returns results.
    """
    return {
        "expired_sessions_cleaned": cleanup_expired_sessions(db),
        "revoked_sessions_cleaned": cleanup_revoked_sessions(db),
        "old_security_events_cleaned": cleanup_old_security_events(db)
    }
