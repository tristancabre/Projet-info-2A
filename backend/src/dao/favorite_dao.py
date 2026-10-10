from business_object.favorite import Favorite
from business_object.neo import Neo
from dao.db_connection import DBConnection
from dao.neo_dao import NeoDao
from utils.log_utils import get_logger, log
from utils.singleton import Singleton

logger = get_logger(__name__)

FAVORITE_TABLE = "project.favorites"
NEO_TABLE = "project.neo"


class FavoriteDao(metaclass=Singleton):
    """Data access for the favorites (association between users and neos)."""

    @log
    def add(self, id_user: int, neo: Neo) -> Favorite | None:
        """Adds a neo to the favorites of a user.

        Returns:
            The created Favorite, or None if the neo was already a favorite
            of this user (requires the UNIQUE (id_user, id_neo) constraint).
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"INSERT INTO {FAVORITE_TABLE} (id_user, id_neo) "
                        "VALUES (%(id_user)s, %(id_neo)s) "
                        "ON CONFLICT (id_user, id_neo) DO NOTHING "
                        "RETURNING id_favorite, date_added;",
                        {"id_user": id_user, "id_neo": neo.id_neo},
                    )
                    res = cursor.fetchone()
        except Exception:
            logger.exception("Error while adding a favorite")
            raise

        if not res:
            return None
        return Favorite(
            id_favorite=res["id_favorite"],
            id_user=id_user,
            neo=neo,
            date_added=res["date_added"],
        )

    @log
    def remove(self, id_user: int, id_neo: int) -> bool:
        """Removes a neo from the favorites of a user.
        Returns True if a favorite was removed, False if there was none."""
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"DELETE FROM {FAVORITE_TABLE} "
                        "WHERE id_user = %(id_user)s AND id_neo = %(id_neo)s;",
                        {"id_user": id_user, "id_neo": id_neo},
                    )
                    res = cursor.rowcount
        except Exception:
            logger.exception("Error while removing a favorite")
            raise

        return res > 0

    @log
    def find_by_user(self, id_user: int) -> list[Favorite]:
        """Returns the favorites of a user, the most recently added first."""
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT f.id_favorite, f.id_user, f.date_added, "
                        "       n.id_neo, n.name, n.diameter, n.distance, "
                        "       n.speed, n.closest_day, n.rarity "
                        f"  FROM {FAVORITE_TABLE} f "
                        f"  JOIN {NEO_TABLE} n ON n.id_neo = f.id_neo "
                        " WHERE f.id_user = %(id_user)s "
                        " ORDER BY f.date_added DESC, n.name;",
                        {"id_user": id_user},
                    )
                    rows = cursor.fetchall()
        except Exception:
            logger.exception("Error while listing the favorites")
            raise

        return [
            Favorite(
                id_favorite=row["id_favorite"],
                id_user=row["id_user"],
                neo=NeoDao._to_neo(row),  # the joined row contains all the neo columns
                date_added=row["date_added"],
            )
            for row in rows or []
        ]
