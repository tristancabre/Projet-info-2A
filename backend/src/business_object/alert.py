from datetime import date

from business_object import Neo


class Alert:
    def __init__(
        self,
        id_user: int,
        number_days: int,
        earth_max_distance: float | None = None,
        min_diameter: float | None = None,
        min_speed: float | None = None,
        targeted_neo_id: int | None = None,
        is_active: bool = True,
        id_alert: int | None = None,
    ):
        self.id_alert = id_alert          # None tant que non enregistrée en base
        self.id_user = id_user
        self.number_days = number_days
        self.earth_max_distance = earth_max_distance
        self.min_diameter = min_diameter
        self.min_speed = min_speed
        self.targeted_neo_id = targeted_neo_id  # None = tous les NEO
        self.is_active = is_active

    def check_neo(self, neo: Neo) -> bool:
        """Retourne True si ce NEO valide l'alerte."""
        if not self.is_active:
            return False

        if self.targeted_neo_id is not None and neo.id_neo != self.targeted_neo_id:
            return False

        days_left = (neo.closest_day - date.today()).days
        if not 0 <= days_left <= self.number_days:
            return False

        if self.earth_max_distance is not None and neo.distance > self.earth_max_distance:
            return False
        if self.min_diameter is not None and neo.diameter < self.min_diameter:
            return False
        if self.min_speed is not None and neo.speed < self.min_speed:
            return False

        return True