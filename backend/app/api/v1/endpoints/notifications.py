"""Notification endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api import deps
from backend.app.models.user import User
from backend.app.schemas.notification import NotificationOut
from backend.app.services.notification_service import NotificationService

router = APIRouter()


@router.get("/", response_model=List[NotificationOut])
def list_notifications(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """List notifications for the authenticated user."""
    service = NotificationService(db)
    return service.list_by_user(current_user.id)


@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get the count of unread notifications."""
    service = NotificationService(db)
    return {"unread_count": service.count_unread(current_user.id)}


@router.patch("/{notification_id}/read", response_model=NotificationOut)
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Mark a single notification as read."""
    service = NotificationService(db)
    notif = service.mark_read(notification_id, current_user.id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notif


@router.post("/mark-all-read")
def mark_all_notifications_read(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Mark all notifications as read for the authenticated user."""
    service = NotificationService(db)
    count = service.mark_all_read(current_user.id)
    return {"marked_read": count}
