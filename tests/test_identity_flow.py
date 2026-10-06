"""Unit tests for ephemeral Google OAuth flow state management."""

from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.modules.identity.google_flow import (
    create_google_flow,
    decode_flow_state,
    encode_flow_state,
)

SECRET_KEY = "test-secret-key-at-least-32-bytes-long"


def test_create_and_decode_flow_state() -> None:
    """A valid flow state encodes to JWT and decodes back accurately."""
    flow = create_google_flow(source="web")

    assert len(flow.attempt_id) == 24
    assert len(flow.state) > 20
    assert len(flow.nonce) > 20
    assert len(flow.verifier) > 40
    assert flow.source == "web"

    token = encode_flow_state(flow, SECRET_KEY)
    assert isinstance(token, str)

    decoded = decode_flow_state(token, SECRET_KEY)
    assert decoded.attempt_id == flow.attempt_id
    assert decoded.state == flow.state
    assert decoded.nonce == flow.nonce
    assert decoded.verifier == flow.verifier
    assert decoded.source == flow.source


def test_decode_flow_state_rejects_expired() -> None:
    """Expired flow tokens must be rejected."""
    flow = create_google_flow(source="admin")
    expired_payload = {
        "type": "afterlook_flow",
        "attempt_id": flow.attempt_id,
        "state": flow.state,
        "nonce": flow.nonce,
        "verifier": flow.verifier,
        "source": flow.source,
        "exp": datetime.now(UTC) - timedelta(seconds=10),
    }
    expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm="HS256")

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_flow_state(expired_token, SECRET_KEY)


def test_decode_flow_state_rejects_invalid_type() -> None:
    """Tokens without type afterlook_flow must be rejected."""
    flow = create_google_flow()
    invalid_payload = {
        "type": "other_token",
        "attempt_id": flow.attempt_id,
        "state": flow.state,
        "nonce": flow.nonce,
        "verifier": flow.verifier,
        "source": flow.source,
        "exp": datetime.now(UTC) + timedelta(minutes=5),
    }
    token = jwt.encode(invalid_payload, SECRET_KEY, algorithm="HS256")

    with pytest.raises(ValueError, match="Invalid flow token type"):
        decode_flow_state(token, SECRET_KEY)


def test_decode_flow_state_rejects_wrong_secret() -> None:
    """Tokens signed with a different key fail signature verification."""
    flow = create_google_flow()
    token = encode_flow_state(flow, SECRET_KEY)

    with pytest.raises(jwt.InvalidSignatureError):
        decode_flow_state(token, "different-secret-key-32-chars-long")
