from datetime import date, timedelta

from business_object.neo import Neo
from dao.nasa_dao import NasaDao
from dao.neo_dao import NeoDao
from utils.log_utils import get_logger, log

logger = get_logger(__name__)


class NeoService:
    """Business logic for Near Earth Objects."""

    @log
    def search_by_id(self, id_neo: int) -> Neo | None:
        """Returns the Neo with this id, or None if it does not exist."""
        return NeoDao().find_by_id(id_neo)

    @log
    def search_by_name(self, name: str) -> list[Neo]:
        """Case insensitive partial match on the name."""
        return NeoDao().find_by_name(name.strip())

    @log
    def find_all(self) -> list[Neo]:
        """Returns every registered Neo."""
        return NeoDao().list_all()

    @log
    def search_by_diameter(
        self, min_diameter: float | None = None, max_diameter: float | None = None
    ) -> list[Neo]:
        """Neos whose diameter is contained between certain values."""
        return NeoDao().find_by_diameter(min_diameter, max_diameter)

    @log
    def search_by_speed(
        self, min_speed: float | None = None, max_speed: float | None = None
    ) -> list[Neo]:
        """Neos whose speed is contained between certain values."""
        return NeoDao().find_by_speed(min_speed, max_speed)

    @log
    def search_by_closest_day(self, day: date) -> list[Neo]:
        """Neos whose closest approach is exactly on this day."""
        return NeoDao().find_by_closest_day(day)

    @log
    def get_approaching(self, days: int = 7) -> list[Neo]:
        """Neos whose closest approach is within the next `days` days,
        sorted from the soonest to the latest."""
        today = date.today()
        return NeoDao().find_between_days(today, today + timedelta(days=days))

    @log
    def create(
        self,
        name: str,
        diameter: float | None,
        distance: float,
        speed: float | None,
        closest_day: date,
    ) -> Neo | None:
        """Creates a Neo. The rarity is computed from distance and diameter.
        Returns the created Neo, or None if the creation failed."""
        neo = Neo(
            name=name,
            diameter=diameter,
            distance=distance,
            closest_day=closest_day,
            speed=speed,
            rarity=NeoDao.calcul_rarity(distance, diameter),
        )
        try:
            if not NeoDao().create(neo):
                return None
        except Exception:
            logger.exception("Error while creating neo")
            return None
        return neo

    @log
    def update(self, neo: Neo) -> Neo | None:
        """Updates an existing Neo. The rarity is recomputed from distance and diameter.
        Returns the updated Neo, or None if the update failed."""
        neo.rarity = NeoDao.calcul_rarity(neo.distance, neo.diameter)
        try:
            if not NeoDao().update(neo):
                return None
        except Exception:
            logger.exception("Error while updating neo")
            return None
        return neo

    @log
    def delete(self, neo: Neo) -> bool:
        """Deletes a Neo. Returns True if it was deleted, False otherwise."""
        try:
            return NeoDao().delete(neo)
        except Exception:
            logger.exception("Error while deleting neo")
            return False

    @log
    def refresh_from_nasa(self) -> int:
        """Fetches the NEO data from the NASA API and stores it in the database.
        Returns the number of neos inserted."""
        neos = NasaDao().recuperer_donnees_nasa()
        return NeoDao().inserer_donnees_sql(neos)
