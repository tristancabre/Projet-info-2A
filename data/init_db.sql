-----------------------------------------------------
-- User
-----------------------------------------------------
DROP TABLE IF EXISTS user CASCADE;
CREATE TABLE user (
    id_player    SERIAL PRIMARY KEY,
    username     VARCHAR(30) UNIQUE,
    password     VARCHAR(256),
    email        VARCHAR(50),
    access_token VARCHAR(255)
);


