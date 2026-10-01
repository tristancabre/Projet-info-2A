from datetime import datetime

import requests

from dao.db_connection import DBConnection
from service.neo_service import NeoService

# ============================================================
# 1. Récupération des données depuis l'API NASA
# ============================================================

url = "https://ssd-api.jpl.nasa.gov/cad.api"

params = {
    "date-min": "2026-01-01",
    "date-max": "2026-12-31",
    "dist-max": "0.05",
    "neo": "true",
    "body": "Earth",
    "diameter": "true",
    "fullname": "true"
}

response = requests.get(url, params=params)

# Vérification de la requête
response.raise_for_status()

data = response.json()

print("Nombre de résultats :", data["count"])
print("Version API :", data["signature"]["version"])


# ============================================================
# 2. Transformation des données
# ============================================================

fields = data["fields"]
rows = data["data"]

# Transformation des listes en dictionnaires
neos = []

for row in rows:

    neo = dict(zip(fields, row, strict=False))

    neos.append(neo)


# Exemple : afficher le premier NEO
if neos:
    print(neos[0])


# ============================================================
# 3. Connexion à PostgreSQL
# ============================================================

connexion = DBConnection.connection

print("Connexion à PostgreSQL réussie !")

cursor = connexion.cursor()

# ============================================================
# 4. Insertion dans PostgreSQL
# ============================================================


def vers_float(valeur):
    """Convertit en float, ou renvoie None si la valeur est absente."""
    return float(valeur) if valeur is not None else None


requete = """
    INSERT INTO project.neo
        (name, diameter, distance, speed, closest_day, rarity)
    VALUES
        (%s, %s, %s, %s, %s, %s)
"""

for neo in neos:

    name = (neo.get("fullname") or neo.get("des")).strip()

    diameter = vers_float(neo.get("diameter"))
    distance = vers_float(neo.get("dist"))
    speed = vers_float(neo.get("v_rel"))

    date_str = neo.get("cd")

    if date_str:
        closest_day = datetime.strptime(date_str[:11], "%Y-%b-%d").date()
    else:
        closest_day = None

    rarity = NeoService.calcul_rarity(distance)

    cursor.execute(
        requete,
        (name, diameter, distance, speed, closest_day, rarity)
    )


# ============================================================
# 5. Validation des insertions
# ============================================================

connexion.commit()

print(f"{len(neos)} NEO insérés dans PostgreSQL.")


# ============================================================
# 6. Fermeture de la connexion
# ============================================================

cursor.close()
connexion.close()
