"""Farm management endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api import deps
from backend.app.models.user import User
from backend.app.schemas.farm import FarmCreate, FarmUpdate, FarmOut
from backend.app.services.farm_service import FarmService

router = APIRouter()


@router.post("/", response_model=FarmOut, status_code=status.HTTP_201_CREATED)
def create_farm(
    data: FarmCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Create a new farm for the authenticated user."""
    service = FarmService(db)
    farm = service.create_farm(current_user.id, data)
    return service.get_farm_with_active_crop_count(farm)


@router.get("/", response_model=List[FarmOut])
def list_farms(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """List all farms for the authenticated user."""
    service = FarmService(db)
    farms = service.list_farms(current_user.id)
    return [service.get_farm_with_active_crop_count(f) for f in farms]


@router.get("/{farm_id}", response_model=FarmOut)
def get_farm(
    farm_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get a specific farm by ID."""
    service = FarmService(db)
    farm = service.get_farm(farm_id, current_user.id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return service.get_farm_with_active_crop_count(farm)


@router.put("/{farm_id}", response_model=FarmOut)
def update_farm(
    farm_id: int,
    data: FarmUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Update an existing farm."""
    service = FarmService(db)
    farm = service.update_farm(farm_id, current_user.id, data)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return service.get_farm_with_active_crop_count(farm)


@router.delete("/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_farm(
    farm_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Delete a farm and all its crop cycles."""
    service = FarmService(db)
    deleted = service.delete_farm(farm_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Farm not found")
