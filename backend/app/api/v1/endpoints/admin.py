from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timezone
from backend.app.api import deps
from backend.app.models.user import User
from backend.app.models.session import Session as UserSession
from backend.app.models.security_event import SecurityEvent
from backend.app.models.enums import AccountStatus
from backend.app.services.audit import get_auth_metrics, log_security_event

router = APIRouter()

# Enforce ADMIN role on all router endpoints
admin_deps = [Depends(deps.get_current_admin)]

@router.get("/metrics", response_model=Dict[str, Any], dependencies=admin_deps)
def admin_metrics(db: Session = Depends(deps.get_db)):
    """
    Get identity and session metrics (Admin only).
    """
    return get_auth_metrics(db)

@router.get("/security-logs", response_model=List[Dict[str, Any]], dependencies=admin_deps)
def get_security_logs(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(deps.get_db)
):
    """
    Get the list of recent security events / audit logs (Admin only).
    """
    logs = db.query(SecurityEvent).order_by(
        SecurityEvent.created_at.desc()
    ).limit(limit).offset(offset).all()
    
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "event_type": log.event_type,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "metadata_json": log.metadata_json,
            "created_at": log.created_at
        }
        for log in logs
    ]

@router.post("/users/{user_id}/status", dependencies=admin_deps)
def update_user_status(
    user_id: int,
    status_val: AccountStatus,
    db: Session = Depends(deps.get_db),
    admin_user: User = Depends(deps.get_current_admin)
):
    """
    Update a user's account status (block, suspend, delete, or activate).
    (Admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
        
    old_status = user.account_status
    user.account_status = status_val
    
    # If soft-deleted, set deleted_at timestamp
    if status_val == AccountStatus.DELETED:
        user.deleted_at = datetime.now(timezone.utc)
    else:
        user.deleted_at = None
        
    db.commit()
    
    # Log audit event
    log_security_event(
        db=db,
        event_type=f"ACCOUNT_{status_val.value}",
        user_id=user.id,
        metadata_json={
            "admin_user_id": admin_user.id,
            "old_status": old_status.value,
            "new_status": status_val.value
        }
    )
    
    # If blocking/suspending/deleting, force-revoke all their sessions
    if status_val in (AccountStatus.BLOCKED, AccountStatus.SUSPENDED, AccountStatus.DELETED):
        sessions = db.query(UserSession).filter(
            UserSession.user_id == user.id,
            UserSession.revoked_at.is_(None)
        ).all()
        for s in sessions:
            s.revoked_at = datetime.now(timezone.utc)
        db.commit()
        
    return {
        "message": f"Successfully updated user status from {old_status.value} to {status_val.value}.",
        "user_id": user_id,
        "status": status_val.value
    }

@router.post("/users/{user_id}/revoke-sessions", dependencies=admin_deps)
def force_logout_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    admin_user: User = Depends(deps.get_current_admin)
):
    """
    Forcefully terminate all active login sessions for a user.
    (Admin only).
    """
    sessions = db.query(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.revoked_at.is_(None)
    ).all()
    
    count = len(sessions)
    for s in sessions:
        s.revoked_at = datetime.now(timezone.utc)
    db.commit()
    
    log_security_event(
        db=db,
        event_type="LOGOUT_ALL",
        user_id=user_id,
        metadata_json={
            "admin_user_id": admin_user.id,
            "reason": "Force revoked by admin"
        }
    )
    
    return {
        "message": f"Successfully revoked {count} active sessions for user.",
        "user_id": user_id
    }
