from typing import List
from sqlalchemy.orm import Session

from backend.app.models.notification import Notification
from backend.app.models.enums import NotificationType


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def create_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        notification_type: NotificationType,
    ) -> Notification:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
        )
        self.db.add(notif)
        self.db.commit()
        self.db.refresh(notif)
        return notif

    def list_by_user(self, user_id: int, limit: int = 20) -> List[Notification]:
        return (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .all()
        )

    def count_unread(self, user_id: int) -> int:
        return (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)
            .count()
        )

    def mark_read(self, notification_id: int, user_id: int) -> Notification | None:
        notif = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        ).first()
        if not notif:
            return None

        notif.is_read = True
        self.db.commit()
        self.db.refresh(notif)
        return notif

    def mark_all_read(self, user_id: int) -> int:
        count = (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)
            .update({"is_read": True})
        )
        self.db.commit()
        return count

    # --- Alert trigger helpers ---

    def notify_pest_detected(self, user_id: int, disease_name: str, crop_name: str | None = None) -> Notification:
        title = f"Pest Alert: {disease_name}"
        message = f"{disease_name} was detected"
        if crop_name:
            message += f" on your {crop_name} crop"
        message += ". Open the Assistant to get treatment recommendations."

        return self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.PEST_ALERT,
        )

    def notify_market_alert(self, user_id: int, commodity: str, message: str) -> Notification:
        title = f"Market Alert: {commodity}"
        return self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.MARKET_ALERT,
        )
