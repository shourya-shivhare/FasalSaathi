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

def test_signup_otp_send_validation(client):
    # Test invalid E.164 phone numbers
    response = client.post(
        "/api/v1/auth/signup/send-otp",
        json={"username": "testuser", "phone_number": "12345", "password": "mypassword", "channel": "SMS"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    response = client.post(
        "/api/v1/auth/signup/send-otp",
        json={"username": "testuser", "phone_number": "9876543210", "password": "mypassword", "channel": "SMS"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Test valid E.164 phone number
    response = client.post(
        "/api/v1/auth/signup/send-otp",
        json={"username": "testuser", "phone_number": "+919876543210", "password": "mypassword", "channel": "SMS"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "pending"

def test_signup_verify_flow_new_user(client, db: Session):
    username = "newfarmer"
    phone = "+919876543210"
    pwd = "securepassword"
    
    # 1. Verify OTP with correct code
    response = client.post(
        "/api/v1/auth/signup/verify",
        json={"username": username, "phone_number": phone, "password": pwd, "otp": "123456", "device_name": "Test Client"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["profile_completed"] is False
    assert data["role"] == "FARMER"
    
    # Check that cookie was set
    assert "refresh_token" in response.cookies
    
    # Check user was created in DB
    user = db.query(User).filter(User.phone_number == phone).first()
    assert user is not None
    assert user.username == username
    assert security.verify_password(pwd, user.password_hash)
    assert user.farmer_profile is not None
    assert user.farmer_profile.profile_completed is False

def test_access_token_claims(client, db: Session):
    username = "claimsuser"
    phone = "+919876543211"
    pwd = "password123"
    
    response = client.post(
        "/api/v1/auth/signup/verify",
        json={"username": username, "phone_number": phone, "password": pwd, "otp": "123456"}
    )
    data = response.json()
    access_token = data["access_token"]
    
    # Decode access token claims
    claims = security.decode_token(access_token)
    assert "sub" in claims
    assert "sid" in claims
    assert "role" in claims
    assert "jti" in claims
    assert "token_family_id" not in claims

def test_refresh_token_rotation_and_replay_detection(client, db: Session):
    username = "rotateuser"
    phone = "+919876543212"
    pwd = "password123"
    
    # 1. Signup
    resp1 = client.post(
        "/api/v1/auth/signup/verify",
        json={"username": username, "phone_number": phone, "password": pwd, "otp": "123456"}
    )
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

def test_blocked_users(client, db: Session):
    username = "blockeduser"
    phone = "+919876543213"
    pwd = "password123"
    
    # Create blocked user
    user = User(
        username=username,
        phone_number=phone,
        password_hash=security.get_password_hash(pwd),
        status=AccountStatus.BLOCKED,
        role=UserRole.FARMER
    )
    db.add(user)
    db.commit()
    
    # Trying to login a blocked user should raise 403
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": pwd}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_login_flow(client, db: Session):
    username = "loginfarmer"
    phone = "+919876543214"
    pwd = "securepassword"
    
    # Create active user
    user = User(
        username=username,
        phone_number=phone,
        password_hash=security.get_password_hash(pwd),
        status=AccountStatus.ACTIVE,
        role=UserRole.FARMER
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create Farmer Profile
    profile = FarmerProfile(
        user_id=user.id,
        full_name=username,
        profile_completed=False,
        profile_version=1
    )
    db.add(profile)
    db.commit()
    
    # Attempt login with invalid password
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": "wrongpassword"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Verify LOGIN_FAILED event was logged
    fail_event = db.query(SecurityEvent).filter(
        SecurityEvent.user_id == user.id,
        SecurityEvent.event_type == "LOGIN_FAILED"
    ).first()
    assert fail_event is not None
    assert fail_event.metadata_json["reason"] == "Password mismatch"
    
    # Attempt login with non-existent user
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "doesnotexist", "password": "somepassword"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Verify LOGIN_FAILED event was logged with user_id as None
    none_user_fail_events = db.query(SecurityEvent).filter(
        SecurityEvent.user_id.is_(None),
        SecurityEvent.event_type == "LOGIN_FAILED"
    ).all()
    none_user_fail_event = next(
        (e for e in none_user_fail_events if e.metadata_json and e.metadata_json.get("username") == "doesnotexist"),
        None
    )
    assert none_user_fail_event is not None

    
    # Attempt login with correct credentials, requesting device trust
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": username,
            "password": pwd,
            "device_name": "Test Device",
            "is_trusted_device": True
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["profile_completed"] is False
    assert data["role"] == "FARMER"
    assert "refresh_token" in response.cookies
    
    # Verify security events: LOGIN_SUCCESS, SESSION_CREATED, TRUSTED_DEVICE
    success_event = db.query(SecurityEvent).filter(
        SecurityEvent.user_id == user.id,
        SecurityEvent.event_type == "LOGIN_SUCCESS"
    ).first()
    assert success_event is not None
    
    session_event = db.query(SecurityEvent).filter(
        SecurityEvent.user_id == user.id,
        SecurityEvent.event_type == "SESSION_CREATED"
    ).first()
    assert session_event is not None
    
    trusted_event = db.query(SecurityEvent).filter(
        SecurityEvent.user_id == user.id,
        SecurityEvent.event_type == "TRUSTED_DEVICE"
    ).first()
    assert trusted_event is not None
    assert trusted_event.metadata_json["device_name"] == "Test Device"

def test_login_rate_limiting(client, db: Session):
    from backend.app.core.config import settings
    
    username = "ratelimitedfarmer"
    phone = "+919876543219"
    pwd = "password123"
    
    user = User(
        username=username,
        phone_number=phone,
        password_hash=security.get_password_hash(pwd),
        status=AccountStatus.ACTIVE,
        role=UserRole.FARMER
    )
    db.add(user)
    db.commit()
    
    # Toggle rate limiter ON for test
    original_setting = settings.ENABLE_RATE_LIMIT
    settings.ENABLE_RATE_LIMIT = True
    
    try:
        # Perform 5 failed login attempts
        for _ in range(5):
            response = client.post(
                "/api/v1/auth/login",
                json={"username": username, "password": "wrongpassword"}
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            
        # 6th attempt should trigger 429
        response = client.post(
            "/api/v1/auth/login",
            json={"username": username, "password": pwd}
        )
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Too many login attempts" in response.json()["detail"]
    finally:
        # Revert rate limiter setting
        settings.ENABLE_RATE_LIMIT = original_setting


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
    username = "contextfarmer"
    phone = "+919876543215"
    pwd = "password123"
    
    # 1. Create User & Profile
    user = User(
        username=username,
        phone_number=phone,
        password_hash=security.get_password_hash(pwd),
        status=AccountStatus.ACTIVE,
        role=UserRole.FARMER
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
        crops_grown=["Cotton", "Rice"],
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
