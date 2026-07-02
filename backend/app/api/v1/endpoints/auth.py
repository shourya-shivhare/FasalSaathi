import uuid
from typing import Optional
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends, status, Request, Response, Cookie
from sqlalchemy.orm import Session
from backend.app.api import deps
from backend.app.models.user import User
from backend.app.models.farmer_profile import FarmerProfile
from backend.app.models.session import Session as UserSession
from backend.app.models.enums import AccountStatus, UserRole
from backend.app.schemas.auth import (
    SignupSendOtpRequest,
    SignupVerifyRequest,
    LoginRequest,
    SendOtpResponse,
    TokenResponse
)
from backend.app.services.twilio_verify import twilio_verify_service
from backend.app.services.rate_limiter import (
    check_otp_send_limits,
    check_otp_verify_limits,
    check_login_limits
)
from backend.app.services.audit import log_security_event, get_auth_metrics
from backend.app.core import security
from backend.app.core.config import settings

router = APIRouter()

@router.post("/signup/send-otp", response_model=SendOtpResponse)
def signup_send_otp(
    payload: SignupSendOtpRequest,
    request: Request,
    db: Session = Depends(deps.get_db)
):
    ip_address = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("user-agent", "")
    
    # 1. Enforce rate limits
    check_otp_send_limits(db, payload.phone_number, ip_address)
    
    # 2. Validate uniqueness
    existing_user_name = db.query(User).filter(User.username == payload.username).first()
    if existing_user_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already registered."
        )
        
    existing_user_phone = db.query(User).filter(User.phone_number == payload.phone_number).first()
    if existing_user_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number is already registered."
        )
        
    # 3. Call Twilio Verify API
    status_msg = twilio_verify_service.send_otp(payload.phone_number, payload.channel.value.lower())
    
    # 4. Log security event
    log_security_event(
        db=db,
        event_type="OTP_SENT",
        user_id=None,
        ip_address=ip_address,
        user_agent=user_agent,
        metadata_json={"phone_number": payload.phone_number, "channel": payload.channel.value, "flow": "signup"}
    )
    
    return {
        "status": status_msg,
        "message": f"OTP successfully sent via {payload.channel.value}."
    }

