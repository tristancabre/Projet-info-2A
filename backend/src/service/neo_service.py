from datetime import date, timedelta

from business_object.neo import Neo
from dao.neo_dao import NeoDao
from utils.log_utils import log


class NeoService:
    """Business logic for Near Earth Objects."""

    @log
    def search_by_id(self, id_neo: int) -> Neo | None:
        """Returns the Neo with this id, or None if it does not exist."""
        return NeoDao().find_by_id(id_neo)

    @log
    def search_by_name(self, name: str) -> list[Neo]:
        """Case insensitive partial match on the name."""
        name = name.strip().lower()
        return NeoDao().find_by_name(name)

    @log
    def find_all(self) -> list[Neo]:
        """Returns every registered Neo."""
        return NeoDao().list_all()

    @log
    def search_by_diameter(self, min_diameter=None, max_diameter=None) -> list[Neo]:
        return [
            n
            for n in NeoDao().find_all()
            if (min_diameter is None or n.diameter >= min_diameter)
            and (max_diameter is None or n.diameter <= max_diameter)
        ]

    @log
    def search_by_speed(self, min_speed=None, max_speed=None) -> list[Neo]:
        """Neos whose speed is contained between certain values."""
        return [
            n
            for n in NeoDao().find_all()
            if (min_speed is None or n.speed >= min_speed)
            and (max_speed is None or n.speed <= max_speed)
        ]

    @log
    def search_by_closest_day(self, day: date) -> list[Neo]:
        """Neos whose closest approach is exactly on this day."""
        return [n for n in NeoDao().find_all() if n.closest_day == day]

    @log
    def get_approaching(self, days: int = 7) -> list[Neo]:
        """Neos whose closest approach is within the next `days` days,
        sorted from the soonest to the latest."""
        today = date.today()
        limit = today + timedelta(days=days)
        approaching = [n for n in NeoDao().find_all() if today <= n.closest_day <= limit]
        return sorted(approaching, key=lambda n: n.closest_day)

    @log
    def update(self, neo: Neo) -> Neo | None:
        """Updates an existing Neo.
        Returns the updated Neo, or None if the update failed."""
        if not NeoDao().update(neo):
            return None
        return neo

    @log
    def delete(self, neo: Neo) -> bool:
        return NeoDao().delete(neo)

    @log
    def create(
        self,
        name: str,
        diameter: float | None,
        distance: float | None,
        speed: float | None,
        closest_day: date,
        rarity,
    ) -> Neo:

        neo = Neo(name, diameter, distance, speed, closest_day, rarity)
        NeoDao().create(neo)
        return neo
