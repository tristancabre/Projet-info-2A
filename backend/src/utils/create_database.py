from dao.db_connection import DBConnection


def create_database():
    connection = DBConnection().connection
    cursor = connection.cursor()

    try:
        cursor.execute("""
            CREATE SCHEMA IF NOT EXISTS project;
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project.users (
                id_user      SERIAL PRIMARY KEY,
                username     VARCHAR(30) UNIQUE NOT NULL,
                password     VARCHAR(256) NOT NULL,
                email        VARCHAR(50) NOT NULL,
                access_token VARCHAR(255),
                is_admin     BOOLEAN
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project.neo (
                id_neo      SERIAL PRIMARY KEY,
                name        VARCHAR(255) NOT NULL,
                diameter    FLOAT,
                distance    FLOAT,
                speed       FLOAT,
                closest_day DATE,
                rarity      INT
            );
        """)

        # --------------------------------------------------
        # Favorites
        # --------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project.favorites (
                id_favorite SERIAL PRIMARY KEY,
                id_user     INTEGER REFERENCES project.users(id_user)
                            ON DELETE CASCADE,
                id_neo      INTEGER REFERENCES project.neo(id_neo)
                            ON DELETE CASCADE,
                date_added  DATE
            );
        """)

        # --------------------------------------------------
        # Alert
        # --------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project.alert (
                id_alert        SERIAL PRIMARY KEY,
                id_user         INTEGER REFERENCES project.users(id_user)
                                ON DELETE CASCADE,
                id_neo          INTEGER REFERENCES project.neo(id_neo)
                                ON DELETE CASCADE,
                min_diameter    INT,
                max_diameter    INT,
                min_distance    FLOAT,
                max_distance    FLOAT,
                min_speed       FLOAT,
                max_speed       FLOAT
            );
        """)

        # --------------------------------------------------
        # NeoDistanceHistory
        # --------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project.neodistancehistory (
                id_distance_history SERIAL PRIMARY KEY,
                id_neo              INTEGER
                                     REFERENCES project.neo(id_neo)
                                     ON DELETE CASCADE,
                distance             FLOAT,
                observation_date     DATE
            );
        """)

        # --------------------------------------------------
        # ConnectionLog
        # --------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project.connectionlog (
                id_connection     SERIAL PRIMARY KEY,
                id_user           INTEGER
                                   REFERENCES project.users(id_user)
                                   ON DELETE CASCADE,
                connection_moment TIMESTAMP
            );
        """)

        # --------------------------------------------------
        # SearchHistory
        # --------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project.searchhistory (
                id_search     SERIAL PRIMARY KEY,
                id_user       INTEGER
                              REFERENCES project.users(id_user)
                              ON DELETE CASCADE,
                search_query  VARCHAR(255),
                search_moment TIMESTAMP
            );
        """)

        # Validation de toutes les requêtes
        connection.commit()

        print("Base de données créée avec succès !")

    except Exception as e:

        # Annulation si une erreur survient
        connection.rollback()

        print("Erreur lors de la création de la base :")
        print(e)

    finally:

        cursor.close()


if __name__ == "__main__":
    create_database()
