import hashlib
import sqlite3

DB_FILE = "surf.db"
SCHEMA_FILE = "schema.sql"


def connect():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def query(sql, params=()):
    conn = connect()
    cursor = conn.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


def run(sql, params=()):
    conn = connect()
    cursor = conn.execute(sql, params)
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def setup():
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
