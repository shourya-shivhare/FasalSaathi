from fastapi import APIRouter, Depends
from app.api import deps
from app.models.user import User
from app.schemas.user import User as UserSchema

router = APIRouter()

@router.get("/me", response_model=UserSchema)
def get_current_user(current_user: User = Depends(deps.get_current_user)):
    return current_user
