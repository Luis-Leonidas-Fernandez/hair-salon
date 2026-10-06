"""Provider-independent contracts for verified external identities.

Following Dependency Inversion Principle (DIP) and Interface Segregation (ISP):
The domain use cases depend on this port, not on concrete provider SDKs.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class VerifiedIdentity:
    """Identity claims accepted after cryptographic provider verification."""

    subject: str
    email: str
    name: str | None


class IdentityProvider(Protocol):
    """Protocol for external OpenID Connect identity providers."""

    def build_authorization_url(self, *, state: str, nonce: str, verifier: str) -> str:
        """Construct the provider's authorization URL with PKCE and state."""
        ...

    async def exchange_code(
        self, *, code: str, expected_nonce: str, code_verifier: str
    ) -> VerifiedIdentity:
        """Exchange authorization code and cryptographically validate the ID token."""
        ...
