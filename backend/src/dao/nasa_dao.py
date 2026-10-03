from datetime import datetime

import requests

from dao.db_connection import DBConnection
from service.neo_service import NeoService


class NasaDao:
    """
    Classe permettant de récupérer les NEO depuis l'API NASA
    et de les enregistrer dans la base PostgreSQL.
    """

    URL = "https://ssd-api.jpl.nasa.gov/cad.api"

    def __init__(self):
        self.connection = DBConnection.connection

    @staticmethod
    def vers_float(valeur):
        """
        Convertit une valeur en float.
        Retourne None si la valeur est absente.
        """

        return (
            float(valeur)
            if valeur is not None
            else None
        )

    def recuperer_donnees_nasa(self):
        """
        Récupère les données des NEO depuis l'API NASA.

        Returns
        -------
        list
            Liste de dictionnaires contenant les données des NEO.
        """

        params = {
            "date-min": "2026-01-01",
            "date-max": "2026-12-31",
            "dist-max": "0.05",
            "neo": "true",
            "body": "Earth",
            "diameter": "true",
            "fullname": "true"
        }

        # Requête vers l'API NASA
        response = requests.get(
            self.URL,
            params=params,
            timeout=10
        )

        # Vérification de la réponse
        response.raise_for_status()

        data = response.json()

        print("Nombre de résultats :", data["count"])
        print("Version API :", data["signature"]["version"])

        # Récupération des champs et des données
        fields = data["fields"]
        rows = data["data"]

        # Transformation en dictionnaires
        neos = []

        for row in rows:
            neo = dict(zip(fields, row, strict=False))
            neos.append(neo)

        return neos

    def inserer_donnees_sql(self, neos):
        """
        Insère les NEO dans la base PostgreSQL.

        Parameters
        ----------
        neos : list
            Liste des NEO récupérés depuis l'API NASA.
        """

        requete = """
            INSERT INTO project.neo
                (name, diameter, distance, speed, closest_day, rarity)
            VALUES
                (%s, %s, %s, %s, %s, %s)
        """

        cursor = self.connection.cursor()

        try:

            for neo in neos:

                # Nom du NEO
                name = (
                    neo.get("fullname")
                    or neo.get("des")
                ).strip()

                # Conversion des valeurs numériques
                diameter = self.vers_float(
                    neo.get("diameter")
                )

                distance = self.vers_float(
                    neo.get("dist")
                )

                speed = self.vers_float(
                    neo.get("v_rel")
                )

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
                rarity = NeoService.calcul_rarity(distance)

                # Insertion
                cursor.execute(
                    requete,
                    (
                        name,
                        diameter,
                        distance,
                        speed,
                        closest_day,
                        rarity
                    )
                )

            # Validation des insertions
            self.connection.commit()

            print(
                f"{len(neos)} NEO insérés dans PostgreSQL."
            )

        except Exception as e:

            # Annulation des modifications en cas d'erreur
            self.connection.rollback()

            print(
                "Erreur lors de l'insertion des NEO :",
                e
            )

            raise

        finally:

            cursor.close()

    def fermer_connection(self):
        """
        Ferme la connexion à PostgreSQL.
        """

        self.connection.close()
