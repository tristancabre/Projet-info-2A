# service/alert_service.py
from business_object.alert import Alert
from dao.alert_dao import AlertDao
from service.notification_service import NotificationService


class AlertNotFoundError(Exception):
    """Alert does not exist or does not belong to the user."""


class AlertService:
    def __init__(
        self,
        alert_dao: AlertDao,
        notification_service: NotificationService | None = None,
        neo_service=None,
    ):
        self.alert_dao = alert_dao
        # Optional: only needed to check the alert right after its creation
        self.notification_service = notification_service
        self.neo_service = neo_service

    def create_alert(
        self,
        id_user: int,
        number_days: int,
        earth_max_distance: float | None = None,
        min_diameter: float | None = None,
        min_speed: float | None = None,
        targeted_neo_id: int | None = None,
    ) -> Alert:
        self._validate(
            number_days, earth_max_distance, min_diameter, min_speed, targeted_neo_id
        )

        alert = Alert(
            id_user=id_user,
            number_days=number_days,
            earth_max_distance=earth_max_distance,
            min_diameter=min_diameter,
            min_speed=min_speed,
            targeted_neo_id=targeted_neo_id,
        )
        alert = self.alert_dao.create(alert)

        self._check_alert_now(alert)
        return alert

    def get_alert(self, id_alert: int, id_user: int) -> Alert:
        return self._get_owned_alert(id_alert, id_user)

    def list_user_alerts(self, id_user: int) -> list[Alert]:
        return self.alert_dao.get_by_user(id_user)

    def update_alert(
        self,
        id_alert: int,
        id_user: int,
        number_days: int,
        earth_max_distance: float | None = None,
        min_diameter: float | None = None,
        min_speed: float | None = None,
        targeted_neo_id: int | None = None,
    ) -> Alert:
        self._validate(
            number_days, earth_max_distance, min_diameter, min_speed, targeted_neo_id
        )

        alert = self._get_owned_alert(id_alert, id_user)
        alert.number_days = number_days
        alert.earth_max_distance = earth_max_distance
        alert.min_diameter = min_diameter
        alert.min_speed = min_speed
        alert.targeted_neo_id = targeted_neo_id
        self.alert_dao.update(alert)

        self._check_alert_now(alert)
        return alert

    def set_active(self, id_alert: int, id_user: int, is_active: bool) -> Alert:
        alert = self._get_owned_alert(id_alert, id_user)
        alert.is_active = is_active
        self.alert_dao.update(alert)

        if is_active:
            self._check_alert_now(alert)
        return alert

    def delete_alert(self, id_alert: int, id_user: int) -> bool:
        self._get_owned_alert(id_alert, id_user)
        return self.alert_dao.delete(id_alert)

    # ---------- private helpers ----------

    def _get_owned_alert(self, id_alert: int, id_user: int) -> Alert:
        """Checks that the alert exists and belongs to the user."""
        alert = self.alert_dao.get_by_id(id_alert)
        if alert is None or alert.id_user != id_user:
            # Same error in both cases: do not reveal that another user's alert exists
            raise AlertNotFoundError(f"Alert {id_alert} not found")
        return alert

    @staticmethod
    def _validate(
        number_days: int,
        earth_max_distance: float | None,
        min_diameter: float | None,
        min_speed: float | None,
        targeted_neo_id: int | None,
    ) -> None:
        if number_days <= 0:
            raise ValueError("number_days must be positive")

        if all(
            c is None
            for c in (earth_max_distance, min_diameter, min_speed, targeted_neo_id)
        ):
            raise ValueError("An alert needs at least one parameter")

        for name, value in (
            ("earth_max_distance", earth_max_distance),
            ("min_diameter", min_diameter),
            ("min_speed", min_speed),
        ):
            if value is not None and value < 0:
                raise ValueError(f"{name} cannot be negative")

    def _check_alert_now(self, alert: Alert) -> None:
        """Generates notifications right away if a Neo already matches the alert."""
        if not alert.is_active:
            return
        if self.notification_service is None or self.neo_service is None:
            return
        neos = self.neo_service.get_upcoming_neos()  # adapt to your NeoService method
        self.notification_service.generate([alert], neos)
