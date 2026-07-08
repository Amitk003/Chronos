from app.crypto import sign_payload


def test_sign_payload_returns_hex_string():
    sig = sign_payload({"a": 1}, "secret")
    assert isinstance(sig, str)
    assert len(sig) == 64
    assert all(c in "0123456789abcdef" for c in sig)


def test_sign_payload_deterministic():
    payload = {"msg": "hello", "num": 42}
    sig1 = sign_payload(payload, "secret")
    sig2 = sign_payload(payload, "secret")
    assert sig1 == sig2


def test_sign_payload_different_secret():
    sig1 = sign_payload({"a": 1}, "secret1")
    sig2 = sign_payload({"a": 1}, "secret2")
    assert sig1 != sig2


def test_sign_payload_different_payload():
    sig1 = sign_payload({"a": 1}, "secret")
    sig2 = sign_payload({"b": 2}, "secret")
    assert sig1 != sig2


def test_sign_payload_sort_keys():
    sig1 = sign_payload({"b": 2, "a": 1}, "secret")
    sig2 = sign_payload({"a": 1, "b": 2}, "secret")
    assert sig1 == sig2
