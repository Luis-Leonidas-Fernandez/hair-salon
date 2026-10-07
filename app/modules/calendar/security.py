"""Security utilities for calendar feed authentication (ADR-018, CU-012)."""

import hashlib
import hmac
import secrets


def generate_hairdresser_feed_token(hairdresser_id: int, secret_key: str) -> str:
    """Calcula un token criptográfico determinista para el feed del peluquero."""
    message = f"afterlook-calendar-feed:{hairdresser_id}".encode()
    key = secret_key.encode("utf-8")
    return hmac.new(key, message, hashlib.sha256).hexdigest()[:32]


def verify_hairdresser_feed_token(
    hairdresser_id: int, token: str, secret_key: str
) -> bool:
    """Verifica en tiempo constante que el token pertenezca al peluquero."""
    if not token or len(token) != 32:
        return False
    expected_token = generate_hairdresser_feed_token(hairdresser_id, secret_key)
    return secrets.compare_digest(expected_token, token)
