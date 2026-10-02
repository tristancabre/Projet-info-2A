# service/notification_service.py
from business_object.alert import Alert
from business_object.neo import Neo
from business_object.notification import Notification
from dao.notification_dao import NotificationDao


class NotificationService:
    def __init__(self, notification_dao: NotificationDao):
        self.notification_dao = notification_dao

    def generate(self, alerts: list[Alert], neos: list[Neo]) -> list[Notification]:
        """Create and save notifications for Neos matching an alert."""
        already_sent = self.notification_dao.get_sent_pairs()

        new_notifications = []
        for alert in alerts:
            for neo in neos:
                if (alert.id_alert, neo.id_neo) in already_sent:
                    continue
                if alert.check_neo(neo):
                    new_notifications.append(Notification.from_alert_and_neo(alert, neo))

        if new_notifications:
            self.notification_dao.save_many(new_notifications)
        return new_notifications

    def get_user_notifications(self, id_user: int) -> list[Notification]:
        return self.notification_dao.get_by_user(id_user)

    # service/notification_service.py supplémentaire pour envoyer une notif
    def check_all_alerts(self, alert_dao, neo_service) -> int:
        """Checks every active alert against upcoming Neos. Returns the number of new notifications."""
        neos = neo_service.get_upcoming_neos()
        alerts = alert_dao.get_all_active()
        return len(self.generate(alerts, neos))
