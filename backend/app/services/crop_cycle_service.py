from typing import List, Optional
from sqlalchemy.orm import Session

from backend.app.models.crop_cycle import CropCycle
from backend.app.models.farm import Farm
from backend.app.models.enums import CropCycleStatus, CropStage
from backend.app.schemas.crop_cycle import CropCycleCreate, CropCycleUpdate


class CropCycleService:
    def __init__(self, db: Session):
        self.db = db

    def create_cycle(self, user_id: int, data: CropCycleCreate) -> Optional[CropCycle]:
        """Create a crop cycle after validating farm ownership."""
        farm = self.db.query(Farm).filter(
            Farm.id == data.farm_id,
            Farm.user_id == user_id
        ).first()
        if not farm:
            return None

        cycle = CropCycle(**data.model_dump())
        self.db.add(cycle)
        self.db.commit()
        self.db.refresh(cycle)
        
        # Invalidate caches
        from backend.app.services.cache_service import CacheService
        from backend.app.utils.cache_keys import make_context_key, make_dashboard_key
        CacheService.delete_sync(make_context_key(user_id))
        CacheService.delete_sync(make_dashboard_key(user_id))
        CacheService.invalidate_pattern_sync(f"crop_rec:{user_id}:*")
        CacheService.invalidate_pattern_sync(f"scheme_rec:{user_id}:*")

        return cycle

    def list_cycles(
        self,
        user_id: int,
        farm_id: Optional[int] = None,
        status: Optional[CropCycleStatus] = None,
        season: Optional[str] = None,
        year: Optional[int] = None,
    ) -> List[CropCycle]:
        """List crop cycles for a user with optional filters."""
        query = (
            self.db.query(CropCycle)
            .join(Farm, CropCycle.farm_id == Farm.id)
            .filter(Farm.user_id == user_id)
        )

        if farm_id:
            query = query.filter(CropCycle.farm_id == farm_id)
        if status:
            query = query.filter(CropCycle.status == status)
        if season:
            query = query.filter(CropCycle.season == season)
        if year:
            query = query.filter(CropCycle.year == year)

        return query.order_by(CropCycle.updated_at.desc()).all()

    def get_cycle(self, cycle_id: int, user_id: int) -> Optional[CropCycle]:
        """Get a single crop cycle after verifying ownership."""
        return (
            self.db.query(CropCycle)
            .join(Farm, CropCycle.farm_id == Farm.id)
            .filter(CropCycle.id == cycle_id, Farm.user_id == user_id)
            .first()
        )

    def update_cycle(self, cycle_id: int, user_id: int, data: CropCycleUpdate) -> Optional[CropCycle]:
        cycle = self.get_cycle(cycle_id, user_id)
        if not cycle:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(cycle, field, value)

        self.db.commit()
        self.db.refresh(cycle)
        
        # Invalidate caches
        from backend.app.services.cache_service import CacheService
        from backend.app.utils.cache_keys import make_context_key, make_dashboard_key
        CacheService.delete_sync(make_context_key(user_id))
        CacheService.delete_sync(make_dashboard_key(user_id))
        CacheService.invalidate_pattern_sync(f"crop_rec:{user_id}:*")
        CacheService.invalidate_pattern_sync(f"scheme_rec:{user_id}:*")

        return cycle

    def update_stage(self, cycle_id: int, user_id: int, new_stage: CropStage) -> Optional[CropCycle]:
        cycle = self.get_cycle(cycle_id, user_id)
        if not cycle:
            return None

        cycle.current_stage = new_stage
        self.db.commit()
        self.db.refresh(cycle)
        
        # Invalidate caches
        from backend.app.services.cache_service import CacheService
        from backend.app.utils.cache_keys import make_context_key, make_dashboard_key
        CacheService.delete_sync(make_context_key(user_id))
        CacheService.delete_sync(make_dashboard_key(user_id))
        CacheService.invalidate_pattern_sync(f"crop_rec:{user_id}:*")
        CacheService.invalidate_pattern_sync(f"scheme_rec:{user_id}:*")

        return cycle

    def complete_cycle(self, cycle_id: int, user_id: int, final_status: CropCycleStatus = CropCycleStatus.COMPLETED) -> Optional[CropCycle]:
        cycle = self.get_cycle(cycle_id, user_id)
        if not cycle:
            return None

        cycle.status = final_status
        self.db.commit()
        self.db.refresh(cycle)
        
        # Invalidate caches
        from backend.app.services.cache_service import CacheService
        from backend.app.utils.cache_keys import make_context_key, make_dashboard_key
        CacheService.delete_sync(make_context_key(user_id))
        CacheService.delete_sync(make_dashboard_key(user_id))
        CacheService.invalidate_pattern_sync(f"crop_rec:{user_id}:*")
        CacheService.invalidate_pattern_sync(f"scheme_rec:{user_id}:*")

        return cycle