@router.post("/signup/verify", response_model=TokenResponse)
def signup_verify(
    payload: SignupVerifyRequest,
    request: Request,
    response: Response,
    db: Session = Depends(deps.get_db)
):
    ip_address = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("user-agent", "")
    
    # 1. Enforce rate limits
    check_otp_verify_limits(db, ip_address)
    
    # 2. Validate uniqueness again to prevent race condition
    existing_user_name = db.query(User).filter(User.username == payload.username).first()
    if existing_user_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already registered."
        )
        
    existing_user_phone = db.query(User).filter(User.phone_number == payload.phone_number).first()
    if existing_user_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number is already registered."
        )
        
    # 3. Verify OTP
    is_valid = twilio_verify_service.verify_otp(payload.phone_number, payload.otp)
    
    if not is_valid:
        # Increment metric & log failure
        log_security_event(
            db=db,
            event_type="OTP_FAILED",
            ip_address=ip_address,
            user_agent=user_agent,
            metadata_json={"phone_number": payload.phone_number, "flow": "signup"}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP code."
        )
        
    # Log successful verification
    log_security_event(
        db=db,
        event_type="OTP_VERIFIED",
        ip_address=ip_address,
        user_agent=user_agent,
        metadata_json={"phone_number": payload.phone_number, "flow": "signup"}
    )
    
    # 4. Create User
    hashed_pwd = security.get_password_hash(payload.password)
    user = User(
        username=payload.username,
        phone_number=payload.phone_number,
        password_hash=hashed_pwd,
        status=AccountStatus.ACTIVE,
        role=UserRole.FARMER
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create Farmer Profile
    profile = FarmerProfile(
        user_id=user.id,
        full_name=payload.username,
        profile_completed=False,
        profile_version=1
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    log_security_event(
        db=db,
        event_type="REGISTRATION_CREATED",
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent
    )
        
    # 5. Create Session
    session_id = str(uuid.uuid4())
    token_family_id = str(uuid.uuid4())
    refresh_jti = str(uuid.uuid4())
    access_jti = str(uuid.uuid4())
    
    # Issue Refresh Token (contains token_family_id)
    refresh_token = security.create_refresh_token(
        user_id=user.id,
        session_id=session_id,
        token_family_id=token_family_id,
        jti=refresh_jti
    )
    
    # Hash refresh token
    refresh_hash = security.hash_refresh_token(refresh_token)
    
    # Expiration datetime
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Create DB session
    new_session = UserSession(
        id=session_id,
        user_id=user.id,
        refresh_token_hash=refresh_hash,
        token_family_id=token_family_id,
        device_info=user_agent[:256] if user_agent else None,
        device_name=payload.device_name[:128] if payload.device_name else None,
        is_trusted_device=payload.is_trusted_device,
        user_agent=user_agent,
        ip_address=ip_address,
        expires_at=expires_at
    )
    db.add(new_session)
    db.commit()
    
    # Issue Access Token (contains sid and role, excludes token_family_id)
    access_token = security.create_access_token(
        user_id=user.id,
        session_id=session_id,
        role=user.role.value,
        jti=access_jti
    )
    
    log_security_event(
        db=db,
        event_type="LOGIN_SUCCESS",
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
        metadata_json={"session_id": session_id, "is_new_user": True}
    )
    
    # Set Refresh Token in secure HTTPOnly Cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "profile_completed": False,
        "role": user.role.value
    }

@router.post("/refresh", response_model=TokenResponse)
def refresh_token_route(
    request: Request,
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    db: Session = Depends(deps.get_db)
):
    ip_address = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("user-agent", "")
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token cookie missing."
        )
        
    try:
        payload = security.decode_token(refresh_token)
        user_id = int(payload.get("sub"))
        session_id = payload.get("sid")
        token_family_id = payload.get("token_family_id")
        token_type = payload.get("type")
        
        if not user_id or not session_id or not token_family_id or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token claims."
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token."
        )
        
    # Query database session
    db_session = db.query(UserSession).filter(UserSession.id == session_id).first()
    incoming_hash = security.hash_refresh_token(refresh_token)
    
    # 1. Replay attack / reuse detection
    if db_session:
        # If session is revoked or hash doesn't match, or expired
        is_revoked = db_session.revoked_at is not None
        expires_at = db_session.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        is_expired = expires_at < datetime.now(timezone.utc)
        hash_mismatch = db_session.refresh_token_hash != incoming_hash
        
        if is_revoked or is_expired or hash_mismatch:
            # Replay / theft warning!
            # Revoke all sessions in the same token family
            family_sessions = db.query(UserSession).filter(
                UserSession.token_family_id == token_family_id
            ).all()
            for s in family_sessions:
                s.revoked_at = datetime.now(timezone.utc)
            db.commit()
            
            # Log security breach attempt
            log_security_event(
                db=db,
                event_type="TOKEN_REUSE_DETECTED",
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata_json={
                    "session_id": session_id,
                    "token_family_id": token_family_id,
                    "reason": "Revoked session reuse or hash mismatch detected"
                }
            )
            
            # Clear cookie
            response.delete_cookie(key="refresh_token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Security alert: session credentials reuse detected. All sessions revoked."
            )
    else:
        # Session record doesn't exist in DB at all, but we have a valid token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found."
        )

    # 2. Verify user status
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.status != AccountStatus.ACTIVE:
        response.delete_cookie(key="refresh_token")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated or deleted."
        )
        
    # 3. Rotate Refresh Token
    new_refresh_jti = str(uuid.uuid4())
    new_access_jti = str(uuid.uuid4())
    
    new_refresh_token = security.create_refresh_token(
        user_id=user_id,
        session_id=session_id,
        token_family_id=token_family_id,
        jti=new_refresh_jti
    )
    
    # Update DB Session hash
    db_session.refresh_token_hash = security.hash_refresh_token(new_refresh_token)
    db_session.last_used_at = datetime.now(timezone.utc)
    db.commit()
    
    # Issue new Access Token (excludes token_family_id)
    new_access_token = security.create_access_token(
        user_id=user_id,
        session_id=session_id,
        role=user.role.value,
        jti=new_access_jti
    )
    
    log_security_event(
        db=db,
        event_type="TOKEN_REFRESH",
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        metadata_json={"session_id": session_id}
    )
    
    # Set rotated cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    profile = db.query(FarmerProfile).filter(FarmerProfile.user_id == user.id).first()
    profile_completed = profile.profile_completed if profile else False
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "profile_completed": profile_completed,
        "role": user.role.value
    }

