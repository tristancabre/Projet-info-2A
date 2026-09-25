CREATE SCHEMA IF NOT EXISTS project;

-----------------------------------------------------
-- User
-----------------------------------------------------

DROP TABLE IF EXISTS project.user CASCADE;
CREATE TABLE project.user (
    id_user      SERIAL PRIMARY KEY,
    username     VARCHAR(30) UNIQUE NOT NULL,
    password     VARCHAR(256) NOT NULL,
    email        VARCHAR(50) NOT NULL,
    access_token VARCHAR(255)
);

-----------------------------------------------------
-- NEO
-----------------------------------------------------

DROP TABLE IF EXISTS project.neo CASCADE;
CREATE TABLE project.neo (
    id_neo      SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    diameter    INT,
    distance    FLOAT,
    speed       FLOAT,
    magnitude   FLOAT,
    closest_day DATE,
    rarity      INT
);

-----------------------------------------------------
-- Favorites
-----------------------------------------------------

DROP TABLE IF EXISTS project.favorites CASCADE;
CREATE TABLE project.favorites (
    id_favorite SERIAL PRIMARY KEY,
    id_user     INTEGER REFERENCES project.user(id_user) ON DELETE CASCADE,
    id_neo      INTEGER REFERENCES project.neo(id_neo) ON DELETE CASCADE,
    date_added  DATE
);

-----------------------------------------------------
-- Alert
-----------------------------------------------------

DROP TABLE IF EXISTS project.alert CASCADE;
CREATE TABLE project.alert (
    id_alert     SERIAL PRIMARY KEY,
    id_user      INTEGER REFERENCES project.user(id_user) ON DELETE CASCADE,
    id_neo       INTEGER REFERENCES project.neo(id_neo) ON DELETE CASCADE,
    min_size     INT,
    max_size     INT,
    min_distance FLOAT,
    max_distance FLOAT,
    min_speed    FLOAT,   
    max_speed    FLOAT
);

-----------------------------------------------------
-- NeoDistanceHistory
-----------------------------------------------------

DROP TABLE IF EXISTS project.neodistancehistory CASCADE;
CREATE TABLE project.neodistancehistory (
    id_distance_history SERIAL PRIMARY KEY,
    id_neo             INTEGER REFERENCES project.neo(id_neo) ON DELETE CASCADE,
    distance            FLOAT,
    observation_date    DATE
);

-----------------------------------------------------
-- ConnectionLog
-----------------------------------------------------

DROP TABLE IF EXISTS project.connectionlog CASCADE;
CREATE TABLE project.connectionlog (
    id_connection     SERIAL PRIMARY KEY,
    id_user           INTEGER REFERENCES project.user(id_user) ON DELETE CASCADE,
    connection_moment TIMESTAMP
);

-----------------------------------------------------
-- SearchHistory
-----------------------------------------------------

DROP TABLE IF EXISTS project.searchhistory CASCADE;
CREATE TABLE project.searchhistory (
    id_search     SERIAL PRIMARY KEY,
    id_user       INTEGER REFERENCES project.user(id_user) ON DELETE CASCADE,
    search_query  VARCHAR(255),
    search_moment TIMESTAMP
);
