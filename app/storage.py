import uuid
import time
from typing import Any


_store: dict[str, dict[str, Any]] = {}


def store(agent_id: str, context_payload: dict[str, Any]) -> str:
    state_id = str(uuid.uuid4())
    _store[state_id] = {
        "agent_id": agent_id,
        "context_payload": context_payload,
        "created_at": time.time(),
    }
    return state_id


def get(state_id: str) -> dict[str, Any] | None:
    return _store.get(state_id)


def delete(state_id: str) -> bool:
    if state_id in _store:
        del _store[state_id]
        return True
    return False
