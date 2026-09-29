# controller/notification_controller.py
from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from dao.notification_dao import NotificationDao
from service.notification_service import NotificationService

router = APIRouter(prefix="/users/{id_user}/notifications", tags=["notifications"])

notification_service = NotificationService(NotificationDao())


class NotificationResponse(BaseModel):
    id_notification: int
    id_alert: int
    id_neo: int
    message: str
    created_at: datetime


@router.get("", response_model=list[NotificationResponse])
def get_notifications(id_user: int):
    """Returns the notifications received by a user."""
    return [
        NotificationResponse(
            id_notification=n.id_notification,
            id_alert=n.id_alert,
            id_neo=n.id_neo,
            message=n.message,
            created_at=n.created_at,
        )
        for n in notification_service.get_user_notifications(id_user)
    ]
