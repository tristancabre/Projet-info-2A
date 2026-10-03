from datetime import datetime

from business_object.neo import Neo
from dao.db_connection import DBConnection
from dao.nasa_dao import NasaDao
from service.neo_service import NeoService
from utils.log_utils import get_logger, log
from utils.singleton import Singleton

logger = get_logger(__name__)


class NeoDao(metaclass=Singleton):
    """ Class containing methods to access NEOs in the database."""

    @staticmethod
    def vers_float(valeur):
        """
        Convertit une valeur en float.
        Retourne None si la valeur est absente.
        """
        return float(valeur) if valeur is not None else None

    nasa_dao = NasaDao()
    neos = nasa_dao.recuperer_donnees_nasa()

    @log
    def inserer_donnees_sql(self, neos: list[dict]) -> bool:
        """
    Insère une liste de NEO dans la base PostgreSQL.

    Args:
        neos: Liste de dictionnaires contenant les données
              récupérées depuis l'API NASA.

    Returns:
        True si l'insertion est réussie, False sinon.
        """

        requete = """
            INSERT INTO project.neo
                (name, diameter, distance, speed, closest_day, rarity)
            VALUES
                (%(name)s, %(diameter)s, %(distance)s, %(speed)s,
                %(closest_day)s, %(rarity)s);
        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:

                    for neo in neos:

                        # Nom du NEO
                        name = (
                            neo.get("fullname")
                            or neo.get("des"))

                        if name:
                            name = name.strip()

                        # Conversion des valeurs numériques
                        diameter = self.vers_float(
                            neo.get("diameter"))

                        distance = self.vers_float(
                            neo.get("dist"))

                        speed = self.vers_float(
                            neo.get("v_rel"))

                        # Conversion de la date
                        date_str = neo.get("cd")

                        if date_str:
                            closest_day = datetime.strptime(
                                date_str[:11],
                                "%Y-%b-%d"
                            ).date()
                        else:
                            closest_day = None

                        # Calcul de la rareté
                        rarity = NeoService.calcul_rarity(
                            distance
                        )

                        # Insertion
                        cursor.execute(
                            requete,
                            {
                                "name": name,
                                "diameter": diameter,
                                "distance": distance,
                                "speed": speed,
                                "closest_day": closest_day,
                                "rarity": rarity
                            }
                        )

            logger.info(
                "%d NEO insérés dans PostgreSQL.",
                len(neos))

            return True

        except Exception as e:
            logger.error(
                "Erreur lors de l'insertion des NEO : %s",
                e)
            raise

    @log
    def create(self, neo: Neo) -> bool:
        """Create a Neo in the database.
        Args:
            Neo to create
        Returns:
            True if creation is successful, False otherwise
        """
        res = None

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO neo(name, id_neo, diameter, distance, closest_day, speed) VALUES "
                        "(%(name)s, %(id_neo)s, %(diameter)s, %(distance)s, %(closest_day)s, %(speed)s) "
                        "RETURNING id_neo;",
                        {
                            "name": neo.name,
                            "id_neo": neo.id_neo,
                            "diameter": neo.diameter,
                            "distance": neo.distance,
                            "closest_day": neo.closest_day,
                            "speed": neo.speed
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        created = False
        if res:
            neo.id_neo = res["id_neo"]
            created = True

        return created

    @log
    def find_by_id(self, id_neo: int) -> Neo:
        """Find a Neo by their id.
        Args:
            id_neo (int): The ID of the Neo to find
        Returns:
            Neo matching the given id
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                            "
                        "  FROM neo                       "
                        " WHERE id_neo = %(id_neo)s;   ",
                        {"id_neo": id_neo},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        neo = None
        if res:
            neo = Neo(
                name=res["name"],
                diameter=res["diameter"],
                distance=res["distance"],
                closest_day=res["closest_day"],
                id_neo=res["id_neo"],
                speed=res["speed"]
            )

        return neo

    @log
    def find_by_name(self, name: str) -> Neo:
        """Find a Neo by its name.
        Args:
            name (str): The name of the Neo to find
        Returns:
            Neo matching the given name
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                      "
                        "  FROM neo                    "
                        " WHERE name = %(name)s;       ",
                        {"name": name},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        neo = None
        if res:
            neo = Neo(
                name=res["name"],
                id_neo=res["id_neo"],
                diameter=res["diameter"],
                distance=res["distance"],
                composition=res["composition"],
                closest_day=res["closest_day"],
                speed=res["speed"]
            )

        return neo

    @log
    def list_all(self) -> list[Neo]:
        """List all neos in the database.
        Returns:
            list[neo] sorted by name
        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                                "
                        "  FROM neo                           "
                        " ORDER BY name;                     "
                    )
                    res = cursor.fetchall()
        except Exception as e:
            logger.error(e)
            raise

        neos_list = []

        if res:
            for row in res:
                neo = Neo(
                    id_neo=row["id_neo"],
                    name=row["name"],
                    diameter=row["diameter"],
                    distance=row["distance"],
                    closest_day=row["closest_day"],
                    speed=row["speed"]
                )

                neos_list.append(neo)

        return neos_list

    @log
    def update(self, neo) -> bool:
        """Update a neo in the database.
        Args:
            neo to be updated
        Returns:
            True if update is successful, False otherwise
        """
        nb_affected_rows = 0

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE neo                                                  "
                        "   SET name = %(name)s,                                "
                        "       diameter = %(diameter)s,                                          "
                        "       distance = %(distance)s,                                      "
                        "       closest_day = %(closest_day)s,                        "
                        "       speed = %(speed)s,                       "
                        " WHERE id_neo = %(id_neo)s;                              ",
                        {
                            "name": neo.name,
                            "diameter": neo.diameter,
                            "distance": neo.distance,
                            "closest_day": neo.closest_day,
                            "id_neo": neo.id_neo,
                            "speed": neo.speed
                        },
                    )
                    nb_affected_rows = cursor.rowcount
        except Exception as e:
            logger.error(e)
            raise

        return nb_affected_rows == 1

    @log
    def delete(self, neo) -> bool:
        """Delete a neo from the database.
        Args:
            neo to delete from the database
        Returns:
            True if the neo was successfully deleted, False otherwise
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM neo                               "
                        " WHERE id_neo = %(id_neo)s                 ",
                        {"id_neo": neo.id_neo},
                    )
                    res = cursor.rowcount
        except Exception as e:
            logger.error(e)
            raise

        return res > 0
