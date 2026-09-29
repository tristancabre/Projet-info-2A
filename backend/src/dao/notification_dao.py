# dao/notification_dao.py
from datetime import datetime

from business_object.notification import Notification
from dao.db_connection import get_connection


class NotificationDao:
    @staticmethod
    def _to_notification(row) -> Notification:
        return Notification(
            id_notification=row["id_notification"],
            id_alert=row["id_alert"],
            id_user=row["id_user"],
            id_neo=row["id_neo"],
            message=row["message"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def get_sent_pairs(self) -> set[tuple[int, int]]:
        """Pairs (id_alert, id_neo) already notified."""
        with get_connection() as conn:
            rows = conn.execute("SELECT id_alert, id_neo FROM notification").fetchall()
        return {(r["id_alert"], r["id_neo"]) for r in rows}

    def save_many(self, notifications: list[Notification]) -> None:
        with get_connection() as conn:
            conn.executemany(
                """INSERT OR IGNORE INTO notification
                       (id_alert, id_user, id_neo, message, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                [
                    (n.id_alert, n.id_user, n.id_neo, n.message, n.created_at.isoformat())
                    for n in notifications
                ],
            )

    def get_by_user(self, id_user: int) -> list[Notification]:
        """All notifications received by a user, most recent first."""
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM notification WHERE id_user = ? ORDER BY created_at DESC",
                (id_user,),
            ).fetchall()
        return [self._to_notification(r) for r in rows]