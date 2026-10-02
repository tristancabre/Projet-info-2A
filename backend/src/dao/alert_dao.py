# dao/alert_dao.py
from business_object.alert import Alert
from dao.db_connection import DBConnection


class AlertDao:
    @staticmethod
    def _to_alert(row) -> Alert:
        return Alert(
            id_alert=row["id_alert"],
            id_user=row["id_user"],
            number_days=row["number_days"],
            earth_max_distance=row["earth_max_distance"],
            min_diameter=row["min_diameter"],
            min_speed=row["min_speed"],
            targeted_neo_id=row["targeted_neo_id"],
            is_active=bool(row["is_active"]),
        )

    def create(self, alert: Alert) -> Alert:
        with DBConnection.connection() as conn:
            cur = conn.execute(
                """INSERT INTO alert (id_user, number_days, earth_max_distance,
                                      min_diameter, min_speed, targeted_neo_id, is_active)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    alert.id_user,
                    alert.number_days,
                    alert.earth_max_distance,
                    alert.min_diameter,
                    alert.min_speed,
                    alert.targeted_neo_id,
                    int(alert.is_active),
                ),
            )
            alert.id_alert = cur.lastrowid
        return alert

    def get_by_id(self, id_alert: int) -> Alert | None:
        with DBConnection.connection() as conn:
            row = conn.execute("SELECT * FROM alert WHERE id_alert = ?", (id_alert,)).fetchone()
        return self._to_alert(row) if row else None

    def get_by_user(self, id_user: int) -> list[Alert]:
        with DBConnection.connection() as conn:
            rows = conn.execute("SELECT * FROM alert WHERE id_user = ?", (id_user,)).fetchall()
        return [self._to_alert(r) for r in rows]

    def get_all_active(self) -> list[Alert]:
        with DBConnection.connection() as conn:
            rows = conn.execute("SELECT * FROM alert WHERE is_active = 1").fetchall()
        return [self._to_alert(r) for r in rows]

    def update(self, alert: Alert) -> bool:
        with DBConnection.connection() as conn:
            cur = conn.execute(
                """UPDATE alert SET number_days = ?, earth_max_distance = ?,
                          min_diameter = ?, min_speed = ?, targeted_neo_id = ?,
                          is_active = ?
                   WHERE id_alert = ?""",
                (
                    alert.number_days,
                    alert.earth_max_distance,
                    alert.min_diameter,
                    alert.min_speed,
                    alert.targeted_neo_id,
                    int(alert.is_active),
                    alert.id_alert,
                ),
            )
        return cur.rowcount > 0

    def delete(self, id_alert: int) -> bool:
        with DBConnection.connection() as conn:
            cur = conn.execute("DELETE FROM alert WHERE id_alert = ?", (id_alert,))
        return cur.rowcount > 0
