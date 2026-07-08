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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS event_subscriptions (
                subscription_id TEXT PRIMARY KEY,
                agent_id TEXT,
                agent_webhook_url TEXT,
                event_name TEXT,
                state_id TEXT,
                created_at REAL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_event_name
            ON event_subscriptions (event_name)
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


def subscribe_event(
    agent_id: str,
    agent_webhook_url: str,
    event_name: str,
    state_id: str,
) -> str:
    subscription_id = str(uuid.uuid4())
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            "INSERT INTO event_subscriptions (subscription_id, agent_id, agent_webhook_url, event_name, state_id, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (subscription_id, agent_id, agent_webhook_url, event_name, state_id, time.time()),
        )
        conn.commit()
    return subscription_id


def get_subscriptions_by_event(event_name: str) -> list[dict[str, Any]]:
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute(
            "SELECT subscription_id, agent_id, agent_webhook_url, event_name, state_id, created_at FROM event_subscriptions WHERE event_name = ?",
            (event_name,),
        )
        rows = cursor.fetchall()
    return [
        {
            "subscription_id": row[0],
            "agent_id": row[1],
            "agent_webhook_url": row[2],
            "event_name": row[3],
            "state_id": row[4],
            "created_at": row[5],
        }
        for row in rows
    ]


def delete_subscription(subscription_id: str) -> bool:
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute(
            "DELETE FROM event_subscriptions WHERE subscription_id = ?",
            (subscription_id,),
        )
        conn.commit()
        return cursor.rowcount > 0
