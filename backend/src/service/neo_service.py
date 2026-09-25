from datetime import date, timedelta

from business_object import Neo


class NeoService:
    """Business logic for Near Earth Objects."""

    def __init__(self, neo_dao):
        self.neo_dao = neo_dao

    def search_by_id(self, id_neo: int) -> Neo | None:
        """Returns the Neo with this id, or None if it does not exist."""
        return self.neo_dao.find_by_id(id_neo)

    def search_by_name(self, name: str) -> list[Neo]:
        """Case insensitive partial match on the name."""
        name = name.strip().lower()
        return [n for n in self.neo_dao.find_all() if name in n.name.lower()]

    def search_by_diameter(self, min_diameter=None, max_diameter=None) -> list[Neo]:
        return [
            n
            for n in self.neo_dao.find_all()
            if (min_diameter is None or n.diameter >= min_diameter) and (max_diameter is None or n.diameter <= max_diameter)
        ]

    def search_by_speed(self, min_speed=None, max_speed=None) -> list[Neo]:
        """Neos whose speed is contained between certain values."""
        return [
            n
            for n in self.neo_dao.find_all()
            if (min_speed is None or n.size >= min_speed) and
            (max_speed is None or n.size <= max_speed)
        ]

    def search_by_closest_day(self, day: date) -> list[Neo]:
        """Neos whose closest approach is exactly on this day."""
        return [n for n in self.neo_dao.find_all() if n.closest_day == day]

    def get_approaching(self, days: int = 7) -> list[Neo]:
        """Neos whose closest approach is within the next `days` days,
        sorted from the soonest to the latest."""
        today = date.today()
        limit = today + timedelta(days=days)
        approaching = [n for n in self.neo_dao.find_all() if today <= n.closest_day <= limit]
        return sorted(approaching, key=lambda n: n.closest_day)
