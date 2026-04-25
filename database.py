"""
Database Manager - SQLite
Multi-group settings store karta hai
"""

import sqlite3
import os

DB_PATH = "vcbot.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Tables create karo on startup"""
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                group_id    INTEGER PRIMARY KEY,
                name        TEXT DEFAULT '',
                join_as     INTEGER DEFAULT 0,
                volume      INTEGER DEFAULT 100,
                pitch       REAL    DEFAULT 1.0,
                echo        INTEGER DEFAULT 0,
                added_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key   TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        conn.commit()
    print("✅ Database initialized.")


# ── Group CRUD ────────────────────────────────────────────────────────────────

def add_group(group_id: int, name: str = "", join_as: int = 0):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO groups (group_id, name, join_as)
            VALUES (?, ?, ?)
            ON CONFLICT(group_id) DO UPDATE SET name=excluded.name
        """, (group_id, name, join_as))
        conn.commit()


def remove_group(group_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM groups WHERE group_id = ?", (group_id,))
        conn.commit()


def get_all_groups() -> list:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM groups ORDER BY added_at").fetchall()
        return [dict(r) for r in rows]


def get_group(group_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM groups WHERE group_id = ?", (group_id,)
        ).fetchone()
        return dict(row) if row else None


def update_group(group_id: int, **kwargs):
    """Update kisi bhi column ko: volume, pitch, echo, join_as"""
    allowed = {"volume", "pitch", "echo", "join_as", "name"}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return
    sets = ", ".join(f"{k}=?" for k in fields)
    vals = list(fields.values()) + [group_id]
    with get_conn() as conn:
        conn.execute(f"UPDATE groups SET {sets} WHERE group_id=?", vals)
        conn.commit()


# ── Global settings ───────────────────────────────────────────────────────────

def set_setting(key: str, value: str):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """, (key, value))
        conn.commit()


def get_setting(key: str, default: str = "") -> str:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT value FROM settings WHERE key=?", (key,)
        ).fetchone()
        return row[0] if row else default
