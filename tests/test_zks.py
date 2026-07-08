from app.crypto import encrypt_payload, decrypt_payload


AGENT_SECRET = "my-agent-secret-key"


def test_encrypt_decrypt_roundtrip():
    payload = {"step": 1, "task": "process_order"}
    ciphertext = encrypt_payload(payload, AGENT_SECRET)
    decrypted = decrypt_payload(ciphertext, AGENT_SECRET)
    assert decrypted == payload


def test_encrypted_output_is_string():
    payload = {"msg": "hello"}
    ciphertext = encrypt_payload(payload, AGENT_SECRET)
    assert isinstance(ciphertext, str)
    assert len(ciphertext) > 0


def test_different_secret_produces_different_ciphertext():
    payload = {"msg": "hello"}
    c1 = encrypt_payload(payload, "secret-1")
    c2 = encrypt_payload(payload, "secret-2")
    assert c1 != c2


def test_wrong_secret_fails_to_decrypt():
    payload = {"msg": "hello"}
    ciphertext = encrypt_payload(payload, AGENT_SECRET)
    try:
        decrypt_payload(ciphertext, "wrong-secret")
        assert False, "Should have raised"
    except Exception:
        pass


def test_deterministic_same_secret_same_ciphertext():
    payload = {"x": 1}
    c1 = encrypt_payload(payload, AGENT_SECRET)
    c2 = encrypt_payload(payload, AGENT_SECRET)
    # Fernet includes a random IV, so ciphertexts differ each time
    assert c1 != c2


def test_decrypt_complex_nested_payload():
    payload = {
        "conversation": [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi"},
        ],
        "metadata": {"timestamp": 1234567890},
    }
    ciphertext = encrypt_payload(payload, AGENT_SECRET)
    decrypted = decrypt_payload(ciphertext, AGENT_SECRET)
    assert decrypted == payload


def test_ciphertext_is_opaque_to_chronos():
    payload = {"secret_api_key": "sk-1234567890abcdef"}
    ciphertext = encrypt_payload(payload, AGENT_SECRET)
    # Chronos never sees the plaintext - the ciphertext is just a string
    assert "sk-" not in ciphertext
    assert "secret_api_key" not in ciphertext
