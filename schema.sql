CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS surfers (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    skill      INTEGER NOT NULL,
    group_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS heats (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    round_number INTEGER NOT NULL,
    heat_number  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS heat_surfers (
    heat_id   INTEGER NOT NULL REFERENCES heats(id),
    surfer_id INTEGER NOT NULL REFERENCES surfers(id),
    PRIMARY KEY (heat_id, surfer_id)
);

CREATE TABLE IF NOT EXISTS scores (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    heat_id   INTEGER NOT NULL REFERENCES heats(id),
    surfer_id INTEGER NOT NULL REFERENCES surfers(id),
    raw_score REAL NOT NULL,
    weight    REAL NOT NULL DEFAULT 1.0
);

CREATE TABLE IF NOT EXISTS forecast_slots (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_time   TEXT NOT NULL,
    wave_height REAL NOT NULL,
    tide_level  REAL NOT NULL
);
