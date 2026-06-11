from typing import List
from sqlalchemy.orm import Session

from backend.app.models.pest_detection_history import PestDetectionHistory
from backend.app.schemas.pest_history import PestHistoryCreate


class PestHistoryService:
    def __init__(self, db: Session):
        self.db = db

    def create_history(self, user_id: int, data: PestHistoryCreate) -> PestDetectionHistory:
        record = PestDetectionHistory(user_id=user_id, **data.model_dump())
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_history(self, user_id: int, limit: int = 20) -> List[PestDetectionHistory]:
        return (
            self.db.query(PestDetectionHistory)
            .filter(PestDetectionHistory.user_id == user_id)
            .order_by(PestDetectionHistory.created_at.desc())
            .limit(limit)
            .all()
        )

    def list_by_crop_cycle(self, crop_cycle_id: int) -> List[PestDetectionHistory]:
        return (
            self.db.query(PestDetectionHistory)
            .filter(PestDetectionHistory.crop_cycle_id == crop_cycle_id)
            .order_by(PestDetectionHistory.created_at.desc())
            .all()
        )
