from typing import List, Optional
from sqlalchemy.orm import Session

from backend.app.models.crop_journal import CropJournalEntry
from backend.app.models.crop_cycle import CropCycle
from backend.app.models.farm import Farm
from backend.app.schemas.crop_journal import JournalEntryCreate


class JournalService:
    def __init__(self, db: Session):
        self.db = db

    def create_entry(self, user_id: int, data: JournalEntryCreate) -> Optional[CropJournalEntry]:
        """Create a journal entry after validating crop cycle ownership."""
        cycle = (
            self.db.query(CropCycle)
            .join(Farm, CropCycle.farm_id == Farm.id)
            .filter(CropCycle.id == data.crop_cycle_id, Farm.user_id == user_id)
            .first()
        )
        if not cycle:
            return None

        entry = CropJournalEntry(**data.model_dump())
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        
        # Invalidate caches
        from backend.app.services.cache_service import CacheService
        from backend.app.utils.cache_keys import make_context_key, make_dashboard_key
        CacheService.delete_sync(make_context_key(user_id))
        CacheService.delete_sync(make_dashboard_key(user_id))
        CacheService.invalidate_pattern_sync(f"crop_rec:{user_id}:*")
        CacheService.invalidate_pattern_sync(f"scheme_rec:{user_id}:*")

        return entry

    def list_by_crop_cycle(self, crop_cycle_id: int) -> List[CropJournalEntry]:
        return (
            self.db.query(CropJournalEntry)
            .filter(CropJournalEntry.crop_cycle_id == crop_cycle_id)
            .order_by(CropJournalEntry.created_at.desc())
            .all()
        )

    def list_recent(self, user_id: int, limit: int = 15) -> List[CropJournalEntry]:
        """Get recent journal entries across all of a user's crop cycles."""
        return (
            self.db.query(CropJournalEntry)
            .join(CropCycle, CropJournalEntry.crop_cycle_id == CropCycle.id)
            .join(Farm, CropCycle.farm_id == Farm.id)
            .filter(Farm.user_id == user_id)
            .order_by(CropJournalEntry.created_at.desc())
            .limit(limit)
            .all()
        )

    def delete_entry(self, entry_id: int, user_id: int) -> bool:
        """Delete a journal entry after verifying ownership chain."""
        entry = (
            self.db.query(CropJournalEntry)
            .join(CropCycle, CropJournalEntry.crop_cycle_id == CropCycle.id)
            .join(Farm, CropCycle.farm_id == Farm.id)
            .filter(CropJournalEntry.id == entry_id, Farm.user_id == user_id)
            .first()
        )
        if not entry:
            return False

        self.db.delete(entry)
        self.db.commit()
        
        # Invalidate caches
        from backend.app.services.cache_service import CacheService
        from backend.app.utils.cache_keys import make_context_key, make_dashboard_key
        CacheService.delete_sync(make_context_key(user_id))
        CacheService.delete_sync(make_dashboard_key(user_id))
        CacheService.invalidate_pattern_sync(f"crop_rec:{user_id}:*")
        CacheService.invalidate_pattern_sync(f"scheme_rec:{user_id}:*")

        return True
