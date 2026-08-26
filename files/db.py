"""
Database layer using SQLite (built into Python, no server setup needed).

Table: urls
  id          -> auto-incrementing integer (this is what we base62-encode)
  long_url    -> the original URL the user submitted
  created_at  -> timestamp
  clicks      -> how many times the short link has been visited
"""

import sqlite3

DB_FILE = "shortener.db"


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            long_url TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            clicks INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def insert_url(long_url: str) -> int:
    """Insert a new long URL and return its auto-generated id."""
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO urls (long_url) VALUES (?)", (long_url,)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def get_url_by_id(url_id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM urls WHERE id = ?", (url_id,)
    ).fetchone()
    conn.close()
    return row


def increment_clicks(url_id: int):
    conn = get_connection()
    conn.execute(
        "UPDATE urls SET clicks = clicks + 1 WHERE id = ?", (url_id,)
    )
    conn.commit()
    conn.close()
