"""Concrete OpenID Connect adapter for Google Identity Provider.

Responsible only for network communication with Google OAuth2 endpoints
and cryptographic verification of Google ID tokens.
"""

import base64
import hashlib
import secrets
from urllib.parse import urlencode

import httpx
from fastapi.concurrency import run_in_threadpool
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2 import id_token

from app.modules.identity.google_port import IdentityProvider, VerifiedIdentity

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


class GoogleOAuthError(Exception):
    """Domain exception raised when Google OAuth verification fails."""

    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


class GoogleOIDCAdapter(IdentityProvider):
    """Production implementation of IdentityProvider connecting to Google."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        timeout_seconds: float = 10.0,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.timeout_seconds = timeout_seconds

    def build_authorization_url(self, *, state: str, nonce: str, verifier: str) -> str:
        """Compute S256 PKCE challenge and format the Google authorization redirect."""
        digest = hashlib.sha256(verifier.encode("ascii")).digest()
        code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "nonce": nonce,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "prompt": "select_account",
        }
        return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    async def exchange_code(
        self, *, code: str, expected_nonce: str, code_verifier: str
    ) -> VerifiedIdentity:
        """Exchange one-time code for tokens and verify the ID token."""
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uri": self.redirect_uri,
                    "grant_type": "authorization_code",
                    "code_verifier": code_verifier,
                },
            )
            if response.status_code != 200:
                raise GoogleOAuthError(
                    "GOOGLE_EXCHANGE_FAILED", f"Status code: {response.status_code}"
                )

            payload = response.json()
            raw_id_token = payload.get("id_token")
            if not raw_id_token or not isinstance(raw_id_token, str):
                raise GoogleOAuthError("GOOGLE_INVALID_TOKEN_RESPONSE")

        try:
            claims = await run_in_threadpool(
                id_token.verify_oauth2_token,
                raw_id_token,
                GoogleRequest(),
                self.client_id,
            )
            sub = claims.get("sub")
            email = claims.get("email")
            email_verified = claims.get("email_verified") in (True, "true")
            actual_nonce = claims.get("nonce")

            if not sub or not email or not email_verified:
                raise GoogleOAuthError("GOOGLE_UNVERIFIED_EMAIL")

            if not actual_nonce or not secrets.compare_digest(
                actual_nonce, expected_nonce
            ):
                raise GoogleOAuthError("GOOGLE_NONCE_MISMATCH")

            name = claims.get("name")
            return VerifiedIdentity(
                subject=sub,
                email=email.strip().lower(),
                name=name.strip() if name else None,
            )
        except Exception as exc:
            if isinstance(exc, GoogleOAuthError):
                raise
            raise GoogleOAuthError("GOOGLE_VALIDATION_FAILED", str(exc)) from exc
