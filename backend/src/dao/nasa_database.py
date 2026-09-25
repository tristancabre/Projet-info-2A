"""
Import des données de l'API NASA/JPL CNEOS Close-Approach (CAD)
vers les tables project.neo et project.neodistancehistory.

Doc API : https://ssd-api.jpl.nasa.gov/doc/cad.html

Dépendances :
    pip install requests psycopg2-binary
"""

from datetime import datetime

import psycopg2
import requests

# -----------------------------------------------------
# Connexion à la base
# -----------------------------------------------------
conn = psycopg2.connect(
    host="localhost",
    dbname="defaultdb",
    user="user-tristancabre",
    password="ias0dmastdgc2h5eex0g",
)
cur = conn.cursor()

# -----------------------------------------------------
# Appel à l'API NASA CAD
# -----------------------------------------------------
URL = "https://ssd-api.jpl.nasa.gov/cad.api"
PARAMS = {
    "date-min": "2020-01-01",
    "date-max": "2030-01-01",
    "dist-max": "0.2",     # 0.2 UA max (~30M km) — à ajuster
    "diameter": "true",    # récupérer le diamètre quand il est connu
    "fullname": "true",
}

response = requests.get(URL, params=PARAMS, timeout=30)
response.raise_for_status()
payload = response.json()

fields = payload["fields"]
records = payload.get("data", [])
print(f"{payload.get('count', 0)} rapprochements récupérés depuis la NASA.")

# -----------------------------------------------------
# Constantes / helpers de conversion
# -----------------------------------------------------
AU_TO_KM = 149_597_870.7


def parse_cad_date(cd_str: str):
    """'2029-Apr-13 21:46' -> date()"""
    return datetime.strptime(cd_str, "%Y-%b-%d %H:%M").date()


def get_or_create_neo(name: str, size_m, distance_km: int, speed_kms: float, closest_day):
    """
    Idempotence : si un NEO du même nom existe déjà, on renvoie son id.
    Sinon on l'insère. (Recommandation : ajouter une contrainte UNIQUE
    sur neo.name, ou mieux, sur une future colonne "designation", pour
    fiabiliser cette vérification.)
    """
    cur.execute("SELECT id_neo FROM project.neo WHERE name = %s", (name,))
    row = cur.fetchone()
    if row:
        return row[0]

    cur.execute(
        """
        INSERT INTO project.neo (name, size, distance, speed, closest_day, origin, rarity)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id_neo
        """,
        (name, size_m, distance_km, speed_kms, closest_day, None, None),
        # origin/rarity: pas fournis par cette API, à compléter manuellement
        # ou via un appel séparé à la SBDB Lookup API pour la classe orbitale.
    )
    return cur.fetchone()[0]


# -----------------------------------------------------
# Traitement des enregistrements
# -----------------------------------------------------
inserted_neo = 0
inserted_history = 0

for raw_row in records:
    record = dict(zip(fields, raw_row, strict=False))

    name = (record.get("fullname") or record["des"]).strip()
    distance = float(record["dist"]) * AU_TO_KM
    speed = float(record["v_rel"])
    closest_day = parse_cad_date(record["cd"])

    diameter = record.get("diameter")
    size = int(float(diameter) * 1000) if diameter else None

    id_neo = get_or_create_neo(name, size, int(distance), speed, closest_day)
    inserted_neo += 1

    cur.execute(
        """
        INSERT INTO project.neodistancehistory (id_neo, distance, observation_date)
        VALUES (%s, %s, %s)
        """,
        (id_neo, distance, closest_day),
    )
    inserted_history += 1

conn.commit()
cur.close()
conn.close()

print(f"{inserted_neo} lignes traitées côté project.neo (créations + réutilisations).")
print(f"{inserted_history} lignes insérées dans project.neodistancehistory.")
