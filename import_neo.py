import os
from datetime import date, timedelta

import psycopg2
import requests
from dotenv import load_dotenv

load_dotenv()

# 1) Appel à l'API NASA NeoWs (7 jours max par requête)
today = date.today()
resp = requests.get(
    "https://api.nasa.gov/neo/rest/v1/feed",
    params={
        "start_date": today.isoformat(),
        "end_date": (today + timedelta(days=6)).isoformat(),
        "api_key": os.getenv("NASA_API_KEY"),
    },
    timeout=30,
)
resp.raise_for_status()
neos_by_day = resp.json()["near_earth_objects"]

# 2) Connexion à PostgreSQL
conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    dbname=os.getenv("POSTGRES_DATABASE"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)

# 3) Insertion (uniquement les champs utiles)
count = 0
with conn, conn.cursor() as cur:
    for day, neos in neos_by_day.items():
        for neo in neos:
            # approche correspondant au jour du feed
            approach = next(
                (
                    a
                    for a in neo["close_approach_data"]
                    if a["close_approach_date"] == day
                ),
                neo["close_approach_data"][0],
            )

            name = neo["name"]
            diameter = neo["estimated_diameter"]["meters"]["estimated_diameter_max"]
            distance = float(approach["miss_distance"]["kilometers"])
            speed = float(approach["relative_velocity"]["kilometers_per_second"])
            closest_day = approach["close_approach_date"]

            # Table neo : insert ou mise à jour, on récupère l'id
            cur.execute(
                """
                INSERT INTO project.neo (name, diameter, distance, speed, closest_day)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (name) DO UPDATE SET
                    diameter = EXCLUDED.diameter,
                    distance = EXCLUDED.distance,
                    speed = EXCLUDED.speed,
                    closest_day = EXCLUDED.closest_day
                RETURNING id_neo
            """,
                (name, diameter, distance, speed, closest_day),
            )
            id_neo = cur.fetchone()[0]

            # Table neodistancehistory : on évite les doublons
            cur.execute(
                """
                INSERT INTO project.neodistancehistory (id_neo, distance, observation_date)
                SELECT %s, %s, %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM project.neodistancehistory
                    WHERE id_neo = %s AND observation_date = %s
                )
            """,
                (id_neo, distance, closest_day, id_neo, closest_day),
            )
            count += 1

conn.close()
print(f"{count} NEO traités.")
