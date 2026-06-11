import re
from pydantic import BaseModel, field_validator, constr
from typing import Optional
from backend.app.models.enums import VerificationChannel

# Regex for validating E.164 phone format
E164_REGEX = re.compile(r"^\+[1-9]\d{1,14}$")

class SendOtpRequest(BaseModel):
    phone_number: str
    channel: VerificationChannel = VerificationChannel.SMS

    @field_validator("phone_number")
    @classmethod
    def validate_e164(cls, value: str) -> str:
        value_stripped = value.strip()
        if not E164_REGEX.match(value_stripped):
            raise ValueError(
                "Phone number must be in E.164 format (e.g., +919876543210)."
            )
        return value_stripped

class VerifyOtpRequest(BaseModel):
    phone_number: str
    otp: constr(min_length=4, max_length=10) # twilio codes are usually 4 to 10 chars
    device_name: Optional[str] = "Web Browser"
    is_trusted_device: Optional[bool] = False

    @field_validator("phone_number")
    @classmethod
    def validate_e164(cls, value: str) -> str:
        value_stripped = value.strip()
        if not E164_REGEX.match(value_stripped):
            raise ValueError(
                "Phone number must be in E.164 format (e.g., +919876543210)."
            )
        return value_stripped

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    profile_completed: bool = False
    role: str = "FARMER"

class SendOtpResponse(BaseModel):
    status: str
    message: str

# Keep legacy schemas for backward compatibility if needed in dependencies/other routers
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    phone: Optional[str] = None
