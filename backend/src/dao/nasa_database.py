# import os
from datetime import datetime

import psycopg2
import requests
from dotenv import load_dotenv

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

load_dotenv()


# Récupération des variables d'environnement
DB_HOST = "postgresql-cnpg-338919-rw.user-tristancabre"
DB_PORT = "5432"
DB_NAME = "defaultdb"
DB_USER = "user-tristancabre"
DB_PASSWORD = "ias0dmastdgc2h5eex0g"


# Vérification
variables = {
    "DB_HOST": DB_HOST,
    "DB_PORT": DB_PORT,
    "DB_NAME": DB_NAME,
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD
}

variables_manquantes = [
    nom for nom, valeur in variables.items()
    if valeur is None
]

if variables_manquantes:
    raise ValueError(
        f"Variables d'environnement manquantes : "
        f"{', '.join(variables_manquantes)}"
    )


# Connexion
connexion = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

print("Connexion à PostgreSQL réussie !")

cursor = connexion.cursor()

# ============================================================
# 3.bis Quelques fonctions de traitement des données
# ============================================================


def calcul_rarity(distance):
    if distance < 0.01:
        return 5
    elif distance < 0.03:
        return 4
    elif distance < 0.05:
        return 3
    elif distance < 0.1:
        return 2
    else:
        return 1


def vers_float(valeur):
    """Convertit en float, ou renvoie None si la valeur est absente."""
    return float(valeur) if valeur is not None else None

# ============================================================
# 4. Insertion dans PostgreSQL
# ============================================================


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

    rarity = calcul_rarity(distance)

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
