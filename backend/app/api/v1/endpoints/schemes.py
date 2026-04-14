from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.api import deps
from app.models.user import User
from app.models.scheme import Scheme
from app.schemas.scheme import (
    SchemeOut,
    SchemeCreate,
    SchemeUpdate,
    SchemeRecommendation,
)
from app.services.scheme_services import SchemeService

router = APIRouter()


@router.get("/recommendations", response_model=List[SchemeRecommendation])
def get_recommendations(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Personalized scheme suggestions for the logged-in farmer."""
    return SchemeService(db).recommend(current_user)


@router.get("/", response_model=List[SchemeOut])
def list_schemes(
    category: Optional[str] = Query(None, description="subsidy | insurance | loan | training"),
    state: Optional[str] = Query(None, description="State code, e.g. MH, UP"),
    crop: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(deps.get_db),
):
    """Browse / filter all schemes (public)."""
    return SchemeService(db).list(
        category=category, state=state, crop=crop, skip=skip, limit=limit
    )


@router.get("/{scheme_id}", response_model=SchemeOut)
def get_scheme(scheme_id: int, db: Session = Depends(deps.get_db)):
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Scheme not found")
    return scheme


@router.post("/", response_model=SchemeOut, status_code=status.HTTP_201_CREATED)
def create_scheme(
    payload: SchemeCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),  # later: admin-only
):
    return SchemeService(db).create(payload)


@router.patch("/{scheme_id}", response_model=SchemeOut)
def update_scheme(
    scheme_id: int,
    payload: SchemeUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    scheme = SchemeService(db).update(scheme_id, payload)
    if not scheme:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Scheme not found")
    return scheme


@router.delete("/{scheme_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scheme(
    scheme_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if not SchemeService(db).delete(scheme_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Scheme not found")
