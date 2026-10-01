from dao.db_connection import DBConnection


def create_database():

    connection = DBConnection.connection
    cursor = connection.cursor()

    try:

        # Création du schéma
        cursor.execute("""
            CREATE SCHEMA IF NOT EXISTS project;
        """)

        # --------------------------------------------------
        # User
        # --------------------------------------------------

        cursor.execute("""
            DROP TABLE IF EXISTS project.users CASCADE;

            CREATE TABLE project.users (
                id_user      SERIAL PRIMARY KEY,
                username     VARCHAR(30) UNIQUE NOT NULL,
                password     VARCHAR(256) NOT NULL,
                email        VARCHAR(50) NOT NULL,
                access_token VARCHAR(255)
            );
        """)

        # --------------------------------------------------
        # NEO
        # --------------------------------------------------

        cursor.execute("""
            DROP TABLE IF EXISTS project.neo CASCADE;

            CREATE TABLE project.neo (
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
            DROP TABLE IF EXISTS project.favorites CASCADE;

            CREATE TABLE project.favorites (
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
            DROP TABLE IF EXISTS project.alert CASCADE;

            CREATE TABLE project.alert (
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
            DROP TABLE IF EXISTS project.neodistancehistory CASCADE;

            CREATE TABLE project.neodistancehistory (
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
            DROP TABLE IF EXISTS project.connectionlog CASCADE;

            CREATE TABLE project.connectionlog (
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
            DROP TABLE IF EXISTS project.searchhistory CASCADE;

            CREATE TABLE project.searchhistory (
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
        connection.close()


if __name__ == "__main__":
    create_database()
