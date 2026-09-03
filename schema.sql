-- Surf Heat Manager database schema.
-- All table changes belong in this file.

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL          -- 'director' or 'viewer'
);

CREATE TABLE IF NOT EXISTS surfers (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    skill      INTEGER NOT NULL,         -- 1 (beginner) to 10 (advanced)
    group_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS heats (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    round_number INTEGER NOT NULL,
    heat_number  INTEGER NOT NULL
);

-- Which surfers are in which heat (a surfer is in one heat per round).
CREATE TABLE IF NOT EXISTS heat_surfers (
    heat_id   INTEGER NOT NULL REFERENCES heats(id),
    surfer_id INTEGER NOT NULL REFERENCES surfers(id),
    PRIMARY KEY (heat_id, surfer_id)
);

-- One row per wave ridden. Raw judge score is kept separate from the
-- weighted total so the weighting rule can change without losing history.
CREATE TABLE IF NOT EXISTS scores (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    heat_id   INTEGER NOT NULL REFERENCES heats(id),
    surfer_id INTEGER NOT NULL REFERENCES surfers(id),
    raw_score REAL NOT NULL,             -- 0 to 10
    weight    REAL NOT NULL DEFAULT 1.0  -- 1.0 typical, up to 1.3 difficult
);

CREATE TABLE IF NOT EXISTS forecast_slots (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_time   TEXT NOT NULL,           -- e.g. "09:00"
    wave_height REAL NOT NULL,           -- metres
    tide_level  REAL NOT NULL            -- metres
);