@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    current_user: User = Depends(deps.get_optional_current_user),
    db: Session = Depends(deps.get_db)
):
    ip_address = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("user-agent", "")
    
    # Attempt to read session from refresh token
    session_id = None
    user_id = current_user.id if current_user else None
    
    if refresh_token:
        try:
            payload = security.decode_token(refresh_token)
            session_id = payload.get("sid")
            if not user_id:
                user_id = int(payload.get("sub"))
        except Exception:
            pass

    if session_id:
        db_session = db.query(UserSession).filter(UserSession.id == session_id).first()
        if db_session:
            db_session.revoked_at = datetime.now(timezone.utc)
            db.commit()
            
    # Delete refresh token cookie
    response.delete_cookie(key="refresh_token")
    
    if user_id:
        log_security_event(
            db=db,
            event_type="LOGOUT",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata_json={"session_id": session_id}
        )
        
    return {"message": "Successfully logged out."}

@router.post("/logout-all")
def logout_all(
    request: Request,
    response: Response,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    ip_address = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("user-agent", "")
    
    # Revoke all sessions
    sessions = db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.revoked_at.is_(None)
    ).all()
    
    for s in sessions:
        s.revoked_at = datetime.now(timezone.utc)
    db.commit()
    
    # Delete cookie
    response.delete_cookie(key="refresh_token")
    
    log_security_event(
        db=db,
        event_type="LOGOUT_ALL",
        user_id=current_user.id,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return {"message": "Successfully logged out from all devices."}

@router.get("/metrics")
def get_metrics(
    db: Session = Depends(deps.get_db),
    admin_user: User = Depends(deps.get_current_admin)
):
    """
    Observability endpoint to get authentication event metrics (Admin only).
    """
    return get_auth_metrics(db)

@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(deps.get_db)
):
    ip_address = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("user-agent", "")
    
    # 1. Enforce rate limits
    check_login_limits(db, payload.username, ip_address)
    
    # 2. Fetch user by username
    user = db.query(User).filter(User.username == payload.username).first()
    if not user:
        log_security_event(
            db=db,
            event_type="LOGIN_FAILED",
            ip_address=ip_address,
            user_agent=user_agent,
            metadata_json={"username": payload.username, "reason": "User not found"}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password."
        )
        
    # 3. Check password matches hash
    if not security.verify_password(payload.password, user.password_hash):
        log_security_event(
            db=db,
            event_type="LOGIN_FAILED",
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata_json={"username": payload.username, "reason": "Password mismatch"}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password."
        )
        
    # 4. Check status
    if user.status != AccountStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated, suspended, or deleted."
        )
        
    # 5. Create Session
    session_id = str(uuid.uuid4())
    token_family_id = str(uuid.uuid4())
    refresh_jti = str(uuid.uuid4())
    access_jti = str(uuid.uuid4())
    
    # Issue Refresh Token (contains token_family_id)
    refresh_token = security.create_refresh_token(
        user_id=user.id,
        session_id=session_id,
        token_family_id=token_family_id,
        jti=refresh_jti
    )
    
    # Hash refresh token
    refresh_hash = security.hash_refresh_token(refresh_token)
    
    # Expiration datetime
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Create DB session
    new_session = UserSession(
        id=session_id,
        user_id=user.id,
        refresh_token_hash=refresh_hash,
        token_family_id=token_family_id,
        device_info=user_agent[:256] if user_agent else None,
        device_name=payload.device_name[:128] if payload.device_name else None,
        is_trusted_device=payload.is_trusted_device,
        user_agent=user_agent,
        ip_address=ip_address,
        expires_at=expires_at
    )
    db.add(new_session)
    db.commit()
    
    # Issue Access Token (contains sid and role, excludes token_family_id)
    access_token = security.create_access_token(
        user_id=user.id,
        session_id=session_id,
        role=user.role.value,
        jti=access_jti
    )
    
    # Log audit events
    log_security_event(
        db=db,
        event_type="LOGIN_SUCCESS",
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
        metadata_json={"session_id": session_id, "is_new_user": False}
    )
    
    log_security_event(
        db=db,
        event_type="SESSION_CREATED",
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
        metadata_json={"session_id": session_id}
    )
    
    if payload.is_trusted_device:
        log_security_event(
            db=db,
            event_type="TRUSTED_DEVICE",
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata_json={"session_id": session_id, "device_name": payload.device_name}
        )
    
    # Set Refresh Token in secure HTTPOnly Cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    # Get profile completed status
    profile = db.query(FarmerProfile).filter(FarmerProfile.user_id == user.id).first()
    profile_completed = profile.profile_completed if profile else False
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "profile_completed": profile_completed,
        "role": user.role.value
    }

