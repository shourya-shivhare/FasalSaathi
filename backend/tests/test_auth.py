import pytest
from datetime import datetime, timezone, timedelta
from fastapi import status
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.models.farmer_profile import FarmerProfile
from backend.app.models.session import Session as UserSession
from backend.app.models.farm import Farm
from backend.app.models.crop_cycle import CropCycle
from backend.app.models.enums import AccountStatus, UserRole, PreferredLanguage, SoilType, IrrigationSource, CropCycleStatus, CropSeason, CropStage
from backend.app.models.security_event import SecurityEvent
from backend.app.services.context_builder import build_farmer_context
from backend.app.services.profile_completion import evaluate_profile_completion
from backend.app.core import security

def test_otp_send_validation(client):
    # Test invalid E.164 phone numbers
    response = client.post("/api/v1/auth/send-otp", json={"phone_number": "12345", "channel": "SMS"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    response = client.post("/api/v1/auth/send-otp", json={"phone_number": "9876543210", "channel": "SMS"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Test valid E.164 phone number
    response = client.post("/api/v1/auth/send-otp", json={"phone_number": "+919876543210", "channel": "SMS"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "pending"

def test_otp_verify_flow_new_user(client, db: Session):
    phone = "+919876543210"
    
    # 1. Verify OTP with correct code
    response = client.post(
        "/api/v1/auth/verify-otp",
        json={"phone_number": phone, "otp": "123456", "device_name": "Test Client"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["profile_completed"] is False
    assert data["role"] == "FARMER"
    
    # Check that cookie was set
    assert "refresh_token" in response.cookies
    refresh_cookie = response.cookies["refresh_token"]
    
    # Check user was created in DB
    user = db.query(User).filter(User.phone_number == phone).first()
    assert user is not None
    assert user.is_phone_verified is True
    assert user.farmer_profile is not None
    assert user.farmer_profile.profile_completed is False

def test_access_token_claims(client, db: Session):
    phone = "+919876543211"
    response = client.post(
        "/api/v1/auth/verify-otp",
        json={"phone_number": phone, "otp": "123456"}
    )
    data = response.json()
    access_token = data["access_token"]
    
    # Decode access token claims
    claims = security.decode_token(access_token)
    assert "sub" in claims
    assert "sid" in claims
    assert "role" in claims
    assert "jti" in claims
    # Crucial adjustment check: token_family_id MUST NOT be in standard access-token claims
    assert "token_family_id" not in claims

def test_refresh_token_rotation_and_replay_detection(client, db: Session):
    phone = "+919876543212"
    
    # 1. Login
    resp1 = client.post("/api/v1/auth/verify-otp", json={"phone_number": phone, "otp": "123456"})
    token1 = resp1.json()["access_token"]
    cookie1 = resp1.cookies["refresh_token"]
    
    # Get session details from DB
    claims = security.decode_token(cookie1)
    session_id = claims["sid"]
    token_family_id = claims["token_family_id"]
    
    db_sess = db.query(UserSession).filter(UserSession.id == session_id).first()
    assert db_sess is not None
    first_hash = db_sess.refresh_token_hash
    
    # 2. Perform silent token refresh
    client.cookies.set("refresh_token", cookie1)
    resp2 = client.post("/api/v1/auth/refresh")
    assert resp2.status_code == status.HTTP_200_OK
    data2 = resp2.json()
    assert "access_token" in data2
    cookie2 = resp2.cookies["refresh_token"]
    
    # Verify DB session rotated its hash
    db.refresh(db_sess)
    assert db_sess.refresh_token_hash != first_hash
    
    # 3. Replay attack: try using the OLD cookie1 again
    client.cookies.set("refresh_token", cookie1)
    resp3 = client.post("/api/v1/auth/refresh")
    assert resp3.status_code == status.HTTP_401_UNAUTHORIZED
    assert "reuse detected" in resp3.json()["detail"]
    
    # Verify that all sessions in token family were revoked in DB
    db.refresh(db_sess)
    assert db_sess.revoked_at is not None
    
    # Verify security event logged
    sec_event = db.query(SecurityEvent).filter(
        SecurityEvent.user_id == db_sess.user_id,
        SecurityEvent.event_type == "TOKEN_REUSE_DETECTED"
    ).first()
    assert sec_event is not None

def test_blocked_and_soft_deleted_users(client, db: Session):
    phone = "+919876543213"
    
    # Create blocked user
    user = User(
        phone_number=phone,
        name="Blocked Farmer",
        account_status=AccountStatus.BLOCKED,
        is_phone_verified=True
    )
    db.add(user)
    db.commit()
    
    # Trying to verify OTP for a blocked user should raise 403
    response = client.post("/api/v1/auth/verify-otp", json={"phone_number": phone, "otp": "123456"})
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # Soft deleted user check
    phone2 = "+919876543214"
    user2 = User(
        phone_number=phone2,
        name="Soft Deleted Farmer",
        deleted_at=datetime.now(timezone.utc),
        is_phone_verified=True
    )
    db.add(user2)
    db.commit()
    
    response2 = client.post("/api/v1/auth/verify-otp", json={"phone_number": phone2, "otp": "123456"})
    assert response2.status_code == status.HTTP_403_FORBIDDEN

def test_profile_completion_evaluator():
    profile = FarmerProfile(
        full_name="Rajesh Kumar",
        state="Haryana",
        district="Karnal",
        village="Taraori",
        farm_size_acres=4.5,
        preferred_language=PreferredLanguage.HINDI
    )
    assert evaluate_profile_completion(profile) is True
    
    # Missing field
    profile.village = None
    assert evaluate_profile_completion(profile) is False

def test_farmer_context_builder_prioritization(db: Session):
    # 1. Create User & Profile with crops_grown migration cache
    user = User(
        phone_number="+919876543215",
        name="Context Farmer",
        is_phone_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    profile = FarmerProfile(
        user_id=user.id,
        full_name="Context Farmer",
        state="Punjab",
        district="Amritsar",
        village="Rayya",
        farm_size_acres=3.0,
        preferred_language=PreferredLanguage.ENGLISH,
        soil_type=SoilType.SANDY,
        irrigation_source=IrrigationSource.RAINFED,
        crops_grown=["Cotton", "Rice"], # migration-compatibility cache
        profile_completed=True
    )
    db.add(profile)
    db.commit()
    
    # Verify builder falls back to crops_grown if no farms exist
    ctx_no_farm = build_farmer_context(user.id, db)
    assert ctx_no_farm["state"] == "Punjab"
    assert set(ctx_no_farm["active_crops"]) == {"Cotton", "Rice"}
    assert ctx_no_farm["soil_type"] == "SANDY"
    
    # 2. Add a Farm and an active CropCycle
    farm = Farm(
        user_id=user.id,
        farm_name="Main Farm",
        state="Haryana", # Farm has different details
        district="Panipat",
        village="Samalkha",
        total_area=5.0,
        soil_type=SoilType.BLACK,
        irrigation_source=IrrigationSource.BOREWELL
    )
    db.add(farm)
    db.commit()
    db.refresh(farm)
    
    cycle = CropCycle(
        farm_id=farm.id,
        crop_name="Wheat", # Active crop
        season=CropSeason.RABI,
        current_stage=CropStage.VEGETATIVE,
        status=CropCycleStatus.ACTIVE
    )
    db.add(cycle)
    db.commit()
    
    # Query context: Farm & CropCycle details MUST be prioritized
    ctx_with_farm = build_farmer_context(user.id, db)
    assert ctx_with_farm["state"] == "Haryana" # prioritized from Farm
    assert ctx_with_farm["district"] == "Panipat"
    assert ctx_with_farm["village"] == "Samalkha"
    assert ctx_with_farm["farm_size_acres"] == 5.0 # prioritized from Farm
    assert ctx_with_farm["soil_type"] == "BLACK" # prioritized from Farm
    assert ctx_with_farm["irrigation_source"] == "BOREWELL" # prioritized from Farm
    
    # Long term source of truth check: active_crops MUST contain "Wheat" (from CropCycle) and NOT "Cotton" or "Rice" (from crops_grown compatibility field)
    assert ctx_with_farm["active_crops"] == ["Wheat"]
