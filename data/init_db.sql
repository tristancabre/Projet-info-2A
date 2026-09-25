CREATE SCHEMA project

-----------------------------------------------------
-- User
-----------------------------------------------------
DROP TABLE IF EXISTS project.user CASCADE;
CREATE TABLE project.user (
    id_user    SERIAL PRIMARY KEY,
    username     VARCHAR(30) UNIQUE,
    password     VARCHAR(256),
    email        VARCHAR(50),
    access_token VARCHAR(255)
);

-----------------------------------------------------
-- NEO
-----------------------------------------------------

DROP TABLE IF EXISTS project.neo CASCADE;
CREATE TABLE project.neo (
    id_neo      SERIAL PRIMARY KEY,
    name        VARCHAR(255),
    size        INT,
    distance    INT,
    speed       FLOAT,
    closest_day DATE,
    origin      VARCHAR(255),
    rarity      INT
);

-----------------------------------------------------
-- Favorites
-----------------------------------------------------

DROP TABLE IF EXISTS project.favorites CASCADE;
CREATE TABLE project.favorites (
    id_favorite SERIAL PRIMARY KEY,
    id_user INTEGER REFERENCES project.user(id_user),
    id_neo INTEGER REFERENCES project.neo(id_neo),
    date_added  DATE
);

-----------------------------------------------------
-- Alert
-----------------------------------------------------

DROP TABLE IF EXISTS project.alerte CASCADE;
CREATE TABLE project.alert (
    id_alert SERIAL PRIMARY KEY,
    id_user INTEGER REFERENCES project.user(id_user),
    id_neo INTEGER REFERENCES project.neo(id_neo),
    min_size    INT,
    max_size    INT,
    min_distance   INT,
    max_distance   INT,
    min_speed    INT,
    max_speed    INT
);

-----------------------------------------------------
-- NeoDistanceHistory
-----------------------------------------------------

DROP TABLE IF EXISTS project.neodistancehistory CASCADE;
CREATE TABLE project.neodistancehistory (
    id_distance_history SERIAL PRIMARY KEY,
    id_neo INTEGER REFERENCES project.neo(id_neo),
    distance    FLOAT,
    observation_date  DATE
);

-----------------------------------------------------
-- ConnectionLog
-----------------------------------------------------

DROP TABLE IF EXISTS project.connectionlog CASCADE;
CREATE TABLE project.connectionlog (
    id_connection SERIAL PRIMARY KEY,
    id_user INTEGER REFERENCES project.user(id_user),
    connection_moment   TIMESTAMP
);

-----------------------------------------------------
-- SearchHistory
-----------------------------------------------------

DROP TABLE IF EXISTS project.searchhistory CASCADE;
CREATE TABLE project.searchhistory (
    id_search SERIAL PRIMARY KEY,
    id_user INTEGER REFERENCES project.user(id_user),
    search_query    VARCHAR(255),
    search_moment   TIMESTAMP
);
