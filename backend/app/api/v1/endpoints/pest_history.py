"""Pest detection history endpoints."""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.api import deps
from backend.app.models.user import User
from backend.app.schemas.pest_history import PestHistoryCreate, PestHistoryOut
from backend.app.services.pest_history_service import PestHistoryService

router = APIRouter()


@router.get("/", response_model=List[PestHistoryOut])
def list_pest_history(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get pest detection history for the authenticated user."""
    service = PestHistoryService(db)
    return service.list_history(current_user.id)


@router.post("/", response_model=PestHistoryOut, status_code=status.HTTP_201_CREATED)
def create_pest_history(
    data: PestHistoryCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Manually create a pest detection history record (source=MANUAL)."""
    from backend.app.models.enums import PestDetectionSource
    data.source = PestDetectionSource.MANUAL
    service = PestHistoryService(db)
    return service.create_history(current_user.id, data)
