"""SQLite connection helpers for Surf Heat Manager."""

import hashlib
import sqlite3

DB_FILE = "surf.db"
SCHEMA_FILE = "schema.sql"


def connect():
    """Open the database with rows that behave like dictionaries."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def query(sql, params=()):
    """Run a SELECT and return all rows."""
    conn = connect()
    cursor = conn.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


def run(sql, params=()):
    """Run an INSERT, UPDATE or DELETE and return the new row id."""
    conn = connect()
    cursor = conn.execute(sql, params)
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def hash_password(password):
    """Passwords are stored as a SHA-256 hash, never as plain text."""
    return hashlib.sha256(password.encode()).hexdigest()


def setup():
    """Create the tables and add the default director account."""
    schema_file = open(SCHEMA_FILE)
    schema = schema_file.read()
    schema_file.close()

    conn = connect()
    conn.executescript(schema)
    conn.commit()
    conn.close()

    directors = query("SELECT id FROM users WHERE username = ?", ("director",))
    if len(directors) == 0:
        run("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            ("director", hash_password("surf2024"), "director"))
