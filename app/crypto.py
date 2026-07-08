import hmac
import hashlib
import json
import base64
from typing import Any

from cryptography.fernet import Fernet


def sign_payload(payload: dict[str, Any], secret: str) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hmac.new(
        secret.encode("utf-8"),
        canonical.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def derive_encryption_key(agent_secret: str) -> bytes:
    raw = hashlib.sha256(agent_secret.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(raw)


def encrypt_payload(payload: dict[str, Any], agent_secret: str) -> str:
    key = derive_encryption_key(agent_secret)
    cipher = Fernet(key)
    plaintext = json.dumps(payload, sort_keys=True).encode("utf-8")
    token = cipher.encrypt(plaintext)
    return base64.urlsafe_b64encode(token).decode("utf-8")


def decrypt_payload(ciphertext_b64: str, agent_secret: str) -> dict[str, Any]:
    key = derive_encryption_key(agent_secret)
    cipher = Fernet(key)
    token = base64.urlsafe_b64decode(ciphertext_b64.encode("utf-8"))
    plaintext = cipher.decrypt(token)
    return json.loads(plaintext.decode("utf-8"))
