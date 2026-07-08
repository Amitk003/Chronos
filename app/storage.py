import sqlite3
import uuid
import time
import json
from typing import Any

DB_FILE = "chronos.db"


def get_db_path() -> str:
    return DB_FILE


def set_db_path(path: str) -> None:
    global DB_FILE
    DB_FILE = path
    init_db()


def init_db() -> None:
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS states (
                state_id TEXT PRIMARY KEY,
                agent_id TEXT,
                ciphertext TEXT,
                created_at REAL
            )
        """)
        conn.commit()


init_db()


def store(agent_id: str, ciphertext: str) -> str:
    state_id = str(uuid.uuid4())
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            "INSERT INTO states (state_id, agent_id, ciphertext, created_at) VALUES (?, ?, ?, ?)",
            (state_id, agent_id, ciphertext, time.time()),
        )
        conn.commit()
    return state_id


def get(state_id: str) -> dict[str, Any] | None:
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute(
            "SELECT agent_id, ciphertext, created_at FROM states WHERE state_id = ?",
            (state_id,),
        )
        row = cursor.fetchone()
    if row is None:
        return None
    return {
        "agent_id": row[0],
        "ciphertext": row[1],
        "created_at": row[2],
    }


def delete(state_id: str) -> bool:
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute(
            "DELETE FROM states WHERE state_id = ?", (state_id,)
        )
        conn.commit()
        return cursor.rowcount > 0
