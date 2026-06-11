"""Journal entry endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.api import deps
from backend.app.models.user import User
from backend.app.schemas.crop_journal import JournalEntryCreate, JournalEntryOut
from backend.app.services.journal_service import JournalService

router = APIRouter()


@router.post("/", response_model=JournalEntryOut, status_code=status.HTTP_201_CREATED)
def create_journal_entry(
    data: JournalEntryCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Create a journal entry for a crop cycle."""
    service = JournalService(db)
    entry = service.create_entry(current_user.id, data)
    if not entry:
        raise HTTPException(status_code=404, detail="Crop cycle not found or not owned by you")
    return entry


@router.get("/", response_model=List[JournalEntryOut])
def list_journal_entries(
    crop_cycle_id: Optional[int] = Query(None),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """List journal entries. Optionally filter by crop_cycle_id."""
    service = JournalService(db)
    if crop_cycle_id:
        return service.list_by_crop_cycle(crop_cycle_id)
    return service.list_recent(current_user.id)


@router.get("/recent", response_model=List[JournalEntryOut])
def list_recent_entries(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get recent journal entries across all crop cycles."""
    service = JournalService(db)
    return service.list_recent(current_user.id)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_journal_entry(
    entry_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Delete a journal entry."""
    service = JournalService(db)
    deleted = service.delete_entry(entry_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Journal entry not found")
