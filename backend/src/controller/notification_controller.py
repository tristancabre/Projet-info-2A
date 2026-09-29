# controller/notification_controller.py
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from utils.auth import get_current_user_id

from dao import alert_dao
from dao.notification_dao import NotificationDao
from service import neo_service
from service.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


notification_service = NotificationService(NotificationDao())


class NotificationResponse(BaseModel):
    id_notification: int
    id_alert: int
    id_neo: int
    message: str
    created_at: datetime


@router.get("", response_model=list[NotificationResponse])
def get_notifications(id_user: int = Depends(get_current_user_id)):
    """Returns the notifications of the connected user."""
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


# check if there are new notifs


@router.post("/check", tags=["Notifications"])
def run_check():
    count = notification_service.check_all_alerts(alert_dao, neo_service)
    return {"new_notifications": count}
