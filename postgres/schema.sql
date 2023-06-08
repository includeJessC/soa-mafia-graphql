CREATE schema "mafia";

CREATE TABLE IF NOT EXISTS mafia.users_ids (
    id INTEGER PRIMARY KEY,
    nickname TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS mafia.user_pdf (
    id INTEGER PRIMARY KEY,
    pdf TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS mafia.users (
    id INTEGER PRIMARY KEY,
    user_name TEXT UNIQUE,
    image_url TEXT,
    sex TEXT,
    email TEXT
);

CREATE TABLE IF NOT EXISTS mafia.games  (
    id INTEGER NOT NULL,
    game_name TEXT NOT NULL,
    winner BOOLEAN DEFAULT FALSE,
    duration BIGINT DEFAULT 0
);