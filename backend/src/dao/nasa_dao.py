import requests

from dao.db_connection import DBConnection


class NasaDao:
    """
    Classe permettant de récupérer les NEO depuis l'API NASA
    et de les enregistrer dans la base PostgreSQL.
    """

    URL = "https://ssd-api.jpl.nasa.gov/cad.api"

    def __init__(self):
        self.connection = DBConnection().connection

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

    def fermer_connection(self):
        """
        Ferme la connexion à PostgreSQL.
        """

        self.connection.close()
