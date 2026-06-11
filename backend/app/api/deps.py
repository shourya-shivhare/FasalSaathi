from datetime import datetime, timezone
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from backend.app.db.database import SessionLocal
from backend.app.core.config import settings
from backend.app.core import security
from backend.app.models.user import User
from backend.app.models.session import Session as UserSession
from backend.app.models.enums import AccountStatus, UserRole

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = security.decode_token(token)
        user_id = payload.get("sub")
        session_id = payload.get("sid")
        token_type = payload.get("type")
        
        if not user_id or not session_id or token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token claims",
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
        
    # Check session status in DB
    now = datetime.now(timezone.utc)
    db_session = db.query(UserSession).filter(
        UserSession.id == session_id,
        UserSession.user_id == int(user_id),
        UserSession.revoked_at.is_(None),
        UserSession.expires_at > now
    ).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired or has been revoked.",
        )
        
    # Fetch user
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Check soft-deleted or non-active accounts
    if user.deleted_at is not None or user.account_status != AccountStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated, suspended, or deleted."
        )
        
    return user

def get_optional_current_user(
    db: Session = Depends(get_db), token: str | None = Depends(reusable_oauth2)
) -> User | None:
    if not token:
        return None
    try:
        payload = security.decode_token(token)
        user_id = payload.get("sub")
        session_id = payload.get("sid")
        token_type = payload.get("type")
        if not user_id or not session_id or token_type != "access":
            return None
            
        now = datetime.now(timezone.utc)
        db_session = db.query(UserSession).filter(
            UserSession.id == session_id,
            UserSession.revoked_at.is_(None),
            UserSession.expires_at > now
        ).first()
        if not db_session:
            return None
            
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user or user.deleted_at is not None or user.account_status != AccountStatus.ACTIVE:
            return None
            
        return user
    except Exception:
        return None

def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency that enforces the user has the ADMIN role.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required."
        )
    return current_user
