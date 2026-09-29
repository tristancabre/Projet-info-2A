# business_object/notification.py
from datetime import datetime

from business_object import Alert, Neo


class Notification:
    """Notification created when a Neo matches an Alert."""

    def __init__(
        self,
        id_alert: int,
        id_user: int,
        id_neo: int,
        message: str,
        created_at: datetime | None = None,
        id_notification: int | None = None,
    ):
        self.id_notification = id_notification  # None until saved in the database
        self.id_alert = id_alert
        self.id_user = id_user
        self.id_neo = id_neo
        self.message = message
        self.created_at = created_at or datetime.now()

    @classmethod
    def from_alert_and_neo(cls, alert: Alert, neo: Neo) -> "Notification":
        message = (
            f"{neo.name} will pass {neo.distance} km from Earth "
            f"on {neo.closest_day} "
            f"(speed: {neo.speed}, diameter: {neo.diameter})."
        )
        return cls(alert.id_alert, alert.id_user, neo.id_neo, message)

    def __str__(self):
        return self.message
