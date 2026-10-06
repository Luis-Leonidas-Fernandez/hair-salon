"""Canonical session cookie management for After Look.

Responsible only for signing, issuing, parsing, and clearing the local
session JWT cookie (`afterlook_session`).
"""

from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Request, Response

from app.modules.identity.schemas import SessionPayload

DEFAULT_SESSION_COOKIE_NAME = "afterlook_session"
DEFAULT_SESSION_TTL_MINUTES = 480  # 8 hours


def issue_session_cookie(
    response: Response,
    *,
    actor_id: int,
    actor_type: str,
    role: str,
    email: str,
    nombre: str,
    profile_complete: bool,
    secret_key: str,
    cookie_name: str = DEFAULT_SESSION_COOKIE_NAME,
    ttl_minutes: int = DEFAULT_SESSION_TTL_MINUTES,
    secure: bool = False,
) -> None:
    """Issue canonical session JWT cookie onto the HTTP response."""
    payload = {
        "sub": str(actor_id),
        "actor_type": actor_type,
        "role": role,
        "email": email,
        "nombre": nombre,
        "profile_complete": profile_complete,
        "exp": datetime.now(UTC) + timedelta(minutes=ttl_minutes),
    }
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    response.set_cookie(
        key=cookie_name,
        value=token,
        max_age=ttl_minutes * 60,
        httponly=True,
        samesite="lax",
        secure=secure,
        path="/",
    )


def extract_session(
    request: Request,
    secret_key: str,
    cookie_name: str = DEFAULT_SESSION_COOKIE_NAME,
) -> SessionPayload | None:
    """Read and validate the session cookie from an incoming request."""
    cookie = request.cookies.get(cookie_name)
    if not cookie:
        return None
    try:
        claims = jwt.decode(
            cookie,
            secret_key,
            algorithms=["HS256"],
            options={"require": ["sub", "actor_type", "role", "email", "exp"]},
        )
        return SessionPayload(
            sub=int(claims["sub"]),
            actor_type=claims["actor_type"],
            role=claims["role"],
            email=claims["email"],
            nombre=claims.get("nombre", ""),
            profile_complete=claims.get("profile_complete", False),
        )
    except (jwt.PyJWTError, KeyError, ValueError):
        return None


def clear_session_cookie(
    response: Response,
    cookie_name: str = DEFAULT_SESSION_COOKIE_NAME,
) -> None:
    """Invalidate canonical session cookie."""
    response.delete_cookie(key=cookie_name, path="/")
