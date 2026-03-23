from fastapi import APIRouter, HTTPException
from app.schemas.auth import LoginRequest, TokenResponse, RegisterRequest

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
async def register(payload: RegisterRequest):
    # TODO: save user to DB, hash password
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    # TODO: validate credentials, return JWT
    raise HTTPException(status_code=501, detail="Not implemented yet")
