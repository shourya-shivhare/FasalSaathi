from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.models.crop import Crop
from app.schemas.crop import Crop as CropSchema, CropCreate, CropUpdate
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[CropSchema])
def list_crops(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db)
):
    """Retrieve a list of all crops."""
    crops = db.query(Crop).offset(skip).limit(limit).all()
    return crops

@router.get("/{crop_id}", response_model=CropSchema)
def get_crop(
    crop_id: int,
    db: Session = Depends(deps.get_db)
):
    """Retrieve a specific crop by ID."""
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    return crop

@router.post("/", response_model=CropSchema, status_code=status.HTTP_201_CREATED)
def create_crop(
    crop_in: CropCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Create a new crop entry (Requires Authentication)."""
    # Check if a crop with the same name already exists
    existing_crop = db.query(Crop).filter(Crop.name == crop_in.name).first()
    if existing_crop:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A crop with this name already exists."
        )
    
    db_crop = Crop(**crop_in.model_dump())
    db.add(db_crop)
    db.commit()
    db.refresh(db_crop)
    return db_crop

@router.put("/{crop_id}", response_model=CropSchema)
def update_crop(
    crop_id: int,
    crop_in: CropUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Update a crop entry (Requires Authentication)."""
    db_crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not db_crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    
    update_data = crop_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_crop, field, value)
        
    db.add(db_crop)
    db.commit()
    db.refresh(db_crop)
    return db_crop

@router.delete("/{crop_id}", response_model=CropSchema)
def delete_crop(
    crop_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Delete a crop entry (Requires Authentication)."""
    db_crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not db_crop:
        raise HTTPException(status_code=404, detail="Crop not found")
        
    db.delete(db_crop)
    db.commit()
    return db_crop
