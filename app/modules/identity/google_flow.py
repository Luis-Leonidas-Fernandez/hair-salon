"""Ephemeral state management for Google OAuth authorization flow.

Responsible only for cryptographically generating, encoding, and verifying
the transient flow parameters (PKCE verifier, state, nonce, attempt_id).
"""

import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt

GOOGLE_FLOW_COOKIE_NAME = "afterlook_google_flow"
GOOGLE_FLOW_TTL = timedelta(minutes=5)


@dataclass(frozen=True, slots=True)
class GoogleFlowState:
    """Ephemeral authorization context carried during the Google round-trip."""

    attempt_id: str
    state: str
    nonce: str
    verifier: str
    source: str


def create_google_flow(source: str = "web") -> GoogleFlowState:
    """Generate cryptographically secure parameters for a new authorization attempt."""
    return GoogleFlowState(
        attempt_id=secrets.token_hex(12),
        state=secrets.token_urlsafe(32),
        nonce=secrets.token_urlsafe(32),
        verifier=secrets.token_urlsafe(64),
        source=source,
    )


def encode_flow_state(flow: GoogleFlowState, secret_key: str) -> str:
    """Encode and sign the flow parameters into a short-lived HS256 JWT."""
    payload = {
        "type": "afterlook_flow",
        "attempt_id": flow.attempt_id,
        "state": flow.state,
        "nonce": flow.nonce,
        "verifier": flow.verifier,
        "source": flow.source,
        "exp": datetime.now(UTC) + GOOGLE_FLOW_TTL,
    }
    return jwt.encode(payload, secret_key, algorithm="HS256")


def decode_flow_state(token: str, secret_key: str) -> GoogleFlowState:
    """Verify signature, expiration and claims of the ephemeral flow cookie."""
    claims = jwt.decode(
        token,
        secret_key,
        algorithms=["HS256"],
        options={
            "require": [
                "type",
                "attempt_id",
                "state",
                "nonce",
                "verifier",
                "source",
                "exp",
            ]
        },
    )
    if claims.get("type") != "afterlook_flow":
        raise ValueError("Invalid flow token type")

    return GoogleFlowState(
        attempt_id=claims["attempt_id"],
        state=claims["state"],
        nonce=claims["nonce"],
        verifier=claims["verifier"],
        source=claims["source"],
    )
