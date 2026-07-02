from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.api import deps
from backend.app.models.user import User
from backend.app.models.farmer_profile import FarmerProfile
from backend.app.models.session import Session as UserSession
from backend.app.schemas.user import UserResponse, UserUpdate
from backend.app.schemas.session import SessionResponse
from backend.app.services.profile_completion import evaluate_profile_completion
from backend.app.services.audit import log_security_event

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def get_current_user(current_user: User = Depends(deps.get_current_user)):
    """
    Get current logged-in user profile details.
    UserResponse.populate_legacy_fields computes name/phone/is_onboarded
    from farmer_profile automatically.
    """
    from backend.app.services.cache_service import CacheService
    from backend.app.utils.cache_keys import make_profile_key

    cache_key = make_profile_key(current_user.id)
    cached = CacheService.get_sync(cache_key)
    if cached is not None:
        return cached

    # Parse and validate model
    res_obj = UserResponse.model_validate(current_user)
    res_dict = res_obj.model_dump()
    
    # Convert datetime objects to ISO strings for JSON serialization compatibility
    res_dict["created_at"] = res_dict["created_at"].isoformat()
    res_dict["updated_at"] = res_dict["updated_at"].isoformat()
    if res_dict.get("farmer_profile"):
        fp = res_dict["farmer_profile"]
        if fp.get("profile_created_at"):
            fp["profile_created_at"] = fp["profile_created_at"].isoformat()
        if fp.get("profile_updated_at"):
            fp["profile_updated_at"] = fp["profile_updated_at"].isoformat()

    CacheService.set_sync(cache_key, res_dict, ttl=900)
    return res_dict

@router.put("/me", response_model=UserResponse)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Update own user and farmer profile details.
    Auto-recalculates profile completion and updates version and timestamps.
    """
    update_data = user_in.model_dump(exclude_unset=True)
    
    # 1. Update user model base fields
    if "phone_number" in update_data:
        current_user.phone_number = update_data["phone_number"]
    if "username" in update_data:
        current_user.username = update_data["username"]
        
    # 2. Get or create farmer profile record
    profile = current_user.farmer_profile
    if not profile:
        profile = FarmerProfile(user_id=current_user.id, profile_version=1)
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
    # 3. Update farmer profile fields
    profile_fields = [
        "full_name", "age", "gender", "state", "district", "village",
        "farm_size_acres", "annual_income", "category", "preferred_language",
        "soil_type", "irrigation_source", "crops_grown"
    ]
    
    profile_updated = False
    for field in profile_fields:
        if field in update_data:
            setattr(profile, field, update_data[field])
            profile_updated = True
                    
    if profile_updated:
        profile.profile_version += 1
        profile.profile_completed = evaluate_profile_completion(profile)
        profile.profile_updated_at = datetime.now(timezone.utc)
        
    db.add(profile)
    db.add(current_user)
    db.commit()
    db.refresh(profile)
    db.refresh(current_user)
    
    # Invalidate profile and context caches
    from backend.app.services.cache_service import CacheService
    from backend.app.utils.cache_keys import make_profile_key, make_context_key, make_dashboard_key
    CacheService.delete_sync(make_profile_key(current_user.id))
    CacheService.delete_sync(make_context_key(current_user.id))
    CacheService.delete_sync(make_dashboard_key(current_user.id))
    CacheService.invalidate_pattern_sync(f"crop_rec:{current_user.id}:*")
    CacheService.invalidate_pattern_sync(f"scheme_rec:{current_user.id}:*")

    return current_user

@router.get("/me/sessions", response_model=List[SessionResponse])
def get_user_sessions(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get all active sessions for current user.
    """
    now = datetime.now(timezone.utc)
    active_sessions = db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.revoked_at.is_(None),
        UserSession.expires_at > now
    ).all()
    return active_sessions

@router.delete("/me/sessions/{session_id}")
def revoke_user_session(
    session_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Revoke a specific session for current user.
    """
    session = db.query(UserSession).filter(
        UserSession.id == session_id,
        UserSession.user_id == current_user.id,
        UserSession.revoked_at.is_(None)
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active session not found."
        )
        
    session.revoked_at = datetime.now(timezone.utc)
    db.commit()
    
    log_security_event(
        db=db,
        event_type="LOGOUT",
        user_id=current_user.id,
        metadata_json={"session_id": session_id, "action": "revoke_session_endpoint"}
    )
    
    return {"message": "Session successfully revoked."}
