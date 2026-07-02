import hashlib
import bcrypt

# Monkeypatch bcrypt to truncate passwords exceeding 72 bytes.
# This fixes the compatibility crash in passlib 1.7.4's internal bug check with newer bcrypt.
_orig_hashpw = bcrypt.hashpw
def _safe_hashpw(password, salt):
    if len(password) > 72:
        password = password[:72]
    return _orig_hashpw(password, salt)
bcrypt.hashpw = _safe_hashpw

from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Dict, Any
from jose import jwt
from backend.app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
MAX_BCRYPT_PASSWORD_BYTES = 72

ALGORITHM = "HS256"

def validate_password_length(password: str) -> None:
    if len(password.encode("utf-8")) > MAX_BCRYPT_PASSWORD_BYTES:
        raise ValueError(
            f"Password must be at most {MAX_BCRYPT_PASSWORD_BYTES} bytes when UTF-8 encoded."
        )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    validate_password_length(plain_password)
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    validate_password_length(password)
    return pwd_context.hash(password)

def hash_refresh_token(token: str) -> str:
    """
    Hashes a refresh token using SHA-256.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def create_access_token(
    user_id: int,
    session_id: str,
    role: str,
    jti: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Generates a standard access token containing: sub, sid, role, and jti.
    Does NOT include token_family_id.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "exp": expire,
        "sub": str(user_id),
        "sid": str(session_id),
        "role": str(role),
        "jti": str(jti),
        "type": "access",
        "iat": datetime.now(timezone.utc)
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(
    user_id: int,
    session_id: str,
    token_family_id: str,
    jti: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Generates a refresh token containing: sub, sid, token_family_id, jti, type, iat, exp.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
    to_encode = {
        "exp": expire,
        "sub": str(user_id),
        "sid": str(session_id),
        "token_family_id": str(token_family_id),
        "jti": str(jti),
        "type": "refresh",
        "iat": datetime.now(timezone.utc)
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates the JWT signature and basic structures.
    Returns the payload dictionary or raises an exception.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
