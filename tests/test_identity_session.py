"""Unit tests for canonical session cookie management."""

from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Response
from fastapi.requests import Request

from app.modules.identity.session import (
    clear_session_cookie,
    extract_session,
    issue_session_cookie,
)

SECRET_KEY = "test-secret-key-at-least-32-bytes-long-1234"


def test_issue_and_extract_session() -> None:
    """Session cookie is issued with correct claims and extracted accurately."""
    response = Response()
    issue_session_cookie(
        response,
        actor_id=42,
        actor_type="cliente",
        role="CLIENTE",
        email="cliente@example.com",
        nombre="Juan Pérez",
        profile_complete=True,
        secret_key=SECRET_KEY,
        cookie_name="test_session",
        ttl_minutes=60,
    )

    # Simulate incoming request with the cookie set
    cookie_header = response.headers.get("set-cookie")
    assert cookie_header is not None
    assert "test_session=" in cookie_header
    assert "HttpOnly" in cookie_header

    # Extract the cookie value
    raw_token = cookie_header.split(";")[0].split("=")[1]

    # Create dummy request with cookies
    scope = {
        "type": "http",
        "headers": [(b"cookie", f"test_session={raw_token}".encode())],
    }
    request = Request(scope)

    session = extract_session(request, SECRET_KEY, cookie_name="test_session")
    assert session is not None
    assert session.sub == 42
    assert session.actor_type == "cliente"
    assert session.role == "CLIENTE"
    assert session.email == "cliente@example.com"
    assert session.nombre == "Juan Pérez"
    assert session.profile_complete is True


def test_extract_session_returns_none_when_expired() -> None:
    """Expired session tokens return None without raising unhandled errors."""
    expired_payload = {
        "sub": "1",
        "actor_type": "staff",
        "role": "ADMIN",
        "email": "admin@example.com",
        "exp": datetime.now(UTC) - timedelta(hours=1),
    }
    token = jwt.encode(expired_payload, SECRET_KEY, algorithm="HS256")

    scope = {
        "type": "http",
        "headers": [(b"cookie", f"test_session={token}".encode())],
    }
    request = Request(scope)

    session = extract_session(request, SECRET_KEY, cookie_name="test_session")
    assert session is None


def test_clear_session_cookie() -> None:
    """Clearing session sets cookie max-age to 0."""
    response = Response()
    clear_session_cookie(response, cookie_name="test_session")
    cookie_header = response.headers.get("set-cookie")
    assert cookie_header is not None
    assert 'test_session=""' in cookie_header or "test_session=;" in cookie_header
    assert "Max-Age=0" in cookie_header
