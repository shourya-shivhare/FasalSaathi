from typing import List, Optional
from sqlalchemy.orm import Session

from backend.app.models.farm import Farm
from backend.app.models.crop_cycle import CropCycle
from backend.app.models.enums import CropCycleStatus
from backend.app.schemas.farm import FarmCreate, FarmUpdate


class FarmService:
    def __init__(self, db: Session):
        self.db = db

    def create_farm(self, user_id: int, data: FarmCreate) -> Farm:
        farm = Farm(user_id=user_id, **data.model_dump())
        self.db.add(farm)
        self.db.commit()
        self.db.refresh(farm)
        
        # Invalidate caches
        from backend.app.services.cache_service import CacheService
        from backend.app.utils.cache_keys import make_context_key, make_dashboard_key
        CacheService.delete_sync(make_context_key(user_id))
        CacheService.delete_sync(make_dashboard_key(user_id))
        CacheService.invalidate_pattern_sync(f"crop_rec:{user_id}:*")
        CacheService.invalidate_pattern_sync(f"scheme_rec:{user_id}:*")

        return farm

    def list_farms(self, user_id: int) -> List[Farm]:
        return self.db.query(Farm).filter(Farm.user_id == user_id).all()

    def get_farm(self, farm_id: int, user_id: int) -> Optional[Farm]:
        return self.db.query(Farm).filter(
            Farm.id == farm_id,
            Farm.user_id == user_id
        ).first()

    def update_farm(self, farm_id: int, user_id: int, data: FarmUpdate) -> Optional[Farm]:
        farm = self.get_farm(farm_id, user_id)
        if not farm:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(farm, field, value)

        self.db.commit()
        self.db.refresh(farm)
        
        # Invalidate caches
        from backend.app.services.cache_service import CacheService
        from backend.app.utils.cache_keys import make_context_key, make_dashboard_key, make_farm_key
        CacheService.delete_sync(make_context_key(user_id))
        CacheService.delete_sync(make_dashboard_key(user_id))
        CacheService.delete_sync(make_farm_key(farm_id))
        CacheService.invalidate_pattern_sync(f"crop_rec:{user_id}:*")
        CacheService.invalidate_pattern_sync(f"scheme_rec:{user_id}:*")

        return farm

    def delete_farm(self, farm_id: int, user_id: int) -> bool:
        farm = self.get_farm(farm_id, user_id)
        if not farm:
            return False

        self.db.delete(farm)
        self.db.commit()
        
        # Invalidate caches
        from backend.app.services.cache_service import CacheService
        from backend.app.utils.cache_keys import make_context_key, make_dashboard_key, make_farm_key
        CacheService.delete_sync(make_context_key(user_id))
        CacheService.delete_sync(make_dashboard_key(user_id))
        CacheService.delete_sync(make_farm_key(farm_id))
        CacheService.invalidate_pattern_sync(f"crop_rec:{user_id}:*")
        CacheService.invalidate_pattern_sync(f"scheme_rec:{user_id}:*")

        return True

    def get_farm_with_active_crop_count(self, farm: Farm) -> dict:
        """Enrich a farm object with its active crop count."""
        active_count = self.db.query(CropCycle).filter(
            CropCycle.farm_id == farm.id,
            CropCycle.status == CropCycleStatus.ACTIVE
        ).count()

        farm_dict = {
            "id": farm.id,
            "user_id": farm.user_id,
            "farm_name": farm.farm_name,
            "state": farm.state,
            "district": farm.district,
            "village": farm.village,
            "total_area": farm.total_area,
            "soil_type": farm.soil_type,
            "irrigation_source": farm.irrigation_source,
            "created_at": farm.created_at,
            "active_crop_count": active_count,
        }
        return farm_dict
