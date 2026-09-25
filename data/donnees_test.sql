-----------------------------------------------------
-- Jeu de données de test pour le schéma "project"
-- A exécuter APRES le script de création des tables
-----------------------------------------------------

-----------------------------------------------------
-- User
-----------------------------------------------------
INSERT INTO project.user (username, password, email, access_token) VALUES
('alice',   'hashed_pw_alice',   'alice@example.com',   'tok_alice_123'),
('bob',     'hashed_pw_bob',     'bob@example.com',     'tok_bob_456'),
('charlie', 'hashed_pw_charlie', 'charlie@example.com', NULL),
('diana',   'hashed_pw_diana',   'diana@example.com',   'tok_diana_789'),
('eve',     'hashed_pw_eve',     'eve@example.com',     NULL);

-----------------------------------------------------
-- NEO (diameter en mètres, distance en km, rarity 1=courant -> 5=très rare)
-----------------------------------------------------
INSERT INTO project.neo (name, diameter, distance, speed, closest_day, rarity) VALUES
('Apophis',        370,  38000.0,      30.7, '2029-04-13', 5),
('Bennu',          490,  750000.0,     28.0, '2135-09-25', 4),
('Icarus',         1400, 6400000.0,    27.4, '2026-06-16', 3),
('2023 DW',        50,   1800000.0,    25.3, '2046-02-14', 2),
('Ryugu',          900,  9500000.0,    15.0, '2027-12-05', 3),
('Didymos',        780,  5900000.0,    23.9, '2028-11-30', 4),
('2010 PK9',       35,   120000.0,     33.6, '2026-10-01', 1),
('Florence',       4500, 7000000.0,    13.9, '2057-09-02', 5);

-----------------------------------------------------
-- Favorites
-----------------------------------------------------
INSERT INTO project.favorites (id_user, id_neo, date_added) VALUES
(1, 1, '2026-01-10'),
(1, 3, '2026-02-15'),
(2, 2, '2026-01-20'),
(3, 1, '2026-03-01'),
(4, 5, '2026-03-10'),
(4, 6, '2026-03-11'),
(5, 7, '2026-04-01');

-----------------------------------------------------
-- Alert
-----------------------------------------------------
INSERT INTO project.alert (id_user, id_neo, min_diameter, max_diameter, min_distance, max_distance, min_speed, max_speed) VALUES
(1, 1,    100, 500,  10000,   50000,   10, 40),
(2, 2,    200, 600,  500000,  1000000, 10, 35),
(3, NULL, 0,   1000, 0,       2000000, 0,  50),
(4, 6,    500, 1000, 4000000, 6000000, 15, 30),
(5, NULL, 0,   100,  0,       500000,  20, 40);

-----------------------------------------------------
-- NeoDistanceHistory
-----------------------------------------------------
INSERT INTO project.neodistancehistory (id_neo, distance, observation_date) VALUES
(1, 42000.5,   '2025-12-01'),
(1, 39500.2,   '2026-01-15'),
(1, 38000.0,   '2026-03-01'),
(2, 780000.0,  '2025-11-10'),
(2, 760000.0,  '2026-02-01'),
(3, 6500000.0, '2025-10-05'),
(3, 6420000.0, '2026-01-20'),
(5, 9600000.0, '2026-02-10'),
(6, 6000000.0, '2026-01-05'),
(7, 130000.0,  '2026-03-15');

-----------------------------------------------------
-- ConnectionLog
-----------------------------------------------------
INSERT INTO project.connectionlog (id_user, connection_moment) VALUES
(1, '2026-09-20 08:15:00'),
(1, '2026-09-22 19:42:00'),
(2, '2026-09-21 10:05:00'),
(3, '2026-09-18 14:30:00'),
(4, '2026-09-23 09:00:00'),
(4, '2026-09-24 21:10:00'),
(5, '2026-09-19 17:25:00');

-----------------------------------------------------
-- SearchHistory
-----------------------------------------------------
INSERT INTO project.searchhistory (id_user, search_query, search_moment) VALUES
(1, 'astéroïdes proches 2026',     '2026-09-20 08:20:00'),
(1, 'Apophis trajectoire',          '2026-09-22 19:45:00'),
(2, 'Bennu mission OSIRIS',         '2026-09-21 10:10:00'),
(3, 'liste NEO dangereux',          '2026-09-18 14:35:00'),
(4, 'Ryugu taille',                 '2026-09-23 09:05:00'),
(5, 'petits astéroïdes rapides',    '2026-09-19 17:30:00');