"""Integration tests for identity HTTP router endpoints using TestClient."""

from fastapi.testclient import TestClient

from app.config.settings import Settings, get_settings
from app.main import app
from app.modules.identity.google_adapter import GoogleOAuthError
from app.modules.identity.google_flow import (
    GOOGLE_FLOW_COOKIE_NAME,
    GoogleFlowState,
    encode_flow_state,
)
from app.modules.identity.google_port import IdentityProvider, VerifiedIdentity
from app.modules.identity.router import get_identity_provider
from app.modules.identity.service import AuthenticatedActor
from app.modules.identity.session import issue_session_cookie

SECRET_KEY = "test-secret-key-at-least-32-bytes-long-1234"


class FakeRouterIdentityProvider(IdentityProvider):
    def __init__(
        self, should_fail: bool = False, actor_identity: VerifiedIdentity | None = None
    ) -> None:
        self.should_fail = should_fail
        self.identity = actor_identity or VerifiedIdentity(
            subject="google-sub-mock",
            email="mockuser@example.com",
            name="Mock User",
        )

    def build_authorization_url(self, *, state: str, nonce: str, verifier: str) -> str:
        return f"https://accounts.google.com/test?state={state}&nonce={nonce}"

    async def exchange_code(
        self, *, code: str, expected_nonce: str, code_verifier: str
    ) -> VerifiedIdentity:
        if self.should_fail:
            raise GoogleOAuthError("GOOGLE_AUTH_FAILED", "Failed exchange")
        return self.identity


def get_test_settings(google_enabled: bool = True) -> Settings:
    return Settings(
        app_name="Test After Look",
        app_version="0.1.0",
        environment="development",
        database_url="postgresql+asyncpg://postgres:pass@localhost:5432/test",
        secret_key=SECRET_KEY,
        seed_admin_name="Admin",
        seed_admin_email="admin@example.com",
        seed_hairdresser_1_name="Hair1",
        seed_hairdresser_1_email="hair1@example.com",
        seed_hairdresser_2_name="Hair2",
        seed_hairdresser_2_email="hair2@example.com",
        google_client_id="mock-client-id" if google_enabled else None,
        google_client_secret="mock-secret" if google_enabled else None,
        google_redirect_uri="http://127.0.0.1:8000/auth/google/callback"
        if google_enabled
        else None,
        session_cookie_name="afterlook_session",
    )


def test_start_endpoint_503_when_disabled() -> None:
    """Returns 503 if Google OAuth credentials are not configured."""
    app.dependency_overrides[get_settings] = lambda: get_test_settings(
        google_enabled=False
    )
    client = TestClient(app)

    response = client.get("/auth/google/start", follow_redirects=False)
    assert response.status_code == 503
    assert response.json()["detail"] == "GOOGLE_NOT_CONFIGURED"

    app.dependency_overrides.clear()


def test_start_endpoint_redirects_and_sets_flow_cookie() -> None:
    """Returns 303 Redirect to Google with PKCE challenge and sets flow cookie."""
    app.dependency_overrides[get_settings] = lambda: get_test_settings(
        google_enabled=True
    )
    app.dependency_overrides[get_identity_provider] = lambda: (
        FakeRouterIdentityProvider()
    )
    client = TestClient(app)

    response = client.get("/auth/google/start?source=web", follow_redirects=False)
    assert response.status_code == 303
    assert "https://accounts.google.com/test" in response.headers["location"]

    set_cookie = response.headers.get("set-cookie")
    assert set_cookie is not None
    assert GOOGLE_FLOW_COOKIE_NAME in set_cookie
    assert "Path=/auth/google" in set_cookie
    assert "HttpOnly" in set_cookie

    app.dependency_overrides.clear()


def test_callback_handles_google_access_denied() -> None:
    """Redirects to /registro with GOOGLE_ACCESS_DENIED on error query param."""
    app.dependency_overrides[get_settings] = lambda: get_test_settings(
        google_enabled=True
    )
    client = TestClient(app)

    response = client.get(
        "/auth/google/callback?error=access_denied", follow_redirects=False
    )
    assert response.status_code == 303
    assert "/registro/?auth_error=GOOGLE_ACCESS_DENIED" in response.headers["location"]

    app.dependency_overrides.clear()


