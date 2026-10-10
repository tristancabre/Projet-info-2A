from datetime import date

from business_object.neo import Neo
from dao.db_connection import DBConnection
from utils.log_utils import get_logger, log
from utils.singleton import Singleton

logger = get_logger(__name__)

TABLE = "project.neo"
COLUMNS = "id_neo, name, diameter, distance, speed, closest_day, rarity"

# Mapping explicite : strptime("%b") dépend de la locale du système
MONTHS = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}


class NeoDao(metaclass=Singleton):
    """Class containing methods to access NEOs in the database."""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def vers_float(valeur) -> float | None:
        """Convertit une valeur en float, ou None si la valeur est absente."""
        return float(valeur) if valeur is not None else None

    @staticmethod
    def parse_date(date_str: str | None) -> date | None:
        """Convertit une date NASA ('2026-Oct-09 12:30') en date, ou None."""
        if not date_str:
            return None
        year, month, day = date_str[:11].split("-")
        return date(int(year), MONTHS[month], int(day))

    @staticmethod
    def calcul_rarity(distance: float, diameter: float | None = None) -> int:
        """Calcule la rareté (1 à 5) d'un NEO.

        NOTE : remplacez le corps par votre version qui utilise le diamètre.
        Ici, seule la distance (version précédente) est prise en compte.
        """
        if distance < 0.01:
            return 5
        elif distance < 0.03:
            return 4
        elif distance < 0.05:
            return 3
        elif distance < 0.1:
            return 2
        return 1

    @staticmethod
    def _to_neo(row: dict) -> Neo:
        """Construit un Neo à partir d'une ligne de la base (curseur de type dict)."""
        return Neo(
            id_neo=row["id_neo"],
            name=row["name"],
            diameter=row["diameter"],
            distance=row["distance"],
            speed=row["speed"],
            closest_day=row["closest_day"],
            rarity=row["rarity"],
        )

    def _fetch_neos(self, query: str, params: dict | None = None) -> list[Neo]:
        """Exécute un SELECT et renvoie la liste de Neo correspondante."""
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, params or {})
                    rows = cursor.fetchall()
        except Exception:
            logger.exception("Erreur lors de la lecture des NEO")
            raise

        return [self._to_neo(row) for row in rows or []]

    def _find_between(self, column: str, minimum, maximum) -> list[Neo]:
        """Neos dont `column` est comprise entre deux bornes (toutes deux optionnelles).

        `column` est toujours une constante interne, jamais une valeur utilisateur.
        """
        conditions = [f"{column} IS NOT NULL"]
        params = {}
        if minimum is not None:
            conditions.append(f"{column} >= %(minimum)s")
            params["minimum"] = minimum
        if maximum is not None:
            conditions.append(f"{column} <= %(maximum)s")
            params["maximum"] = maximum

        query = (
            f"SELECT {COLUMNS} FROM {TABLE} "
            f"WHERE {' AND '.join(conditions)} "
            f"ORDER BY {column}, id_neo;"
        )
        return self._fetch_neos(query, params)

    # ------------------------------------------------------------------
    # Import des données NASA
    # ------------------------------------------------------------------
    @log
    def inserer_donnees_sql(self, neos: list[dict]) -> int:
        """Insère une liste de NEO (format API NASA) dans la base PostgreSQL.

        Les entrées sans nom ou sans distance sont ignorées.

        Args:
            neos: Liste de dictionnaires récupérés depuis l'API NASA.

        Returns:
            Le nombre de NEO réellement insérés.
        """
        requete = f"""
            INSERT INTO {TABLE}
                (name, diameter, distance, speed, closest_day, rarity)
            VALUES
                (%(name)s, %(diameter)s, %(distance)s, %(speed)s,
                 %(closest_day)s, %(rarity)s);
        """

        lignes = []
        for neo in neos:
            name = (neo.get("fullname") or neo.get("des") or "").strip()
            distance = self.vers_float(neo.get("dist"))
            if not name or distance is None:
                continue

            diameter = self.vers_float(neo.get("diameter"))
            speed = self.vers_float(neo.get("v_rel"))
            distance = round(distance, 6)
            if speed is not None:
                speed = round(speed, 6)

            lignes.append(
                {
                    "name": name,
                    "diameter": diameter,
                    "distance": distance,
                    "speed": speed,
                    "closest_day": self.parse_date(neo.get("cd")),
                    "rarity": self.calcul_rarity(distance, diameter),
                }
            )

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.executemany(requete, lignes)
        except Exception:
            logger.exception("Erreur lors de l'insertion des NEO")
            raise

        logger.info("%d NEO insérés sur %d reçus.", len(lignes), len(neos))
        return len(lignes)

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    @log
    def create(self, neo: Neo) -> bool:
        """Create a Neo in the database.
        Args:
            neo: Neo to create (its id_neo is filled in on success)
        Returns:
            True if creation is successful, False otherwise
        """
        res = None

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"INSERT INTO {TABLE} "
                        "(name, diameter, distance, speed, closest_day, rarity) "
                        "VALUES (%(name)s, %(diameter)s, %(distance)s, %(speed)s, "
                        "        %(closest_day)s, %(rarity)s) "
                        "RETURNING id_neo;",
                        {
                            "name": neo.name,
                            "diameter": neo.diameter,
                            "distance": neo.distance,
                            "speed": neo.speed,
                            "closest_day": neo.closest_day,
                            "rarity": neo.rarity,
                        },
                    )
                    res = cursor.fetchone()
        except Exception:
            logger.exception("Erreur lors de la création du NEO")
            raise

        if res:
            neo.id_neo = res["id_neo"]
            return True
        return False

    @log
    def find_by_id(self, id_neo: int) -> Neo | None:
        """Find a Neo by its id, or None if it does not exist."""
        neos = self._fetch_neos(
            f"SELECT {COLUMNS} FROM {TABLE} WHERE id_neo = %(id_neo)s;",
            {"id_neo": id_neo},
        )
        return neos[0] if neos else None

    @log
    def find_by_name(self, name: str) -> list[Neo]:
        """Case insensitive partial match on the name."""
        return self._fetch_neos(
            f"SELECT {COLUMNS} FROM {TABLE} "
            "WHERE LOWER(name) LIKE %(name)s "
            "ORDER BY name;",
            {"name": f"%{name.strip().lower()}%"},
        )

    @log
    def list_all(self) -> list[Neo]:
        """List all neos in the database, sorted by name."""
        return self._fetch_neos(f"SELECT {COLUMNS} FROM {TABLE} ORDER BY name;")

    @log
    def find_by_diameter(self, min_diameter=None, max_diameter=None) -> list[Neo]:
        """Neos whose diameter is within the given bounds."""
        return self._find_between("diameter", min_diameter, max_diameter)

    @log
    def find_by_speed(self, min_speed=None, max_speed=None) -> list[Neo]:
        """Neos whose speed is within the given bounds."""
        return self._find_between("speed", min_speed, max_speed)

    @log
    def find_by_closest_day(self, day: date) -> list[Neo]:
        """Neos whose closest approach is exactly on this day."""
        return self._fetch_neos(
            f"SELECT {COLUMNS} FROM {TABLE} WHERE closest_day = %(day)s ORDER BY name;",
            {"day": day},
        )

    @log
    def find_between_days(self, start: date, end: date) -> list[Neo]:
        """Neos whose closest approach is between two dates (inclusive), soonest first."""
        return self._find_between("closest_day", start, end)

    @log
    def update(self, neo: Neo) -> bool:
        """Update a neo in the database.
        Returns:
            True if exactly one row was updated, False otherwise
        """
        nb_affected_rows = 0

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"UPDATE {TABLE} "
                        "   SET name = %(name)s, "
                        "       diameter = %(diameter)s, "
                        "       distance = %(distance)s, "
                        "       speed = %(speed)s, "
                        "       closest_day = %(closest_day)s, "
                        "       rarity = %(rarity)s "
                        " WHERE id_neo = %(id_neo)s;",
                        {
                            "name": neo.name,
                            "diameter": neo.diameter,
                            "distance": neo.distance,
                            "speed": neo.speed,
                            "closest_day": neo.closest_day,
                            "rarity": neo.rarity,
                            "id_neo": neo.id_neo,
                        },
                    )
                    nb_affected_rows = cursor.rowcount
        except Exception:
            logger.exception("Erreur lors de la mise à jour du NEO")
            raise

        return nb_affected_rows == 1

    @log
    def delete(self, neo: Neo) -> bool:
        """Delete a neo from the database.
        Returns:
            True if the neo was deleted, False otherwise
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"DELETE FROM {TABLE} WHERE id_neo = %(id_neo)s;",
                        {"id_neo": neo.id_neo},
                    )
                    res = cursor.rowcount
        except Exception:
            logger.exception("Erreur lors de la suppression du NEO")
            raise

        return res > 0
