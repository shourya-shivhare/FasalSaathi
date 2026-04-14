from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate
from app.api.deps import get_db

router = APIRouter()

@router.get("/me", response_model=UserSchema)
def get_current_user(current_user: User = Depends(deps.get_current_user)):
    return current_user

@router.put("/me", response_model=UserSchema)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_user)
):
    """Update own user information."""
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data:
        # TODO: use hash_password helper from core
        current_user.hashed_password = update_data["password"]
        del update_data["password"]
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
