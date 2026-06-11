"""Crop cycle management endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.api import deps
from backend.app.models.user import User
from backend.app.models.enums import CropCycleStatus, CropSeason
from backend.app.schemas.crop_cycle import CropCycleCreate, CropCycleUpdate, CropCycleOut, StageUpdate
from backend.app.services.crop_cycle_service import CropCycleService

router = APIRouter()


@router.post("/", response_model=CropCycleOut, status_code=status.HTTP_201_CREATED)
def create_crop_cycle(
    data: CropCycleCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Create a crop cycle for a farm owned by the user."""
    service = CropCycleService(db)
    cycle = service.create_cycle(current_user.id, data)
    if not cycle:
        raise HTTPException(status_code=404, detail="Farm not found or not owned by you")
    return cycle


@router.get("/", response_model=List[CropCycleOut])
def list_crop_cycles(
    farm_id: Optional[int] = Query(None),
    status: Optional[CropCycleStatus] = Query(None),
    season: Optional[CropSeason] = Query(None),
    year: Optional[int] = Query(None),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """List crop cycles with optional filters."""
    service = CropCycleService(db)
    return service.list_cycles(
        current_user.id,
        farm_id=farm_id,
        status=status,
        season=season.value if season else None,
        year=year,
    )


@router.get("/{cycle_id}", response_model=CropCycleOut)
def get_crop_cycle(
    cycle_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get a specific crop cycle."""
    service = CropCycleService(db)
    cycle = service.get_cycle(cycle_id, current_user.id)
    if not cycle:
        raise HTTPException(status_code=404, detail="Crop cycle not found")
    return cycle


@router.put("/{cycle_id}", response_model=CropCycleOut)
def update_crop_cycle(
    cycle_id: int,
    data: CropCycleUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Update a crop cycle."""
    service = CropCycleService(db)
    cycle = service.update_cycle(cycle_id, current_user.id, data)
    if not cycle:
        raise HTTPException(status_code=404, detail="Crop cycle not found")
    return cycle


@router.patch("/{cycle_id}/stage", response_model=CropCycleOut)
def update_crop_stage(
    cycle_id: int,
    data: StageUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Update only the growth stage of a crop cycle."""
    service = CropCycleService(db)
    cycle = service.update_stage(cycle_id, current_user.id, data.current_stage)
    if not cycle:
        raise HTTPException(status_code=404, detail="Crop cycle not found")
    return cycle


@router.post("/{cycle_id}/complete", response_model=CropCycleOut)
def complete_crop_cycle(
    cycle_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Mark a crop cycle as completed."""
    service = CropCycleService(db)
    cycle = service.complete_cycle(cycle_id, current_user.id, CropCycleStatus.COMPLETED)
    if not cycle:
        raise HTTPException(status_code=404, detail="Crop cycle not found")
    return cycle
