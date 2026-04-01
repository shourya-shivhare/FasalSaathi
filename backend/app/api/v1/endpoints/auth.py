from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.api import deps
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, RegisterRequest
from app.core.security import verify_password, get_password_hash, create_access_token

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(deps.get_db)):
    # Check if user exists
    db_user = db.query(User).filter(User.email == payload.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Hash password
    hashed_password = get_password_hash(payload.password)
    
    # Create new user
    new_user = User(
        email=payload.email,
        name=payload.name,
        hashed_password=hashed_password,
        phone=payload.phone
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create token
    access_token = create_access_token(subject=new_user.id)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(deps.get_db)):
    # Authenticate user
    db_user = db.query(User).filter(User.email == payload.email).first()
    if not db_user or not verify_password(payload.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not db_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    
    # Create token
    access_token = create_access_token(subject=db_user.id)
    return {"access_token": access_token, "token_type": "bearer"}
