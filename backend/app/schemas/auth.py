from pydantic import BaseModel, EmailStr, constr


class LoginRequest(BaseModel):
    email: EmailStr
    password: constr(max_length=72)


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: constr(max_length=72)
    phone: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
