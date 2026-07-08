import hmac
import hashlib
import json
from typing import Any


def sign_payload(payload: dict[str, Any], secret: str) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hmac.new(
        secret.encode("utf-8"),
        canonical.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