def test_callback_handles_expired_or_missing_flow_cookie() -> None:
    """Redirects to /registro with GOOGLE_SESSION_EXPIRED when cookie is missing."""
    app.dependency_overrides[get_settings] = lambda: get_test_settings(
        google_enabled=True
    )
    client = TestClient(app)

    response = client.get(
        "/auth/google/callback?code=mock_code&state=mock_state", follow_redirects=False
    )
    assert response.status_code == 303
    assert (
        "/registro/?auth_error=GOOGLE_SESSION_EXPIRED" in response.headers["location"]
    )

    app.dependency_overrides.clear()


def test_callback_successful_new_client_redirects_to_complete_data() -> None:
    """Callback for client needing CU-002 redirects to completar_datos."""
    settings = get_test_settings(google_enabled=True)
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_identity_provider] = lambda: (
        FakeRouterIdentityProvider()
    )

    # Mock service resolution
    from unittest.mock import patch

    mock_actor = AuthenticatedActor(
        actor_id=45,
        actor_type="cliente",
        role="CLIENTE",
        email="nuevo@example.com",
        nombre="Nuevo Cliente",
        profile_complete=False,
    )

    flow = GoogleFlowState(
        attempt_id="abcdef123456",
        state="valid_state_123",
        nonce="valid_nonce_123",
        verifier="valid_verifier_123",
        source="web",
    )
    flow_cookie = encode_flow_state(flow, settings.secret_key)

    client = TestClient(app)
    client.cookies.set(GOOGLE_FLOW_COOKIE_NAME, flow_cookie, path="/auth/google")

    with patch(
        "app.modules.identity.router.authenticate_and_resolve_actor",
        return_value=mock_actor,
    ):
        response = client.get(
            "/auth/google/callback?code=good_code&state=valid_state_123",
            follow_redirects=False,
        )

    assert response.status_code == 303
    assert response.headers["location"] == "/reservas/?completar_datos=1"

    set_cookie = response.headers.get("set-cookie")
    assert set_cookie is not None
    assert "afterlook_session=" in set_cookie

    app.dependency_overrides.clear()


def test_me_endpoint_unauthenticated() -> None:
    """Returns 401 when no session cookie is provided."""
    app.dependency_overrides[get_settings] = lambda: get_test_settings(
        google_enabled=True
    )
    client = TestClient(app)

    response = client.get("/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "NOT_AUTHENTICATED"

    app.dependency_overrides.clear()


def test_me_endpoint_authenticated() -> None:
    """Returns current user claims when valid session cookie is provided."""
    from fastapi import Response

    settings = get_test_settings(google_enabled=True)
    app.dependency_overrides[get_settings] = lambda: settings

    client = TestClient(app)
    dummy_resp = Response()
    issue_session_cookie(
        dummy_resp,
        actor_id=12,
        actor_type="staff",
        role="ADMIN",
        email="admin@example.com",
        nombre="Administrator",
        profile_complete=True,
        secret_key=settings.secret_key,
        cookie_name=settings.session_cookie_name,
    )
    raw_cookie = dummy_resp.headers["set-cookie"].split(";")[0].split("=")[1]
    client.cookies.set(settings.session_cookie_name, raw_cookie)

    response = client.get("/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 12
    assert data["actor_type"] == "staff"
    assert data["role"] == "ADMIN"
    assert data["email"] == "admin@example.com"
    assert data["nombre"] == "Administrator"
    assert data["profile_complete"] is True

    app.dependency_overrides.clear()


def test_logout_endpoint_clears_cookie() -> None:
    """Logout endpoint returns status logged_out and clears session cookie."""
    settings = get_test_settings(google_enabled=True)
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)

    response = client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json() == {"status": "logged_out"}
    set_cookie = response.headers.get("set-cookie")
    assert set_cookie is not None
    assert "afterlook_session=" in set_cookie
    assert "Max-Age=0" in set_cookie

    app.dependency_overrides.clear()
